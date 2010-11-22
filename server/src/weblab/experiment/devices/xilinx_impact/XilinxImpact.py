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
# Author: Pablo Orduña <pablo@ordunya.com>
#         Jaime Irurzun <jaime.irurzun@gmail.com>
# 

from voodoo.log import logged
import os
import subprocess
import tempfile
import threading
import voodoo.exceptions.configuration.ConfigurationExceptions as ConfigurationExceptions
import voodoo.log as log
import weblab.exceptions.experiment.devices.xilinx_impact.XilinxImpactExceptions as XilinxImpactExceptions
import weblab.experiment.devices.xilinx_impact.XilinxDevices as XilinxDevices


def create(xilinx_device, cfg_manager):
    if not XilinxDevices.isXilinxDevices(xilinx_device):
        raise XilinxImpactExceptions.NotAXilinxDeviceEnumException(
                "Not a Xilinx Device Enumeration: %s" % xilinx_device
            )
    if xilinx_device == XilinxDevices.FPGA:
        return _XilinxImpactFPGA(cfg_manager)
    elif xilinx_device == XilinxDevices.PLD:
        return _XilinxImpactPLD(cfg_manager)
    else:
        raise XilinxImpactExceptions.XilinxDeviceNotFoundException(
                "Couldn't find xilinx device gateway: %s" % xilinx_device.name
            )


class XilinxImpact(object):
    def __init__(self, cfg_manager):
        super(XilinxImpact,self).__init__()
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
                raise XilinxImpactExceptions.AlreadyProgrammingDeviceException(
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
    def program_device(self, program_path, device):
        file_content, xilinx_impact = self._parse_configuration_to_program(device)

        cmd_file_name = self._create_batch_file(file_content,program_path)
        try:
            self._reserve_device()
            try:
                res, out, err = self._execute(cmd_file_name, xilinx_impact)
            finally:
                self._release_device()
        finally:
            os.remove(cmd_file_name)

        self._log(res,out,err)

        # TODO: this could be improved :-D
        if out.find("ERROR") >= 0 or len(err) > 0:
            error_messages = [ i for i in out.split('\n') if i.find('ERROR') >= 0 ] 
            error_messages += '; ' + err
            raise XilinxImpactExceptions.ProgrammingGotErrors(
                    "Impact raised errors while programming the device: %s" % error_messages
                )
        if res != 0:
            raise XilinxImpactExceptions.ProgrammingGotErrors(
                    "Impact returned %i" % res
                )

    @logged()
    def source2svf(self, source_file_full_name, device):
        file_content, xilinx_impact = self._parse_configuration_to_source2svf(device)
        
        cmd_file_name = self._create_source2svf_batch_file(file_content, source_file_full_name)
        try:
            res, out, err = self._execute(cmd_file_name, xilinx_impact)
        finally:
            os.remove(cmd_file_name)

        self._log(res,out,err)

        # TODO: this could be improved :-D
	# Kludge!
        if device == XilinxDevices.PLD:
	        if out.find("ERROR") >= 0:
        	    error_messages = [ i for i in out.split('\n') if i.find('ERROR') >= 0 ] 
	            error_messages += '; ' + err
	            raise XilinxImpactExceptions.GeneratingSvfFileGotErrors(
	                    "Impact raised errors while generating the .SVF file: %s" % error_messages
	                )
	        if res != 0:
	            raise XilinxImpactExceptions.GeneratingSvfFileGotErrors(
	                    "Impact returned %i" % res
	                ) 
	else:
		if out.find("ERROR") >= 0:
       	            error_messages = [ i for i in out.split('\n') if i.find('ERROR') >= 0 ]
               	    error_messages += '; ' + err
                    raise XilinxImpactExceptions.GeneratingSvfFileGotErrors(
                            "Impact raised errors while generating the .SVF file: %s" % error_messages
                        )
                if res != 0:
                    raise XilinxImpactExceptions.GeneratingSvfFileGotErrors(
                            "Impact returned %i" % res
                        )
       

    
    def _execute(self, cmd_file_name, xilinx_impact):
        full_cmd_line = xilinx_impact + ['-batch',cmd_file_name]

        try:
            popen = subprocess.Popen(
                full_cmd_line,
                stdin  = subprocess.PIPE,
                stdout = subprocess.PIPE,
                stderr = subprocess.PIPE
            )
        except Exception, e:
            raise XilinxImpactExceptions.ErrorProgrammingDeviceException(
                "There was an error while executing Xilinx Impact: %s" % e
            )
        # TODO: make use of popen.poll to make this asynchronous
        try:
            result = popen.wait()
        except Exception, e:
            raise XilinxImpactExceptions.ErrorWaitingForProgrammingFinishedException(
                "There was an error while waiting for Xilinx Impact to finish: %s" % e
            )

        try:
            stdout_result = popen.stdout.read()
            stderr_result = popen.stderr.read()
        except Exception, e:
            raise XilinxImpactExceptions.ErrorRetrievingOutputFromProgrammingProgramException(
                "There was an error while retrieving the output of Xilinx Impact: %s" % e
            )
        return result, stdout_result, stderr_result

    def _parse_configuration_to_program(self, device):
        try:
            program_file_content = self._cfg_manager.get_value('xilinx_batch_content_' + device.name)
            xilinx_impact = self._cfg_manager.get_value('xilinx_impact_full_path')
        except ConfigurationExceptions.KeyNotFoundException,knfe:
            raise XilinxImpactExceptions.CantFindXilinxProperty(
                    "Can't find in configuration manager the property '%s'" % knfe.key
                )
        return program_file_content, xilinx_impact

    def _parse_configuration_to_source2svf(self, device):
        try:
            svf2jsvf_file_content = self._cfg_manager.get_value('xilinx_source2svf_batch_content_' + device.name)
            xilinx_impact = self._cfg_manager.get_value('xilinx_impact_full_path')
        except ConfigurationExceptions.KeyNotFoundException,knfe:
            raise XilinxImpactExceptions.CantFindXilinxProperty(
                    "Can't find in configuration manager the property '%s'" % knfe.key
                )
        return svf2jsvf_file_content, xilinx_impact

    def _create_batch_file(self, content, program_path):
        fd, file_name = tempfile.mkstemp(prefix='xilinx_batch_file_',suffix='.cmd')
        os.write(fd, content.replace('$FILE',program_path))
        os.close(fd)
        return file_name
    
    def _create_source2svf_batch_file(self, content, source_file_full_name):
        fd, file_name = tempfile.mkstemp(prefix='xilinx_source2svf_batch_file_',suffix='.cmd')
        os.write(fd, content.replace('$SOURCE_FILE', source_file_full_name).replace('$SVF_FILE', source_file_full_name.replace('.'+self.get_suffix(), '.svf')))
        os.close(fd)
        return file_name    

    def _log(self, result_code, output, stderr):
        log.log(XilinxImpact,log.LogLevel.Info,"Device programming was finished. Result code: %i\n<output>\n%s\n</output><stderr>\n%s\n</stderr>" % (
                result_code,
                output,
                stderr
            )
        )
    def get_suffix(self):
        return 'file.extension.retrieved.by.xilinx.impact.implementor'

class XilinxImpactPLD(XilinxImpact):
    def __init__(self, *args, **kargs):
        super(XilinxImpactPLD,self).__init__(*args, **kargs)
    def program_device(self, program):
        return super(XilinxImpactPLD,self).program_device( program, XilinxDevices.PLD)
    def source2svf(self, program):
        return super(XilinxImpactPLD,self).source2svf( program, XilinxDevices.PLD)
    def get_suffix(self):
        return 'jed'

class XilinxImpactFPGA(XilinxImpact):
    def __init__(self, *args, **kargs):
        super(XilinxImpactFPGA,self).__init__(*args, **kargs)
    def program_device(self, program):
        return super(XilinxImpactFPGA,self).program_device( program, XilinxDevices.FPGA)
    def source2svf(self, program):
        return super(XilinxImpactFPGA,self).source2svf( program, XilinxDevices.FPGA)
    def get_suffix(self):
        return 'bit'
    

_XilinxImpactFPGA = XilinxImpactFPGA
_XilinxImpactPLD = XilinxImpactPLD