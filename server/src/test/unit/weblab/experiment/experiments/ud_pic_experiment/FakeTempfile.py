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

import tempfile
import os

def mkstemp(prefix, suffix):
    """Fake mkstemp that always generates the same filename, for testing purposes."""
    file_name = tempfile.gettempdir() + os.sep + prefix + "T3MP0R4L" + suffix
    fd = os.open(file_name, tempfile._text_openflags)
    return fd, file_name