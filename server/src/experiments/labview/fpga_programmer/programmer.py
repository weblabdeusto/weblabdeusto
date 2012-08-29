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

import base64
import tempfile
import traceback
import SimpleXMLRPCServer

import sys, os
sys.path.append(os.sep.join(('..','..','..','..','..')))

import voodoo.configuration as CM
import weblab.experiment.devices.xilinx_impact.devices as XilinxDevices
import weblab.experiment.devices.xilinx_impact.impact  as XilinxImpact

class FpgaProgrammer(object):
    def program(self, serialized_content):
        print "File received"
        content = base64.decodestring(serialized_content)

        fd, file_name = tempfile.mkstemp(prefix='weblab_fpga_program', suffix='.bit')
        try:
            os.write(fd, content)
            os.close(fd)

            print "Programming... %s" % file_name
            impact.program_device(file_name)

            print "Programmed successfully"
            return "ok"
        except:
            traceback.print_exc()
            raise
        finally:
            os.remove(file_name)

if __name__ == '__main__':
    cfg_manager = CM.ConfigurationManager()
    cfg_manager.append_path("config.py")
    impact = XilinxImpact.create(XilinxDevices.FPGA, cfg_manager)

    server = SimpleXMLRPCServer.SimpleXMLRPCServer(('', cfg_manager.get_value("port")))
    server.register_instance(FpgaProgrammer())
    server.serve_forever()
