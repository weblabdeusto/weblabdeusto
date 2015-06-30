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
from __future__ import print_function, unicode_literals

#
# Level 1 did not support batch:
# - start and dispose could return anything
# - start and dispose did not receive any parameter
#
level_1     = '1'
level_3_0   = level_1
level_3_9   = level_1
level_4_0M1 = level_1


#
# Level 2 started supporting batch:
# - start and dispose had to return something in JSON
# - start could receive new arguments
#
level_2            = '2'
level_4_1          = level_2
level_2_concurrent = level_2 + '_concurrent'

#
# Current always points to the latest API
#
current       = level_2
level_current = current

supported_levels = level_1, level_2

def get_level(level):
    return globals().get('level_' + str(level))

def is_level(level):
    return get_level(level) is not None

def is_supported(level):
    return get_level(level) is not None and get_level(level) in supported_levels

