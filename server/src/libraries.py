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

#import pymysql_sa
#pymysql_sa.make_default_mysql_dialect()

"""
Importing this module automatically adds to the PYTHONPATH the libraries found in "lib" and "lib_branch".

If you make a branch, you can place the replacements of the libraries in the "lib_branch" directory (by
default it doesn't exist), and it will be used instead of the one found in "lib". This way, "lib" can still
be a svn:externals directory.
"""
import sys, os, math, platform, os.path

LIB_DIRECTORY         = os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + os.sep + '..' + os.sep + 'lib')
BRANCH_LIB_DIRECTORY  = os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + os.sep + '..' + os.sep + 'lib_branch')

def check_more_imports():
    latest_import_path = os.path.join(sys.path[0],"more_imports.py")
    if os.path.exists(latest_import_path):
        import more_imports

version = '.'.join((str(i) for i in sys.version_info[0:2]))
if sys.platform == 'darwin':
	# in Mac OS X, platform.architecture() does not return '32bit' when it should
	if sys.maxint <= 2147483647:
		bits = '32'
	else:
		bits = '64'
else:
	bitness, _ = platform.architecture()
	bits = bitness[:-len('bit')] # '32' or '64'

###############################################################################
# 
#       
# 

def configure_path(libraries_dir):
    # 
    # First, import the common packages, common for all platforms.
    # 
    sys.path.insert(0,libraries_dir + os.sep + 'common')
    check_more_imports()

    #
    # Finally, start importing the binaries for the given platform & architecture (e.g. linux2/64)
    # This folder does not need to exist, by default in darwin we use 64 + 32 bits, in win32, 32 bits,
    # and in linux2, 32 bits and then /linux2/2.5/64/ actually uses the 64 binaries.
    # 
    sys.path.insert(0,libraries_dir + os.sep + sys.platform + os.sep + version + os.sep + bits)
    check_more_imports()
    
    #
    # Required so .dll work fine in windows
    # 
    os.environ['PATH'] = os.environ.get('PATH','') + os.pathsep + libraries_dir + os.sep + sys.platform + os.sep + version + os.sep + bits

    #
    # Required so shared .so files (like libmysqlclient.so.15) work fine in linux
    # 
    os.environ['LD_LIBRARY_PATH'] = os.environ.get('LD_LIBRARY_PATH','') + os.pathsep + libraries_dir + os.sep + sys.platform + os.sep + version + os.sep + bits


configure_path(LIB_DIRECTORY)
configure_path(BRANCH_LIB_DIRECTORY)

import patcher
patcher.apply()

def load(): # Dummy method to avoid "unused import" warnings
    pass

