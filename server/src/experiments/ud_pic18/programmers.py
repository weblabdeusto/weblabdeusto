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

from abc import ABCMeta, abstractmethod
from voodoo.override import Override

import subprocess        

class UdXilinxProgrammer(object):

    __metaclass__ = ABCMeta
    
    def __init__(self, cfg_manager):
        super(UdXilinxProgrammer, self).__init__()
        self._cfg_manager = cfg_manager

    @staticmethod
    def create(cfg_manager):
        return PICProgrammer(cfg_manager)
    
    @abstractmethod
    def program(self, file_name):
        pass


class PICProgrammer(UdXilinxProgrammer):
    
    def __init__(self, cfg_manager):
        super(PICProgrammer, self).__init__(cfg_manager)
    
    @Override(UdXilinxProgrammer)
    def program(self, file_name):
        proc = subprocess.Popen(["/opt/pk2cmd/pk2cmdv1-20Linux2-6/pk2cmd","-PPIC18F45K20","-F%s" % file_name,"-M","-R"], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        code = proc.wait()
        stdout = proc.stdout.read()
        stderr = proc.stderr.read()
        print stdout
        print stderr
        if code != 0:
            raise Exception("Error programming device: %s; %s" % (stdout, stderr))
    
