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

class GoBackException(Exception):
    def __init__(self):
        super(GoBackException, self).__init__()

class InvalidNullableAndDefaultValuesException(Exception):
    def __init__(self, message):
        super(InvalidNullableAndDefaultValuesException, self).__init__(message)