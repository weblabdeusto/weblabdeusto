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
# Author: Pablo Orduña <pablo@ordunya.com>
# 
from __future__ import print_function, unicode_literals

import voodoo.log as log
from voodoo.log import logged

import voodoo.configuration as ConfigurationErrors
import weblab.experiment.devices.gpib.exc as GpibErrors

import subprocess
import os
import time

CPP_FILE = '$CPP_FILE'
OBJ_FILE = '$OBJ_FILE'
EXE_FILE = '$EXE_FILE'

class Launcher(object):
    
    _time = time
    
    def __init__(self, cfg_manager):
        super(Launcher, self).__init__()
        self._cfg_manager = cfg_manager
        self.popen = None

    def _create_popen(self, cmd_file):
        return subprocess.Popen(
                cmd_file,
                stdin  = subprocess.PIPE,
                stdout = subprocess.PIPE,
                stderr = subprocess.PIPE
            )
            
    @logged()
    def execute(self, file_path, background):
        try:
            self.popen = self._create_popen(file_path)
        except Exception as e:
            raise GpibErrors.ErrorProgrammingDeviceError(
                "There was an error while compiling the device: %s" % e # TODO: "compiling"
            )
        if not background:
            result_code = self._wait_for_results()
            self._save_results()
            return result_code, self.result_stdout, self.result_stderr
        return None

    def _wait_for_results(self):
        try:
            MAX_TIME = 15
            initial_time = time.time()
            result = None
            while result is None and ((initial_time + MAX_TIME) > time.time()):
                result = self.popen.poll()
                if result is None:
                    self._time.sleep(0.1)
            if result is None:
                raise Exception("Program took too much time to run")
            return result
        except Exception as e:
            raise GpibErrors.ErrorWaitingForProgrammingFinishedError(
                "There was an error while waiting for the compiler to finish: %s" % e
            )

    def _save_results(self):
        try:
            self.result_stdout = self.popen.stdout.read()
            self.result_stderr = self.popen.stderr.read()
        except Exception as e:
            raise GpibErrors.ErrorRetrievingOutputFromProgrammingProgramError(
                "There was an error while retrieving the output of the compiler: %s" % e
            )

    def poll(self):
        try:
            self.result_code = self.popen.poll()
        except Exception as e:
            raise GpibErrors.ErrorWaitingForProgrammingFinishedError(
                "There was an error while waiting for the compiler to finish: %s" % e
            )
    
        if self.result_code is not None:
            self._save_results()
            return True
        else:
            return False
                    
    def get_result_code(self):
        return self.result_code
    
    def get_result_stdout(self):
        return self.result_stdout

    def get_result_stderr(self):
        return self.result_stderr


class Compiler(Launcher):
    
    def __init__(self, cfg_manager):
        super(Compiler, self).__init__(cfg_manager)

    @logged()
    def compile_file(self, file_path):
        self._check(file_path)

        file_name_base = file_path[:-4]

        compiler_command, linker_command = self._parse_configuration()

        self._set_up_command(file_name_base, CPP_FILE, '.cpp', compiler_command)
        self._set_up_command(file_name_base, OBJ_FILE, '.obj', linker_command)
        self._set_up_command(file_name_base, EXE_FILE, '.exe', linker_command)

        self._execute_and_check_errors(compiler_command, 'compiling')
        self._execute_and_check_errors(linker_command,   'linking')

        obj_file = file_path[:-4] + '.obj'
        if os.path.exists(obj_file):
            os.remove(obj_file)

        return file_name_base + '.exe'

    def _set_up_command(self, file_name_base, name, ext, command):
        command_strs = [ i for i in command if i.find(name) >= 0 ]
        if len(command_strs) == 1:
            index = command.index(command_strs[0])
            s = command[index]
            command[index] = s.replace(name,file_name_base + ext)
        else:
            raise GpibErrors.InvalidGpibProperty("Experiment misconfigured: no %s found on %s" % (
                    name,
                    command
                )
            )

    def _execute_and_check_errors(self, command, action):
        res, out, err = self.execute(command, False)
        self._log(action, res, out, err)

        if out.find('ERROR') >= 0: #or len(err) > 0:
            errors = 'stdout: <%s>' % '; '.join([ i for i in out.split('\n') if i.find('ERROR') >= 0])
            errors += '; stderr: <%s>' % err
            raise GpibErrors.ProgrammingGotErrors(
                    "Errors raised while %s the file: %s" % (action, errors)
                )
        if res != 0:
            raise GpibErrors.ProgrammingGotErrors(
                    "%s tool returned %s" % (action, res)
                )

    def _log(self, action, result_code, output, stderr):
        log.log(Compiler,log.level.Info,"%s was finished. Result code: %i\n<output>\n%s\n</output><stderr>\n%s\n</stderr>" % (
                action,
                result_code,
                output,
                stderr
            )
        )

    def _parse_configuration(self):
        try:
            compiler_command = list(self._cfg_manager.get_value('gpib_compiler_command'))
            linker_command   = list(self._cfg_manager.get_value('gpib_linker_command'))
        except ConfigurationErrors.KeyNotFoundError as knfe:
            raise GpibErrors.CantFindGpibProperty(
                    "Can't find in configuration manager the property '%s'" % knfe.key
                )
        else:
            return compiler_command, linker_command

    def _log_line(self, level, msg, line):
        log.log(Compiler,level, "%s::%s" % (msg, line))

    def _check(self, file_path):
        # TODO: security checkings should be performed here
        # TODO: to be tested
        file_content = open(file_path).read()
        bad_content = [ i for i in file_content.split('\n') if i.find('\tscanf') >= 0 or i.find('scanf') == 0 or i.find('getchar') >= 0]
        if len(bad_content) > 0:
            raise GpibErrors.ProgrammingGotErrors('Invalid commands found: %s' % (bad_content))

