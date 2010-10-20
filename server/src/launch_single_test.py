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

import libraries, sys, os, unittest

if len(sys.argv) < 2:
        print >> sys.stderr, "python %s <testfile>" % sys.argv[0]
        sys.exit(1)

testfile = sys.argv[1]

if not testfile.endswith('.py'):
        print >> sys.stderr, "python %s <testfile>" % sys.argv[0]
        sys.exit(2)

module_name = testfile[:-3].replace(os.sep,'.')

print "Launching... %s" % module_name
module =  __import__(module_name, globals(), locals(), [module_name])
suite = module.suite

unittest.main(module = module, defaultTest = 'suite', argv = [sys.argv[0]] + sys.argv[2:])
