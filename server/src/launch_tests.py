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
import sys
import glob
import test
import unittest
import logging
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
            wasSuccessful = xmlrunner.XMLTestRunner(output).run(suite).wasSuccessful()
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

def check_all_unused_exceptions():
    check_unused_exceptions( 'weblab/exceptions', ('weblab', ) )
    check_unused_exceptions( 'voodoo/exceptions', ('voodoo', 'weblab') )
    check_unused_exceptions( 'voodoo/gen/exceptions', ('voodoo', 'weblab') )


def check_flakes():
    try:
        from pyflakes.scripts.pyflakes import main as main_pyflakes
    except ImportError:
        print >> sys.stderr, "pyflakes not installed. Did you run pip install -r requirements_tests.txt or python launch_tests.py --install-basic-requirements?"
        return -1

    stdout = sys.stdout
    sys.stdout = StringIO.StringIO()
    original_argv = sys.argv
    sys.argv = [original_argv[0], "weblab", "test", "voodoo", "experiments"]
    try:
        number_of_lines = main_pyflakes()
    except SystemExit:
        pass
    finally:
        results = sys.stdout.getvalue()
        sys.stdout = stdout
        sys.argv   = original_argv

    lines = [ line for line in results.split('\n') if line.find('generated') < 0 ]
    for line in lines:
        if len(line.strip()) > 0:
            print >> sys.stderr, line

    check_all_unused_exceptions()
    return 0

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

    parser.add_option('-e', '--env', '--environment',       dest='environment', default=None, metavar="ENVIRONMENT",
                                                   help = "Use the specified environment, generated by virtualenv, to import so "
                                                          "as to use installed libraries.")

    parser.add_option('-f', '--flakes',            dest='flakes', action="store_true", default = False, 
                                                   help = "Run pyflakes, not tests")

    parser.add_option('-t', '--tests',             dest='tests', action="store_true", default = False, 
                                                   help = "Additionally run the tests")

    parser.add_option('--install-weblab',          dest='install_weblab', action='store_true', default=False,
                                                    help = "Call the setup.py script to install weblab")

    parser.add_option('--install-basic-requirements', dest='install_basic_requirements', action='store_true', default=False,
                                                    help = "Install the basic requirements in the current environment (the ones required for testing and so on)")

    parser.add_option('--install-all-requirements', dest='install_all_requirements', action='store_true', default=False,
                                                    help = "Install all the requirements in the current environment (including the ones that require compiling)")

    parser.add_option('--deploy-stubs',             dest='deploy_stubs', action='store_true', default=False,
                                                    help = "Creates all the ZSI SOAP stubs.")

    # TODO: implement this part
    testdb_options = optparse.OptionGroup(parser, "Test database",
                                            "So as to run the tests, the testing database must be created and populated.")

    testdb_options.add_option('--deploy-test-db',           dest='deploy_testdb', action='store_true', default=False,
                                                    help = "Deploys the testing database.")
                                                    
    testdb_options.add_option('--test-db-engine',           dest='testdb_engine', default='sqlite', metavar="ENGINE",
                                                    help = "engine used for the testing database.")
    
    testdb_options.add_option('--test-db-create-db',        dest='testdb_create_db', action='store_true', default=False,
                                                    help = "Create the database before populating it. If not selected, the system "
                                                           "will expect you to create it with the proper credentials prior to run this "
                                                           "script. The system does not support all engines (just MySQL and sqlite). ")

    testdb_options.add_option('--test-db-admin-user',       dest='testdb_admin_user',  default='root', metavar="ADMIN_DB_USER",
                                                    help = "Database admin user for the creating the testing database (default: root)")

    testdb_options.add_option('--test-db-admin-passwd',     dest='testdb_admin_passwd', default='', metavar="ADMIN_DB_PASSWORD",
                                                    help = "Database admin password for the creating the testing database.")

    testdb_options.add_option('--test-db-user',             dest='testdb_user',  default='weblab', metavar="DB_USER",
                                                    help = "Database user for populating the database (default: weblab)")

    testdb_options.add_option('--test-db-passwd',           dest='testdb_passwd', default='weblab', metavar="DB_PASSWORD",
                                                    help = "Database password for populating the database.")

    parser.add_option_group(testdb_options)

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

    if options.install_basic_requirements or options.install_all_requirements:
        os.system("pip install -r requirements.txt")
        os.system("pip install -r requirements_testing.txt")
        os.system("pip install -r requirements_recommended.txt")
    if options.install_all_requirements:
        os.system("pip install -r requirements_suggested.txt")

    if options.install_weblab:
        os.system("python setup.py install")

    if options.deploy_stubs:
        import weblab.comm.util as comm_util
        comm_util.deploy_stubs()

    if options.flakes:
        flakes_return_code = check_flakes()
        if not options.tests:
            sys.exit(flakes_return_code)

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

