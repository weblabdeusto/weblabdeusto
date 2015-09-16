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
# Author: Luis Rodriguez-Gil <luis.rodriguezgil@deusto.es>
#
from __future__ import print_function, unicode_literals

import subprocess
import threading

import voodoo.log as log
from voodoo.log import logged
import voodoo.configuration as ConfigurationErrors
import weblab.experiment.devices.exc as DeviceErrors


DEBUG = True


def debug(msg):
    if DEBUG:
        print(msg)


class Xcs3prog(object):
    """
    Wrapper around the XCS3Prog command line tool to program .BIT files into FPGA files.
    """

    def __init__(self, cfg_manager):
        super(Xcs3prog, self).__init__()
        self._cfg_manager = cfg_manager
        self._lock = threading.Lock()
        self._busy = False

        # Should be in the config. It is parsed in every program_device call.
        self._xc3sprog_full_path = None  # Full path to the tool
        self._xc3sprog_batch_content = None  # Batch parameters that will be passed for the current device (FPGA / PLD...?)

    def _reserve_device(self):
        self._lock.acquire()
        try:
            if self._busy:
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
    def program_device(self, program_path, xilinx_board_type):
        # TODO: Maybe this shouldn't be hard-coded.
        self._parse_configuration_to_program(xilinx_board_type)

        # The batch content should have a $FILE template so that we can replace it.
        cmd_params = self._xc3sprog_batch_content.replace('$FILE', program_path)
        self._reserve_device()
        try:
            res, out, err = self._execute(cmd_params, self._xc3sprog_full_path)
            debug('%s %s %s' % (res, out, err))
        finally:
            self._release_device()

        self._log(res, out, err)

        if out.upper().find("ERROR") >= 0:
            error_messages = [i for i in out.split('\n') if i.find('Error') >= 0]
            error_messages += '; ' + err
            raise ProgrammingGotErrors(
                "xcs3prog FPGA programmer tool raised errors while programming the device: %s" % error_messages
            )
        if res != 0:
            raise ProgrammingGotErrors(
                "xcs3prog FPGA programmer tool returned %i" % res
            )

    def _execute(self, cmd_params, xcs3prog_full_path):
        """
        Runs the actual process with the given command line arguments and full path.
        :param cmd_params:
        :param xcs3prog_full_path:
        :return:
        """

        full_cmd_line = xcs3prog_full_path + cmd_params.split(" ")

        log.log(Xcs3prog, log.level.Warning, "Executing %s" % full_cmd_line)

        try:
            popen = subprocess.Popen(
                full_cmd_line,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        except Exception as e:
            raise ErrorProgrammingDeviceError(
                "There was an error while executing xcs3prog FPGA programming tool: %s" % e
            )

        try:
            stdout, stderr = popen.communicate('N\n')
            result = popen.wait()
        except Exception as e:
            raise ErrorWaitingForProgrammingFinishedError(
                "There was an error while waiting for xcs3prog FPGA programming tool to finish: %s" % e
            )

        return result, stdout, stderr

    def _parse_configuration_to_program(self, xilinx_board_type):
        """
        Reads the relevant Experiment configuration.
        Variables required:
          'xc3sprog_full_path'
          'xc3sprog_batch_content_<device>'

        :param device: The actual device name. For instance, FPGA or PLD. The actual batch content will depend upon it.
        """
        try:
            # TODO: RENAME XC3S TO XCS3 OR THE OTHER WAY ROUND
            self._xc3sprog_full_path = self._cfg_manager.get_value('xc3sprog_full_path')
            self._xc3sprog_batch_content = self._cfg_manager.get_value('xc3sprog_batch_content_' + xilinx_board_type)
        except ConfigurationErrors.KeyNotFoundError as knfe:
            raise CantFindXc3sprogProperty(
                "Can't find in configuration manager the property '%s'" % knfe.key
            )

    # def _create_batch_file(self, content, program_path):
    #     fd, file_name = tempfile.mkstemp(prefix='digilent_adept_batch_file_', suffix='.cmd')
    #     os.write(fd, content.replace('$FILE', program_path))
    #     os.close(fd)
    #     return file_name

    def _log(self, result_code, output, stderr):
        log.log(Xcs3prog, log.level.Info,
                "Device programming was finished. Result code: %i\n<output>\n%s\n</output><stderr>\n%s\n</stderr>" % (
                    result_code,
                    output,
                    stderr
                )
                )


class CantFindXc3sprogProperty(DeviceErrors.MisconfiguredDeviceError):
    def __init__(self, *args, **kargs):
        DeviceErrors.MisconfiguredDeviceError.__init__(self, *args, **kargs)


class AlreadyProgrammingDeviceError(DeviceErrors.AlreadyProgrammingDeviceError):
    def __init__(self, *args, **kargs):
        DeviceErrors.AlreadyProgrammingDeviceError.__init__(self, *args, **kargs)


class ErrorProgrammingDeviceError(DeviceErrors.ProgrammingDeviceError):
    def __init__(self, *args, **kargs):
        DeviceErrors.ProgrammingDeviceError.__init__(self, *args, **kargs)


class ErrorRetrievingOutputFromProgrammingProgramError(DeviceErrors.ProgrammingDeviceError):
    def __init__(self, *args, **kargs):
        DeviceErrors.ProgrammingDeviceError.__init__(self, *args, **kargs)


class ErrorWaitingForProgrammingFinishedError(DeviceErrors.ProgrammingDeviceError):
    def __init__(self, *args, **kargs):
        DeviceErrors.ProgrammingDeviceError.__init__(self, *args, **kargs)


class ProgrammingGotErrors(DeviceErrors.ProgrammingDeviceError):
    def __init__(self, *args, **kargs):
        DeviceErrors.ProgrammingDeviceError.__init__(self, *args, **kargs)
