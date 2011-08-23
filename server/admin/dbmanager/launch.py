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

import sys, os
sys.path.append(os.sep.join(('..','..','src')))

import libraries

from weblab.admin.dbmanager.controller import Controller

if __name__ == "__main__":
    controller = Controller()