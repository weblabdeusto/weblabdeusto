#!/usr/bin/env python
#-*-*- encoding: utf-8 -*-*-
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
#
from __future__ import print_function, unicode_literals

import time, sys

def show_time():
    cur = time.time()
    tuple = time.localtime(cur)
    return time.asctime(tuple) + ', ' + ('%0.3f millis' % (cur - int(cur)))[2:]

def flush():
    sys.stdout.flush()

