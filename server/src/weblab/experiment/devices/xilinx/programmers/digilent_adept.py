#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2005 onwards University of Deusto
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
from __future__ import print_function, unicode_literals
 
import os
import tempfile
import subprocess
import threading

import voodoo.log as log
from voodoo.log import logged

import voodoo.configuration as ConfigurationErrors
import weblab.experiment.devices.exc as DeviceErrors

# Quick help for debugging:
#digilentmofas = open("/tmp/digilentmofas", 'w+')
#def printar(msg):
#   digilentmofas.write(str(msg)+"\n")
#   digilentmofas.flush()

DEBUG = True

def debug(msg):
    if DEBUG:
        print(msg)

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
                raise AlreadyProgrammingDeviceError(
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
            debug('%s %s %s' % (res, out, err))
        finally:
            self._release_device()

        self._log(res, out, err)

        # TODO: this could be improved :-D
        if out.find("ERROR") >= 0:
            error_messages = [ i for i in out.split('\n') if i.find('ERROR') >= 0 ] 
            error_messages += '; ' + err
            raise ProgrammingGotErrors(
                    "Digilent Adept raised errors while programming the device: %s" % error_messages
                )
        if res != 0:
            raise ProgrammingGotErrors(
                    "Digilent Adept returned %i" % res
                )

    def _execute(self, cmd_params, digilent_adept):
        # Kludge!
        full_cmd_line = digilent_adept + cmd_params.split(" ")

        log.log(DigilentAdept,log.level.Warning,"Executing %s" % full_cmd_line)

        try:
            popen = subprocess.Popen(
                full_cmd_line,
                stdin  = subprocess.PIPE,
                stdout = subprocess.PIPE,
                stderr = subprocess.PIPE
            )
        except Exception as e:
            raise ErrorProgrammingDeviceError(
                "There was an error while executing Digilent Adept: %s" % e
            )
        # TODO: make use of popen.poll to make this asynchronous
        try:
            stdout, stderr = popen.communicate('N\n')
            result = popen.wait()
        except Exception as e:
            raise ErrorWaitingForProgrammingFinishedError(
                "There was an error while waiting for Digilent Adept to finish: %s" % e
            )

        return result, stdout, stderr

    def _parse_configuration_to_program(self):
        try:
            program_file_content = self._cfg_manager.get_value('digilent_adept_batch_content')
            digilent_adept = self._cfg_manager.get_value('digilent_adept_full_path')
        except ConfigurationErrors.KeyNotFoundError as knfe:
            raise CantFindDigilentAdeptProperty(
                    "Can't find in configuration manager the property '%s'" % knfe.key
                )
        return program_file_content, digilent_adept

    def _create_batch_file(self, content, program_path):
        fd, file_name = tempfile.mkstemp(prefix='digilent_adept_batch_file_',suffix='.cmd')
        os.write(fd, content.replace('$FILE',program_path))
        os.close(fd)
        return file_name
    
    def _log(self, result_code, output, stderr):
        log.log(DigilentAdept,log.level.Info,"Device programming was finished. Result code: %i\n<output>\n%s\n</output><stderr>\n%s\n</stderr>" % (
                result_code,
                output,
                stderr
            )
        )


class CantFindDigilentAdeptProperty(DeviceErrors.MisconfiguredDeviceError):
    def __init__(self, *args, **kargs):
        DeviceErrors.MisconfiguredDeviceError.__init__(self, *args, **kargs)

class AlreadyProgrammingDeviceError(DeviceErrors.AlreadyProgrammingDeviceError):
    def __init__(self, *args, **kargs):
        DeviceErrors.AlreadyProgrammingDeviceError.__init__(self, *args, **kargs)

class ErrorProgrammingDeviceError(DeviceErrors.ProgrammingDeviceError):
    def __init__(self,*args,**kargs):
        DeviceErrors.ProgrammingDeviceError.__init__(self,*args,**kargs)

class ErrorRetrievingOutputFromProgrammingProgramError(DeviceErrors.ProgrammingDeviceError):
    def __init__(self,*args,**kargs):
        DeviceErrors.ProgrammingDeviceError.__init__(self,*args,**kargs)

class ErrorWaitingForProgrammingFinishedError(DeviceErrors.ProgrammingDeviceError):
    def __init__(self,*args,**kargs):
        DeviceErrors.ProgrammingDeviceError.__init__(self,*args,**kargs)

class ProgrammingGotErrors(DeviceErrors.ProgrammingDeviceError):
    def __init__(self,*args,**kargs):
        DeviceErrors.ProgrammingDeviceError.__init__(self,*args,**kargs)
