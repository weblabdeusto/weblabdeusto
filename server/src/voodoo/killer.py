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
import sys

def term(popen_obj):
    if sys.platform == "win32":
        from _subprocess import TerminateProcess
        TerminateProcess(popen_obj._handle, 0)
    else:
        import os, signal
        os.kill(popen_obj.pid, signal.SIGTERM)

def kill(popen_obj):
    if sys.platform == "win32":
        term(popen_obj)
    else:
        import os, signal
        os.kill(popen_obj.pid, signal.SIGKILL)
