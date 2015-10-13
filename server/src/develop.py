#!/usr/bin/env python
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

from __future__ import print_function, unicode_literals

"""
develop.py is a script used for the development of WebLab-Deusto. It 
runs the tests with different UIs, install the requirements, deploys 
the database used for tests, shows the test coverage, etc.

In order to see the options, run:

 $ ./develop.py --help

"""

import os
import sys
import glob
import test
import time
import codecs
import getpass
import unittest
import urllib2
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
                mod = __import__(module.__name__ + '.' + module_name, globals(), locals(), [str(module_name)])
                setattr(module, module_name, mod)
                if hasattr(mod, 'suite'):
                    suites.append(mod.suite())
            elif os.path.isdir(content_path) and os.path.exists(content_path + os.sep + '__init__.py'):
                module_name = content
                mod = __import__(module.__name__ + '.' + module_name, globals(), locals(), [str(module_name)])
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

def runConsole(single_test, avoid_integration, argv):
    if single_test is None:
        if os.name == 'posix':
            os.system("clear")
        module = None
    else:
        module_name = single_test[:-3].replace(os.sep,'.')
        module =  __import__(module_name, globals(), locals(), [str(module_name)])

    old_sys_exit = sys.exit
    def _exit(status = 0):
        global EXIT_VALUE
        EXIT_VALUE = status
    sys.exit = _exit
    global AVOID_INTEGRATION
    AVOID_INTEGRATION = avoid_integration
    sys.argv = argv
    if module is None:
        unittest.main(defaultTest = 'suite')
    else:
        unittest.main(module = module, defaultTest = 'suite')
    debugThreads()
    old_sys_exit(EXIT_VALUE)

def runXml(folder):
    def runSuite(suite, file_name):
        output = open(file_name,'w')
        sio = StringIO.StringIO()
        try:
            wasSuccessful = xmlrunner.XMLTestRunner(output, stream = sio).run(suite).wasSuccessful()
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
    print("%i threads running:" % threading.activeCount())
    for i in threading.enumerate():
        print(i,i.__module__)
    print()
    from test.util.ports import CURRENT_PORT
    print("Max port achieved:", CURRENT_PORT)

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
        for line in codecs.open(exc_file, encoding = 'utf-8'):
            if line.startswith('class '):
                classname = line.split(' ')[1].split('(')[0].strip()
                exceptions[classname] = [0, exc_file]

    for exc_file in exception_files + source_files:
        content = codecs.open(exc_file, encoding = 'utf-8').read()

        to_remove = []
        for exception in exceptions:
            exceptions[exception][0] += content.count(exception)
            if exceptions[exception][0] >= 2:
                to_remove.append(exception)

        for exc in to_remove:
            exceptions.pop(exc)

    for exception in exceptions:
        exc_file = exceptions[exception][1]
        print("Unused exception: %s at %s" % (exception, exc_file), file=sys.stderr)

def check_all_unused_exceptions():
    check_unused_exceptions( 'weblab/exceptions', ('weblab', ) )
    check_unused_exceptions( 'voodoo/exceptions', ('voodoo', 'weblab') )

def check_flakes():
    try:
        from pyflakes.scripts.pyflakes import main as main_pyflakes
    except ImportError:
        print("pyflakes not installed. Did you run pip install -r requirements_tests.txt or python develop.py --install-basic-requirements?", file=sys.stderr)
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
            print(line, file=sys.stderr)

    check_all_unused_exceptions()
    return 0

def deploy_testdb(options):
    from weblab.admin.deploy import insert_required_initial_data, populate_weblab_tests, generate_create_database, insert_required_initial_coord_data
    import weblab.db.model as Model
    import weblab.core.coordinator.sql.model as CoordinatorModel

    import voodoo.sessions.db_lock_data as DbLockData
    import voodoo.sessions.sqlalchemy_data as SessionSqlalchemyData

    from sqlalchemy import create_engine
    
    try:
        import MySQLdb
        dbi = MySQLdb
    except ImportError:
        try:
            import pymysql_sa
        except ImportError:
            raise Exception("Neither MySQLdb nor pymysql_sa have been installed. First install them by running 'pip install pymysql_sa' or 'pip install python-mysql'")
        pymysql_sa.make_default_mysql_dialect()

    t_initial = time.time()
    
    db_dir = 'db'
    if not os.path.exists(db_dir):
        os.mkdir(db_dir)

    db_engine                = options.testdb_engine
    weblab_db_username       = options.testdb_user
    weblab_db_password       = options.testdb_passwd
    weblab_admin_db_username = options.testdb_admin_user
    if options.testdb_ask_admin_passwd:
        weblab_admin_db_password = getpass.getpass("Database password:".encode('utf8'))
    else:
        weblab_admin_db_password = options.testdb_admin_passwd

    if db_engine == 'mysql':
        weblab_test_db_str = 'mysql://%s:%s@localhost/WebLabTests%s'         % (weblab_db_username, weblab_db_password,'%s')
        weblab_coord_db_str = 'mysql://%s:%s@localhost/WebLabCoordination%s' % (weblab_db_username, weblab_db_password, '%s')
        weblab_sessions_db_str = 'mysql://%s:%s@localhost/WebLabSessions'    % (weblab_db_username, weblab_db_password)
    elif db_engine == 'sqlite':
        weblab_test_db_str = 'sqlite:///db/WebLabTests%s.db'
        weblab_coord_db_str = 'sqlite:///db/WebLabCoordination%s.db'
        weblab_sessions_db_str = 'sqlite:///db/WebLabSessions.db'
    else:
        raise Exception("db engine %s not supported" % db_engine)

    if options.testdb_create_db:
        create_database = generate_create_database(db_engine)
        if create_database is None:
            raise Exception("db engine %s not supported for creating database" % db_engine)

        t = time.time()

        error_message = 'Could not create database. This may happen if the admin db credentials are wrong. Try --db-ask-admin-passwd'

        create_database(error_message, weblab_admin_db_username, weblab_admin_db_password, "WebLab",              weblab_db_username, weblab_db_password, db_dir = db_dir)
        create_database(error_message, weblab_admin_db_username, weblab_admin_db_password, "WebLabTests",         weblab_db_username, weblab_db_password, db_dir = db_dir)
        create_database(error_message, weblab_admin_db_username, weblab_admin_db_password, "WebLabTests2",        weblab_db_username, weblab_db_password, db_dir = db_dir)
        create_database(error_message, weblab_admin_db_username, weblab_admin_db_password, "WebLabTests3",        weblab_db_username, weblab_db_password, db_dir = db_dir)

        create_database(error_message, weblab_admin_db_username, weblab_admin_db_password, "WebLabIntTests1",     weblab_db_username, weblab_db_password, db_dir = db_dir)

        create_database(error_message, weblab_admin_db_username, weblab_admin_db_password, "WebLabCoordination",  weblab_db_username, weblab_db_password, db_dir = db_dir)
        create_database(error_message, weblab_admin_db_username, weblab_admin_db_password, "WebLabCoordination2", weblab_db_username, weblab_db_password, db_dir = db_dir)
        create_database(error_message, weblab_admin_db_username, weblab_admin_db_password, "WebLabCoordination3", weblab_db_username, weblab_db_password, db_dir = db_dir)
        create_database(error_message, weblab_admin_db_username, weblab_admin_db_password, "WebLabSessions",      weblab_db_username, weblab_db_password, db_dir = db_dir)

        print("Databases created.\t\t\t\t[done] [%1.2fs]" % (time.time() - t))
    
    #####################################################################
    # 
    # Populating main database
    #
    for tests in ('','2','3'):
        print("Populating 'WebLabTests%s' database...  \t\t" % tests, end="")
        t = time.time()

        engine = create_engine(weblab_test_db_str % tests, echo = False)
        metadata = Model.Base.metadata
        metadata.drop_all(engine)
        metadata.create_all(engine)

        insert_required_initial_data(engine)
        populate_weblab_tests(engine, tests)

        print("[done] [%1.2fs]" % (time.time() - t))

    #####################################################################
    # 
    # Populating Coordination database
    # 

    for coord in ('','2','3'):
        print("Populating 'WebLabCoordination%s' database...\t" % coord, end="")
        t = time.time()

        engine = create_engine(weblab_coord_db_str % coord, echo = False)

        CoordinatorModel.load()

        metadata = CoordinatorModel.Base.metadata
        metadata.drop_all(engine)
        metadata.create_all(engine)
        
        insert_required_initial_coord_data(engine)

        print("[done] [%1.2fs]" % (time.time() - t))


    #####################################################################
    # 
    # Populating Sessions database
    # 


    print("Populating 'WebLabSessions' database...\t\t", end="")
    t = time.time()

    engine = create_engine(weblab_sessions_db_str, echo = False)

    metadata = DbLockData.SessionLockBase.metadata
    metadata.drop_all(engine)
    metadata.create_all(engine)    

    metadata = SessionSqlalchemyData.SessionBase.metadata
    metadata.drop_all(engine)
    metadata.create_all(engine)   

    print("[done] [%1.2fs]" % (time.time() - t))

    print("Total database deployment: \t\t\t[done] [%1.2fs]" % (time.time() - t_initial))



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

    parser.add_option('-f', '--flakes',            dest='flakes', action="store_true", default = False, 
                                                   help = "Run pyflakes, not tests")

    parser.add_option('-t', '--tests',             dest='tests', action="store_true", default = False, 
                                                   help = "Additionally run the tests")

    parser.add_option('-s', '--single',            dest='single_test', default = None, metavar = 'TESTFILE', 
                                                   help = "Run a single test suite (instead of all the tests)")

    parser.add_option('-c', '--coverage',          dest='coverage', action="store_true", default = False, 
                                                   help = "Measure the coverage")

    parser.add_option('--coverage-report',         dest='coverage_report', default = 'report',  choices = ('report', 'xml', 'html'),
                                                   help = "Coverage report style (report, xml, html)", metavar = 'REPORT_STYLE')

    parser.add_option('--compile-gwt-client',      dest='compile_client', action='store_true', default=False,
                                                   help = "Compiles the client.")

    parser.add_option('--dont-disable-proxies',    dest='dont_disable_proxies', action='store_true', default=False,
                                                   help = "Do not disable HTTP proxies (which sometimes are problematic).")

    install_options = optparse.OptionGroup(parser, "Installation environment",
                                                   "You may want to deploy WebLab-Deusto in a virtualenv environment. " 
                                                   "Through these options you can select them and install dependencies on it.")

    install_options.add_option('-e', '--env', '--environment',       dest='environment', default=None, metavar="ENVIRONMENT",
                                                   help = "Use the specified environment, generated by virtualenv, to import so "
                                                          "as to use installed libraries.")

    install_options.add_option('--install-weblab',          dest='install_weblab', action='store_true', default=False,
                                                    help = "Call the setup.py script to install weblab")

    install_options.add_option('--install-basic-requirements', dest='install_basic_requirements', action='store_true', default=False,
                                                    help = "Install the basic requirements in the current environment (the ones required for testing and so on)")

    install_options.add_option('--install-all-requirements', dest='install_all_requirements', action='store_true', default=False,
                                                    help = "Install all the requirements in the current environment (including the ones that require compiling)")

    parser.add_option_group(install_options)
    
    testdb_options = optparse.OptionGroup(parser, "Test database",
                                            "So as to run the tests, the testing database must be created and populated.")

    testdb_options.add_option('--deploy-test-db',   dest='deploy_testdb', action='store_true', default=False,
                                                    help = "Deploys the testing database.")
                                                   
    testdb_options.add_option('--db-engine',        dest='testdb_engine', default='mysql', metavar="ENGINE",
                                                    help = "engine used for the testing database.")
    
    testdb_options.add_option('--db-create-db',     dest='testdb_create_db', action='store_true', default=False,
                                                    help = "Create the database before populating it. If not selected, the system "
                                                           "will expect you to create it with the proper credentials prior to run this "
                                                           "script. The system does not support all engines (just MySQL and sqlite). ")

    testdb_options.add_option('--db-admin-user',    dest='testdb_admin_user',  default='root', metavar="ADMIN_DB_USER",
                                                    help = "Database admin user for the creating the testing database (default: root)")

    testdb_options.add_option('--db-admin-passwd',  dest='testdb_admin_passwd', default='', metavar="ADMIN_DB_PASSWORD",
                                                    help = "Database admin password for the creating the testing database.")

    testdb_options.add_option('--db-ask-admin-passwd',  dest='testdb_ask_admin_passwd', default=False, action='store_true',
                                                    help = "Instead of providing the admin password, ask for it from the standard input.")


    testdb_options.add_option('--db-user',          dest='testdb_user',  default='weblab', metavar="DB_USER",
                                                    help = "Database user for populating the database (default: weblab)")

    testdb_options.add_option('--db-passwd',        dest='testdb_passwd', default='weblab', metavar="DB_PASSWORD",
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

    if options.coverage:
        coverage_script = list(sys.argv)
        coverage_script.insert(0, 'coverage')
        coverage_script.insert(1, 'run')
        coverage_script.insert(2, '--branch')
        if '--coverage' in coverage_script:
            coverage_script.remove('--coverage')
        if '-c' in coverage_script:
            coverage_script.remove('-c')
        exit_value = os.system(' '.join(coverage_script))
        if exit_value == 0:
            os.system('coverage %s --omit="test/*,develop*,conf*,env*,voodoo/patcher*"' % options.coverage_report)
            sys.exit(0)
        else:
            sys.exit(exit_value)

    if options.install_basic_requirements or options.install_all_requirements:
        os.system("pip install -r requirements.txt")
        os.system("pip install -r requirements_testing.txt")
        os.system("pip install -r requirements_recommended.txt")
    if options.install_all_requirements:
        os.system("pip install -r requirements_suggested.txt")

    if options.install_weblab:
        os.system("python setup.py install")

    if options.deploy_testdb:
        deploy_testdb(options)
        if not options.tests and not options.flakes and not options.compile_client:
            sys.exit(0)

    if options.compile_client:
        CLIENT_LOCATION = os.path.abspath(os.path.join('..','..','client'))
        WAR_LOCATION = os.path.join(CLIENT_LOCATION,'war')
        from weblab.admin.client_deploy import compile_client
        compile_client(WAR_LOCATION, CLIENT_LOCATION)
        if not options.tests and not options.flakes:
            sys.exit(0)

    if options.flakes:
        flakes_return_code = check_flakes()
        if not options.tests:
            sys.exit(flakes_return_code)

    if options.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.CRITICAL + 1)

    if len(os.environ.get('http_proxy','')) > 0 and not options.dont_disable_proxies:
        print("Some tests fail when a proxy is present.", file=sys.stderr)
        print("The proxy will be disabled to run the tests.", file=sys.stderr)
        print("Pass --dont-disable-proxies to avoid this behavior", file=sys.stderr)
        os.environ.pop('http_proxy',None)
        os.environ.pop('https_proxy',None)
        opener = urllib2.build_opener(urllib2.ProxyHandler({}))
        urllib2.install_opener(opener)

    if options.ui == 'console':
        runConsole(options.single_test, options.avoid_integration, [sys.argv[0]] + (options.options or []))
    elif options.ui == 'gui':
        runGui(options.avoid_integration, [sys.argv[0]] + (options.options or []))
    elif options.ui == 'xml':
        if options.directory is not None:
            runXml(options.directory)
        else:
            print("Select xml folder", file=sys.stderr)
    else:
        print("Unregistered user interface: %s" % options.ui, file=sys.stderr)

