#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2005-2009 University of Deusto
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#
# This software consists of contributions made by many individuals, 
# listed below:
#
# Author: Jaime Irurzun <jaime.irurzun@gmail.com>
#
 
import os
import tempfile
import subprocess
import threading

import voodoo.log as log
from voodoo.log import logged

import voodoo.exceptions.configuration.ConfigurationExceptions as ConfigurationExceptions
import weblab.exceptions.experiment.devices.digilent_adept.DigilentAdeptExceptions as DigilentAdeptExceptions

# Quick help for debugging:
#digilentmofas = open("/tmp/digilentmofas", 'w+')
#def printar(msg):
#   digilentmofas.write(str(msg)+"\n")
#   digilentmofas.flush()

class DigilentAdept(object):

    def __init__(self, cfg_manager):
        super(DigilentAdept,self).__init__()
        self._cfg_manager= cfg_manager
        self._lock = threading.Lock()
        self._busy = False
    
    def _reserve_device(self):
        self._lock.acquire()
        try:
            if self._busy:
                # TODO check if it's really busy
                # Refactor this code so that it has "simple sessions"
                # so that if the program is finished, it starts programming the next device
                # Consider that this might happen with any device, so 
                # DigilentAdept might be a subclass of Experiment or sth
                raise DigilentAdeptExceptions.AlreadyProgrammingDeviceException(
                    "This experiment is already programming the device"
                )
            self._busy = True
        finally:
            self._lock.release()

    def _release_device(self):
        self._lock.acquire()
        self._busy = False
        self._lock.release()

    @logged()
    def program_device(self, program_path):
        file_content, digilent_adept = self._parse_configuration_to_program()

        cmd_params = file_content.replace('$FILE',program_path)
        self._reserve_device()
        try:
            res, out, err = self._execute(cmd_params, digilent_adept)
        finally:
            self._release_device()

        self._log(res,out,err)

        # TODO: this could be improved :-D
        if out.find("ERROR") >= 0:
            error_messages = [ i for i in out.split('\n') if i.find('ERROR') >= 0 ] 
            error_messages += '; ' + err
            raise DigilentAdeptExceptions.ProgrammingGotErrors(
                    "Digilent Adept raised errors while programming the device: %s" % error_messages
                )
        if res != 0:
            raise DigilentAdeptExceptions.ProgrammingGotErrors(
                    "Digilent Adept returned %i" % res
                )

    def _execute(self, cmd_params, digilent_adept):
        # Kludge!
        full_cmd_line = digilent_adept + cmd_params.split(" ")
        
        try:
            popen = subprocess.Popen(
                full_cmd_line,
                stdin  = subprocess.PIPE,
                stdout = subprocess.PIPE,
                stderr = subprocess.PIPE
            )
        except Exception, e:
            raise DigilentAdeptExceptions.ErrorProgrammingDeviceException(
                "There was an error while executing Digilent Adept: %s" % e
            )
        # TODO: make use of popen.poll to make this asynchronous
        try:
            result = popen.wait()
        except Exception, e:
            raise DigilentAdeptExceptions.ErrorWaitingForProgrammingFinishedException(
                "There was an error while waiting for Digilent Adept to finish: %s" % e
            )

        try:
            stdout_result = popen.stdout.read()
            stderr_result = popen.stderr.read()
        except Exception, e:
            raise DigilentAdeptExceptions.ErrorRetrievingOutputFromProgrammingProgramException(
                "There was an error while retrieving the output of Digilent Adept: %s" % e
            )
        return result, stdout_result, stderr_result

    def _parse_configuration_to_program(self):
        try:
            program_file_content = self._cfg_manager.get_value('digilent_adept_batch_content')
            digilent_adept = self._cfg_manager.get_value('digilent_adept_full_path')
        except ConfigurationExceptions.KeyNotFoundException,knfe:
            raise DigilentAdeptExceptions.CantFindDigilentAdeptProperty(
                    "Can't find in configuration manager the property '%s'" % knfe.key
                )
        return program_file_content, digilent_adept

    def _create_batch_file(self, content, program_path):
        fd, file_name = tempfile.mkstemp(prefix='digilent_adept_batch_file_',suffix='.cmd')
        os.write(fd, content.replace('$FILE',program_path))
        os.close(fd)
        return file_name
    
    def _log(self, result_code, output, stderr):
        log.log(DigilentAdept,log.LogLevel.Info,"Device programming was finished. Result code: %i\n<output>\n%s\n</output><stderr>\n%s\n</stderr>" % (
                result_code,
                output,
                stderr
            )
        )
