#!/usr/bin/env python
#-*-*- encoding: utf-8 -*-*-
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

import time
import subprocess
import traceback

_PROCESSES = []

def start_process(popen_args = None, popen_kargs = None):
    if popen_args is None:
        popen_args = ()
    if popen_kargs is None:
        popen_kargs = {}
    process = subprocess.Popen(*popen_args, **popen_kargs)
    _PROCESSES.append(process)
    return process

def clean_created():
    copy = _PROCESSES[:]
    for process in copy:
        _PROCESSES.remove(process)

    for process in copy:
        if process.poll() is None:
            try:
                process.terminate()
            except:
                traceback.print_exc()

    counter = 20
    while counter > 0 and len([ p for p in copy if p.poll() is None ]) > 0:
        counter -= 1
        time.sleep(0.05)

    for process in copy:
        if process.poll() is None:
            try:
                process.kill()
            except:
                traceback.print_exc()
