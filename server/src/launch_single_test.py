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
        print >> sys.stderr, "python %s [-g] <testfile>" % sys.argv[0]
        sys.exit(1)

if len(sys.argv) == 3 and sys.argv[1] == '-g':
    testfile = sys.argv[2]
    gui = True
else:
    testfile = sys.argv[1]
    gui = False

if not testfile.endswith('.py'):
        print >> sys.stderr, "python %s <testfile>" % sys.argv[0]
        sys.exit(2)

module_name = testfile[:-3].replace(os.sep,'.')

def debugThreads():
    import threading
    print "%i threads running:" % threading.activeCount()
    for i in threading.enumerate():
        print i,i.__module__
    print
    import voodoo.gen.protocols.SOAP.ServerSOAP as SSOAP
    print "ServerSoap:",SSOAP._resource_manager.get_current_resources()

print "Launching... %s" % module_name
module =  __import__(module_name, globals(), locals(), [module_name])
suite = module.suite
if gui:
    import unittestgui
    unittestgui.main(__name__ + '.suite')
else:
    try:
        unittest.main(module = module, defaultTest = 'suite', argv = [sys.argv[0]] + sys.argv[2:])
    finally:
        debugThreads()
