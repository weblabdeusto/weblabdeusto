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
# Author: Luis Rodr�guez <luis.rodriguez@opendeusto.es>
# 

import VirtualMachineManager
import VirtualMachineDummy
import VirtualBox

def _():
    print VirtualMachineManager, VirtualMachineDummy, VirtualBox

__all__ = ["VirtualMachineManager", "VirtualMachineDummy", "VirtualBox"]