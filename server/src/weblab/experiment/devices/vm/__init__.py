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
# Author: Luis Rodr�guez <luis.rodriguez@opendeusto.es>
# 
from __future__ import print_function, unicode_literals

import manager as VirtualMachineManager
import dummy as VirtualMachineDummy
import virtualbox as VirtualBox

def _():
    print(VirtualMachineManager, VirtualMachineDummy, VirtualBox)

__all__ = ["VirtualMachineManager", "VirtualMachineDummy", "VirtualBox"]
