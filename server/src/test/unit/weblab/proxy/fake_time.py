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

import time as real_time

TIME_TO_RETURN = 1289548551.2617509 # 2010_11_12___07_55_51

def time():
    return TIME_TO_RETURN

def strftime(format, gmtime):
    return real_time.strftime(format, gmtime)

def gmtime(timestamp):
    return real_time.gmtime(timestamp)