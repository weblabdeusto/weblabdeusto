#!/usr/bin/python
# -*- coding: utf-8 -*-
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

import os
import new
import test
import unittest
import logging
import sys
import StringIO
import optparse

def get_suites(avoid_integration = False, avoid_stress = True):
    ROOT_DIRECTORY=test.__file__[:test.__file__.rfind('test')]

    suites = []

    def recursion_on_modules(module, directory):
        if avoid_integration:
            if module.__name__.split('.')[-1] in ('stress','integration'):
                return
        if avoid_stress:
            if module.__name__.split('.')[-1] == 'stress':
                return

        for content in os.listdir(directory):
            content_path = directory + os.sep + content
            if content_path.endswith('.py') and content_path != '__init__.py':
                module_name = content[:-len('.py')]
                mod = __import__(module.__name__ + '.' + module_name, globals(), locals(), [module_name])
                setattr(module, module_name, mod)
                if hasattr(mod, 'suite'):
                    suites.append(mod.suite())
            elif os.path.isdir(content_path) and os.path.exists(content_path + os.sep + '__init__.py'):
                module_name = content
                mod = __import__(module.__name__ + '.' + module_name, globals(), locals(), [module_name])
                setattr(module, module_name, mod)
                recursion_on_modules(mod, content_path)

    recursion_on_modules(test, ROOT_DIRECTORY + 'test')
    return suites


AVOID_INTEGRATION = False

def suite():
    global AVOID_INTEGRATION
    suites = get_suites(AVOID_INTEGRATION)
    suite = unittest.TestSuite(suites)
    return suite

def runGui(avoid_integration, argv):
    "python /usr/lib/python2.4/site-packages/unittestgui.py launch_test.suite"

    global AVOID_INTEGRATION
    AVOID_INTEGRATION = avoid_integration

    import unittestgui
    sys.argv = argv
    unittestgui.main(__name__ + '.suite')

EXIT_VALUE = 0

def runConsole(avoid_integration, argv):
    if os.name == 'posix':
        os.system("clear")

    old_sys_exit = sys.exit
    def _exit(status = 0):
        global EXIT_VALUE
        EXIT_VALUE = status
    sys.exit = _exit
    global AVOID_INTEGRATION
    AVOID_INTEGRATION = avoid_integration
    sys.argv = argv
    unittest.main(defaultTest = 'suite')
    debugThreads()
    old_sys_exit(EXIT_VALUE)

def runXml(folder):
    def runSuite(suite, file_name):
        output = open(file_name,'w')
        try:
            wasSuccessful = xmlrunner.XmlTestRunner(output).run(suite).wasSuccessful()
        finally:
            output.close()
        return wasSuccessful

    all_suites_ordered = {
            # classname : [ testcase, testcase, testcase]
        }

    def orderRecursively(suite):
        if hasattr(suite,'_test') and len(suite._test) > 0:
            for i in suite._test:
                orderRecursively(i)
        elif hasattr(suite, '_tests') and len(suite._tests) > 0:
            for i in suite._tests:
                orderRecursively(i)
        else:
            class_ = suite.__class__
            classname = class_.__module__ + "." + class_.__name__
            if classname in all_suites_ordered:
                all_suites_ordered[classname].append(suite)
            else:
                all_suites_ordered[classname] = [suite]

    import xmlrunner
    suites = get_suites(avoid_stress=True)

    for suite in suites:
        orderRecursively(suite)

    wasSuccessful = True

    for classname in all_suites_ordered:
        current_suite = unittest.TestSuite(all_suites_ordered[classname])
        file_name = folder + os.sep + 'TEST-%s.xml' % classname
        wasSuccessful &= runSuite(current_suite, file_name)

    if not wasSuccessful:
        sys.exit(-1)

def debugThreads():
    import threading
    print "%i threads running:" % threading.activeCount()
    for i in threading.enumerate():
        print i,i.__module__
    print
    import voodoo.gen.protocols.SOAP.ServerSOAP as SSOAP
    print "ServerSoap:",SSOAP._resource_manager.get_current_resources()

#DEFAULT_UI     = 'xml'
#DEFAULT_UI     = 'gui'
DEFAULT_UI     = 'console'

def check_flakes():
    try:
        from pyflakes.scripts.pyflakes import main as main_pyflakes
    except ImportError:
        return

    stdout = sys.stdout
    sys.stdout = StringIO.StringIO()
    number_of_lines = main_pyflakes(("weblab", "test", "voodoo", "experiments"))
    results = sys.stdout
    sys.stdout = stdout
    lines = [ line for line in results.getvalue().split('\n') if line.find('generated') < 0 ]
    for line in lines:
        if len(line.strip()) > 0:
            print >> sys.stderr, line

    import check_unused_exceptions
    check_unused_exceptions.check()

if __name__ == '__main__':
    def vararg_callback(option, opt_str, value, parser):
         assert value is None
         value = [ arg for arg in parser.rargs ]
         del parser.rargs[:len(value)]
         setattr(parser.values, option.dest, value)

    parser = optparse.OptionParser()

    parser.add_option('-u', '--ui',                dest='ui', choices = ('console', 'gui', 'xml'), default = 'console', 
                                                   help = "User interface to use: console, gui (Tkinter) or xml (JUnit format)")

    parser.add_option('-d', '--debug',             dest='debug', action='store_true',              default=False,
                                                   help = "Show additional debugging information")

    parser.add_option('-i', '--avoid-integration', dest='avoid_integration', action='store_true',  default=False,
                                                   help = "Avoid the integration tests")

    parser.add_option('--dir', '--directory',      dest='directory', default = None,
                                                   help = "If selecting XML, in which directory should the results be placed")

    parser.add_option('-o', '--options',           dest='options', action='callback', callback = vararg_callback, 
                                                   help = "Options to be passed to unittest. Beware that no other option "
                                                          "will be interpreted by this command after: they will be managed "
                                                          "by unittest directly.")

    parser.add_option('-e', '--environment',       dest='environment', default=None, metavar="ENVIRONMENT",
                                                   help = "Use the specified environment, generated by virtualenv, to import so "
                                                          "as to use installed libraries.")

    options, args = parser.parse_args()

    if options.environment is not None:
        potential_locations = [ os.path.join(options.environment, 'bin', 'activate_this.py'),
                                os.path.join(options.environment, 'Scripts', 'activate_this.py'), ]
        for potential_location in potential_locations:
            if os.path.exists(potential_location):
                activate_this = potential_location
                break
        else:
            parser.error("Environment %s not found. Tried %s" % (options.environment, potential_locations))

        execfile(activate_this, dict(__file__=activate_this))


    if options.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.CRITICAL + 1)

    if options.ui == 'console':
        runConsole(options.avoid_integration, [sys.argv[0]] + (options.options or []))
    elif options.ui == 'gui':
        runGui(options.avoid_integration, [sys.argv[0]] + (options.options or []))
    elif options.ui == 'xml':
        if options.directory is not None:
            runXml(options.directory)
        else:
            print >>sys.stderr, "Select xml folder"
    else:
        print >>sys.stderr, "Unregistered user interface: %s" % options.ui

