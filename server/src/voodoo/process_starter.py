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

import subprocess

# try:
#     import pwd
# except:
#    pwd = None

def start_process(popen_args = None, popen_kargs = None):
    if popen_args is None:
        popen_args = ()
    if popen_kargs is None:
        popen_kargs = {}

    #
    # TODO:
    #
    # We must make a fork, manage pipes, etc. and we have other priorities
    # right now.
    #
    # uid = pwd.getpwnam(username)

    return subprocess.Popen(*popen_args, **popen_kargs)
