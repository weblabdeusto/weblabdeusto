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

def get_files():

    def gather_exc_files(excluded, folder, files):
        python_files.extend( 
            ( os.path.join(folder, python_file) 
                for python_file in files 
                if python_file == 'exc.py' 
            ) )

    def gather_not_exc_files(excluded, folder, files):
        python_files.extend( 
            ( os.path.join(folder, python_file) 
                for python_file in files 
                if python_file.endswith('.py') and python_file != 'exc.py' 
            ) )

    python_files = []
    os.path.walk('.', gather_exc_files, None)
    exception_python_files = python_files

    python_files = []
    os.path.walk('.', gather_not_exc_files, None)
    source_python_files = python_files

    return exception_python_files, source_python_files

def check_unused_exceptions(exceptions_folder, source_folders):
    exception_files, source_files = get_files()

    exceptions = {}
    for exc_file in exception_files:
        for line in open(exc_file):
            if line.startswith('class '):
                classname = line.split(' ')[1].split('(')[0].strip()
                exceptions[classname] = [0, exc_file]

    for exc_file in exception_files + source_files:
        content = open(exc_file).read()

        to_remove = []
        for exception in exceptions:
            exceptions[exception][0] += content.count(exception)
            if exceptions[exception][0] >= 2:
                to_remove.append(exception)

        for exc in to_remove:
            exceptions.pop(exc)

    for exception in exceptions:
        exc_file = exceptions[exception][1]
        print >> sys.stderr, "Unused exception: %s at %s" % (exception, exc_file)

def check():
    check_unused_exceptions( 'weblab/exceptions', ('weblab', ) )
    check_unused_exceptions( 'voodoo/exceptions', ('voodoo', 'weblab') )
    check_unused_exceptions( 'voodoo/gen/exceptions', ('voodoo', 'weblab') )

if __name__ == '__main__':
    check()

