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
#         Jaime Irurzun <jaime.irurzun@gmail.com>
# 
from __future__ import print_function, unicode_literals

import os
import subprocess
import threading

import voodoo.log as log
from voodoo.log import logged

import voodoo.configuration as ConfigurationErrors
import weblab.experiment.devices.exc as DeviceErrors


class JTagBlazer(object):
    
    def __init__(self, cfg_manager):
        super(JTagBlazer,self).__init__()
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
                # XilinxImpact might be a subclass of Experiment or sth
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
        
    def _svf_to_jsvf(self, svf_file_name):    
        jbmanager_svf2jsvf_path = self._get_property('xilinx_jtag_blazer_jbmanager_svf2jsvf_full_path')
          
        # 1st step: .svf -> .jsvf
        jsvf_file_name = svf_file_name.replace(".svf", ".jsvf")
        try:
            full_cmd_line = jbmanager_svf2jsvf_path + ['-o', jsvf_file_name, svf_file_name]
            try:
                popen = subprocess.Popen(
                    full_cmd_line,
                    stdin  = subprocess.PIPE,
                    stdout = subprocess.PIPE,
                    stderr = subprocess.PIPE
                )
            except Exception as e:
                raise ErrorProgrammingDeviceError(
                    "There was an error generating the JSVF file: %s" % e
                )
            # TODO: make use of popen.poll to make this asynchronous
            try:
                result = popen.wait()
            except Exception as e:
                raise ErrorWaitingForJTagBlazerSvf2JsvfFinishedError(
                    "There was an error while waiting for JBManager to generate the JSVF file: %s" % e
                )    
            try:
                stdout_result = popen.stdout.read()
                stderr_result = popen.stderr.read()
            except Exception as e:
                raise ErrorRetrievingOutputFromJTagBlazerSvf2JsvfError(
                    "There was an error while retrieving the output of the JSVF file generator program: %s" % e
                )
        finally:
            try:
                os.remove(svf_file_name)
            except OSError:
                pass
            
        log.log(JTagBlazer, log.level.Info, "JSVF file generated. Result code: %i\n<output>\n%s\n</output><stderr>\n%s\n</stderr>" % (
                result,
                stdout_result,
                stderr_result
            )
        )        
        
        # TODO: this could be improved :-D
        if stdout_result.find("ERROR") >= 0 or len(stderr_result) > 0:
            error_messages = [ i for i in stdout_result.split('\n') if i.find('ERROR') >= 0 ] 
            error_messages += '; ' + stderr_result
            raise JTagBlazerSvf2JsvfErrorError(
                    "JTagBlazer svf2jsvf raised errors while generating the JSVF file: %s" % error_messages
                )
        if result != 0:
            raise JTagBlazerSvf2JsvfErrorError(
                    "JTagBlazer svf2jsvf returned %i" % result
                )         
        
        return jsvf_file_name
        
    def _program(self, device_ip, jsvf_file_name):
        jbmanager_target_path = self._get_property('xilinx_jtag_blazer_jbmanager_target_full_path')
        
        # 2nd step: Program the device
        try:
            self._reserve_device()
            try:
                full_cmd_line = jbmanager_target_path + [device_ip, jsvf_file_name]
                try:
                    popen = subprocess.Popen(
                        full_cmd_line,
                        stdin  = subprocess.PIPE,
                        stdout = subprocess.PIPE,
                        stderr = subprocess.PIPE
                    )
                except Exception as e:
                    raise ErrorProgrammingDeviceError(
                        "There was an error while programming the device: %s" % e
                    )
                # TODO: make use of popen.poll to make this asynchronous
                try:
                    result = popen.wait()
                except Exception as e:
                    raise ErrorWaitingForJTagBlazerTargetFinishedError(
                        "There was an error while waiting for the programming program to finish: %s" % e
                    )    
                try:
                    stdout_result = popen.stdout.read()
                    stderr_result = popen.stderr.read()
                except Exception as e:
                    raise ErrorRetrievingOutputFromJTagBlazerTargetError(
                        "There was an error while retrieving the output of the programming program: %s" % e
                    )
            finally:
                self._release_device()
        finally:
            try:
                os.remove(jsvf_file_name)
            except OSError:
                pass

        log.log(JTagBlazer, log.level.Info, "Device programming was finished. Result code: %i\n<output>\n%s\n</output><stderr>\n%s\n</stderr>" % (
                result,
                stdout_result,
                stderr_result
            )
        )   
        
        # TODO: this could be improved :-D
        if stdout_result.find("ERROR") >= 0 or len(stderr_result) > 0:
            error_messages = [ i for i in stdout_result.split('\n') if i.find('ERROR') >= 0 ] 
            error_messages += '; ' + stderr_result
            raise JTagBlazerTargetErrorError(
                    "JTagBlazer target raised errors while programming the device: %s" % error_messages
                )
        if result != 0:
            raise JTagBlazerTargetErrorError(
                    "JTagBlazer target returned %i" % result
                ) 
        
    @logged()
    def program_device(self, svf_file_name, device_ip):
        if svf_file_name[-4:] != ".svf":
            raise InvalidSvfFileExtError("Invalid file extension: %s" % svf_file_name)
        
        jsvf_file_name = self._svf_to_jsvf(svf_file_name)
        self._program(device_ip, jsvf_file_name)

    def _get_property(self, property):
        try:
            value = self._cfg_manager.get_value(property)
        except ConfigurationErrors.KeyNotFoundError as knfe:
            raise CantFindJTagBlazerProperty(
                    "Can't find in configuration manager the property '%s'" % knfe.key
                )
        return value


class CantFindJTagBlazerProperty(DeviceErrors.MisconfiguredDeviceError):
    def __init__(self, *args, **kargs):
        DeviceErrors.MisconfiguredDeviceError.__init__(self, *args, **kargs)

class AlreadyProgrammingDeviceError(DeviceErrors.AlreadyProgrammingDeviceError):
    def __init__(self, *args, **kargs):
        DeviceErrors.AlreadyProgrammingDeviceError.__init__(self, *args, **kargs)
        
class ErrorProgrammingDeviceError(DeviceErrors.ProgrammingDeviceError):
    def __init__(self,*args,**kargs):
        DeviceErrors.ProgrammingDeviceError.__init__(self,*args,**kargs)        
        
class JTagBlazerSvf2JsvfErrorError(DeviceErrors.ProgrammingDeviceError):
    def __init__(self,*args,**kargs):
        DeviceErrors.ProgrammingDeviceError.__init__(self,*args,**kargs)

class ErrorRetrievingOutputFromJTagBlazerSvf2JsvfError(DeviceErrors.ProgrammingDeviceError):
    def __init__(self,*args,**kargs):
        DeviceErrors.ProgrammingDeviceError.__init__(self,*args,**kargs)

class ErrorWaitingForJTagBlazerSvf2JsvfFinishedError(DeviceErrors.ProgrammingDeviceError):
    def __init__(self,*args,**kargs):
        DeviceErrors.ProgrammingDeviceError.__init__(self,*args,**kargs)

class JTagBlazerTargetErrorError(DeviceErrors.ProgrammingDeviceError):
    def __init__(self,*args,**kargs):
        DeviceErrors.ProgrammingDeviceError.__init__(self,*args,**kargs)

class ErrorRetrievingOutputFromJTagBlazerTargetError(DeviceErrors.ProgrammingDeviceError):
    def __init__(self,*args,**kargs):
        DeviceErrors.ProgrammingDeviceError.__init__(self,*args,**kargs)

class ErrorWaitingForJTagBlazerTargetFinishedError(DeviceErrors.ProgrammingDeviceError):
    def __init__(self,*args,**kargs):
        DeviceErrors.ProgrammingDeviceError.__init__(self,*args,**kargs)

class InvalidSvfFileExtError(DeviceErrors.DeviceError):
    def __init__(self, *args, **kargs):
        DeviceErrors.DeviceError.__init__(self, *args, **kargs)
