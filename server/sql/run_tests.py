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
# Author: Pablo Orduña <pablo@ordunya.com>
# 

import os
import sys
import glob
import subprocess
import wl_administrator_credentials as cred

mysql = 'mysql' #TODO: not always

#TODO: stdin not used (and < used)

failed = False

SIZE=50

def try_command(message, filename):
    print message + '...' + ' '*(SIZE - len(message)),
    pr = subprocess.Popen(
            mysql + ' -u' + cred.ADMINISTRATOR_USER + ' -p' + cred.ADMINISTRATOR_PASSWORD + ' < ' + filename,
            shell=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
        )
    result = pr.wait()
    failed = result != 0
    if failed:
        print "[failed]: ", pr.stderr.read()
    else:
        print "[done]"
    return failed

failed |= try_command( 'Rebuilding database',             'create_WebLabDB.sql'            )
failed |= try_command( 'Rebuilding session database',     'create_SessionsDB.sql'          )
failed |= try_command( 'Rebuilding coordinator database', 'create_CoordinatorDB.sql'       )

setupfiles = glob.glob("setup_samples" + os.sep + "setup_*.sql")
setupfiles.sort()

for setupfile in setupfiles:
    failed |= try_command( 'Setting up "%s"' % setupfile.split(os.sep)[-1],   setupfile)

if failed:
    sys.exit(-1)
