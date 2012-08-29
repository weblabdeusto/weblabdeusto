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
import getpass
import signal
import sys
import stat
import uuid
import time
import traceback
import sqlite3
import urllib2
import json
from optparse import OptionParser, OptionGroup

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from weblab.util import data_filename
from weblab.admin.monitor.monitor import WebLabMonitor
import weblab.core.coordinator.status as WebLabQueueStatus

from weblab.admin.cli.controller import Controller

import weblab.db.model as Model

import weblab.admin.deploy as deploy

import voodoo.sessions.db_lock_data as DbLockData
import voodoo.sessions.sqlalchemy_data as SessionSqlalchemyData

from voodoo.gen.loader.ConfigurationParser import GlobalParser

# 
# TODO
#  - --virtual-machine
#  - xmlrpc server
#  - Support rebuild-db
# 

SORTED_COMMANDS = []
SORTED_COMMANDS.append(('create',     'Create a new weblab instance')), 
SORTED_COMMANDS.append(('start',      'Start an existing weblab instance')), 
SORTED_COMMANDS.append(('stop',       'Stop an existing weblab instance')),
SORTED_COMMANDS.append(('admin',      'Adminstrate a weblab instance')),
SORTED_COMMANDS.append(('monitor',    'Monitor the current use of a weblab instance')),
SORTED_COMMANDS.append(('rebuild-db', 'Rebuild the database of the weblab instance')), 

COMMANDS = dict(SORTED_COMMANDS)

def check_dir_exists(directory):
    if not os.path.exists(directory):
        print >> sys.stderr,"ERROR: Directory %s does not exist" % directory
        sys.exit(-1)
    if not os.path.isdir(directory):
        print >> sys.stderr,"ERROR: File %s exists, but it is not a directory" % directory
        sys.exit(-1)

def weblab():
    if len(sys.argv) in (1, 2) or sys.argv[1] not in COMMANDS:
        command_list = ""
        max_size = max((len(command) for command in COMMANDS))
        for command, help_text in SORTED_COMMANDS:
            filled_command = command + ' ' * (max_size - len(command))
            command_list += "\t%s\t%s\n" % (filled_command, help_text)
        print >> sys.stderr, "Usage: %s option DIR [option arguments]\n\n%s\n" % (sys.argv[0], command_list)
        sys.exit(0)
    main_command = sys.argv[1]
    if main_command == 'create':
        weblab_create(sys.argv[2])
        sys.exit(0)

    check_dir_exists(sys.argv[2])
    if main_command == 'start':
        weblab_start(sys.argv[2])
    elif main_command == 'stop':
        weblab_stop(sys.argv[2])
    elif main_command == 'monitor':
        weblab_monitor(sys.argv[2])
    elif main_command == 'admin':
        weblab_admin(sys.argv[2])
    elif main_command == 'rebuild-db':
        weblab_rebuild_db(sys.argv[2])
    else:
        print >>sys.stderr, "Command %s not yet implemented" % sys.argv[1]


#########################################################################################
# 
# 
# 
#      W E B L A B     D I R E C T O R Y     C R E A T I O N
# 
# 
# 



COORDINATION_ENGINES = ['sql',   'redis'  ]
DATABASE_ENGINES     = ['mysql', 'sqlite' ]
SESSION_ENGINES      = ['sql',   'redis', 'memory']

def _test_redis(what, verbose, redis_port, redis_passwd, redis_db, redis_host):
    if verbose: print "Checking redis connection for %s..." % what,; sys.stdout.flush()
    kwargs = {}
    if redis_port   is not None: kwargs['port']     = redis_port
    if redis_passwd is not None: kwargs['password'] = redis_passwd
    if redis_db     is not None: kwargs['db']       = redis_db
    if redis_host   is not None: kwargs['host']     = redis_host
    try:
        import redis
    except ImportError:
        print >> sys.stderr, "redis selected for %s; but redis module is not available. Try installing it with 'pip install redis'" % what
        sys.exit(-1)
    else:
        try:
            client = redis.Redis(**kwargs)
            client.get("this.should.not.exist")
        except:
            print >> sys.stderr, "redis selected for %s; but could not use the provided configuration" % what
            traceback.print_exc()
            sys.exit(-1)
        else:
            if verbose: print "[done]"

def uncomment_json(lines):
    new_lines = []
    for line in lines:
        if '//' in line:
            if '"' in line or "'" in line:
                single_quote_open = False
                double_quote_open = False
                previous_slash    = False
                counter           = 0
                comment_found     = False
                for c in line:
                    if c == '/':
                        if previous_slash and not single_quote_open and not double_quote_open:
                            comment_found = True
                            break # counter is the previous one 
                        previous_slash = True
                    else:
                        previous_slash = False
                    if c == '"':
                        double_quote_open = not double_quote_open
                    if c == "'":
                        single_quote_open = not single_quote_open
                        
                    counter += 1

                if comment_found:
                    new_lines.append(line[:counter - 1] + '\n')
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line.split('//')[0])
        else:
            new_lines.append(line)
    return new_lines

DB_ROOT     = None
DB_PASSWORD = None

def _check_database_connection(what, metadata, directory, verbose, db_engine, db_host, db_name, db_user, db_passwd):
    if verbose: print "Checking database connection for %s..." % what,; sys.stdout.flush()

    if db_engine == 'sqlite':
        base_location = os.path.join(os.path.abspath(directory), 'db', '%s.db' % db_name)
        if sys.platform.startswith('win'):
            sqlite_location     = base_location
            location = '/' + base_location
        else:
            sqlite_location = '/' + base_location
            location = '/' + base_location
        sqlite3.connect(database = sqlite_location).close()
    else:
        location = "%(user)s:%(password)s@%(host)s/%(name)s" % { 
                        'user'     : db_user, 
                        'password' : db_passwd, 
                        'host'     : db_host,
                        'name'     : db_name
                    }
    
    db_str = "%(engine)s://%(location)s" % { 
                        'engine'   : db_engine,
                        'location' : location,
                    }
    
    try:
        engine = create_engine(db_str, echo = False)
        engine.execute("select 1")
    except Exception as e:
        print >> sys.stderr, "error: database used for %s is misconfigured" % what
        print >> sys.stderr, "error: %s"  % str(e)
        if verbose:
            traceback.print_exc()
        else:
            print >> sys.stderr, "error: Use -v to get more detailed information"

        try:
            create_database = deploy.generate_create_database(db_engine)
        except Exception as e:
            print >> sys.stderr, "error: You must create the database and the db credentials"
            print >> sys.stderr, "error: reason: there was an error trying to offer you the creation of users:", str(e)
            sys.exit(-1)
        else:
            if create_database is None:
                print >> sys.stderr, "error: You must create the database and the db credentials"
                print >> sys.stderr, "error: reason: weblab does not support creating a database with engine %s" % db_engine
                sys.exit(-1)
            else:
                should_create = raw_input('Would you like to create it now? (y/N) ').lower().startswith('y')
                if not should_create:
                    print >> sys.stderr, "not creating"
                    sys.exit(-1)
                if db_engine == 'sqlite':
                    create_database("Error", None, None, db_name, None, None, db_dir = os.path.join(directory, 'db'))
                elif db_engine == 'mysql':
                    global DB_ROOT, DB_PASSWORD
                    if DB_ROOT is None or DB_PASSWORD is None:
                        admin_username = raw_input("Enter the MySQL administrator username (typically root): ") or 'root'
                        admin_password = getpass.getpass("Enter the MySQL administrator password: ")
                    else:
                        admin_username = DB_ROOT
                        admin_password = DB_PASSWORD
                    try:
                        create_database("Did you type your password incorrectly?", admin_username, admin_password, db_name, db_user, db_passwd, db_host)
                    except Exception as e:
                        print >> sys.stderr, "error: could not create database. reason:", str(e)
                        sys.exit(-1)
                    else:
                        DB_ROOT     = admin_username
                        DB_PASSWORD = admin_password
                else:
                    print >> sys.stderr, "error: You must create the database and the db credentials"
                    print >> sys.stderr, "error: reason: weblab does not support gathering information to create a database with engine %s" % db_engine
                    sys.exit(-1)



    if verbose: print "[done]"
    if verbose: print "Adding information to the %s database..." % what,; sys.stdout.flush()
    metadata.drop_all(engine)
    metadata.create_all(engine)
    if verbose: print "[done]"
    return engine



def weblab_create(directory):

    ###########################################
    # 
    # Define possible options
    # 


    parser = OptionParser(usage="%prog create DIR [options]")

    parser.add_option("-f", "--force",            dest="force", action="store_true", default=False,
                                                   help = "Overwrite the contents even if the directory already existed.")

    parser.add_option("-v", "--verbose",          dest="verbose", action="store_true", default=False,
                                                   help = "Show more information about the process.")

    parser.add_option("--add-test-data",          dest="add_test_data", action="store_true", default=False,
                                                  help = "Populate the database with sample data")

    parser.add_option("--cores",                  dest="cores",           type="int",    default=1,
                                                  help = "Number of core servers.")

    parser.add_option("--start-port",             dest="start_ports",     type="int",    default=10000,
                                                  help = "From which port start counting.")

    parser.add_option("-i", "--system-identifier",dest="system_identifier", type="string", default="",
                                                  help = "A human readable identifier for this system.")

    parser.add_option("--enable-https",           dest="enable_https",   action="store_true", default=False,
                                                  help = "Tell external federated servers that they must use https when connecting here")

    parser.add_option("--base-url",               dest="base_url",       type="string",    default="",
                                                  help = "Base location, before /weblab/. Example: /deusto.")

    parser.add_option("--entity-link",            dest="entity_link",       type="string",  default="http://www.yourentity.edu",
                                                  help = "Link of the host entity (e.g. http://www.deusto.es ).")

    parser.add_option("--server-host",            dest="server_host",     type="string",    default="localhost",
                                                  help = "Host address of this machine. Example: weblab.domain.")

    parser.add_option("--poll-time",              dest="poll_time",     type="int",    default=350,
                                                  help = "Time in seconds that will wait before expiring a user session.")

    parser.add_option("--inline-lab-server",      dest="inline_lab_serv", action="store_true", default=False,
                                                  help = "Laboratory server included in the same process as the core server. " 
                                                         "Only available if a single core is used." )

    admin_data = OptionGroup(parser, "Administrator data",
                                                "Administrator basic data: username, password, etc.")
    admin_data.add_option("--admin-user",             dest="admin_user",       type="string",    default="admin",
                                                  help = "Username for the WebLab-Deusto administrator")
    admin_data.add_option("--admin-name",             dest="admin_name",       type="string",    default="Administrator",
                                                  help = "Full name of the administrator")
    admin_data.add_option("--admin-password",       dest="admin_password", type="string",    default="password",
                                                  help = "Administrator password ('password' is the default)")
    admin_data.add_option("--admin-mail",             dest="admin_mail",       type="string",    default="",
                                                  help = "E-mail address of the system administrator.")

    parser.add_option_group(admin_data)

    # TODO
    experiments = OptionGroup(parser, "Experiments options",
                                "While most laboratories are specific to a particular equipment, "
                                "some of them are useful anywhere (such as the VM experiment, as long as " 
                                "you have a VirtualBox virtual machine that you'd like to deploy, or the "
                                "logic game, which does not require any equipment). Other experiments, "
                                "such as VISIR, have been deployed in many universities. Finally, for "
                                "development purposes, the XML-RPC experiment is particularly useful.")

    # TODO
    experiments.add_option("--xmlrpc-experiment",      dest="xmlrpc_experiment", action="store_true", default=False,
                                                       help = "By default, the Experiment Server is located in the same process as the  " 
                                                              "Laboratory server. However, it is possible to force that the laboratory  "
                                                              "uses XML-RPC to contact the Experiment Server. If you want to test a "
                                                              "Java, C++, .NET, etc. Experiment Server, you can enable this option, "
                                                              "and the system will try to find the Experiment Server in other port ")

    experiments.add_option("--dummy-experiment-name", dest="dummy_name", type="string",    default="dummy",
                                                       help = "There is a testing experiment called 'dummy'. You may change this name "
                                                              "(e.g. to dummy1 or whatever) by changing this option." )

    # TODO
    experiments.add_option("--xmlrpc-experiment-port", dest="xmlrpc_experiment_port", type="int",    default=None,
                                                       help = "What port should the Experiment Server use. Useful for development.")

    experiments.add_option("--visir-server",           dest="visir_server", action="store_true", default=False,
                                                       help = "Add a VISIR server to the deployed system. "  )

    experiments.add_option("--visir-slots",            dest="visir_slots", default=60, type="int", metavar='SLOTS',
                                                       help = "Number of concurrent users of VISIR. "  )

    experiments.add_option("--visir-experiment-name",  dest="visir_experiment_name", default='visir', type="string", metavar='EXPERIMENT_NAME',
                                                       help = "Name of the VISIR experiment. "  )

    experiments.add_option("--visir-base-url",         dest="visir_base_url", default='', type="string", metavar='VISIR_BASE_URL',
                                                       help = "URL of the VISIR system (e.g. http://weblab-visir.deusto.es/electronics/ ). It should contain login.php, for instance. "  )

    experiments.add_option("--visir-measurement-server", dest="visir_measurement_server", default=None, type="string", metavar='MEASUREMENT_SERVER',
                                                       help = "Measurement server. E.g. weblab-visir.deusto.es:8080 "  )

    experiments.add_option("--visir-use-php",          dest="visir_use_php", action="store_true", default=True,
                                                       help = "VISIR can manage the authentication through a PHP code. This option is slower, but required if that scheme is used."  )

    experiments.add_option("--visir-login",            dest="visir_login", default='guest', type="string", metavar='USERNAME',
                                                       help = "If the PHP version is used, define which username should be used. Default: guest."  )

    experiments.add_option("--visir-password",         dest="visir_password", default='guest', type="string", metavar='PASSWORD',
                                                       help = "If the PHP version is used, define which password should be used. Default: guest."  )

    # TODO
    experiments.add_option("--logic-server",           dest="logic_server", action="store_true", default=False,
                                                       help = "Add a logic server to the deployed system. "  )

    # TODO
    experiments.add_option("--vm-server",              dest="vm_server", action="store_true", default=False,
                                                       help = "Add a VM server to the deployed system. "  )

    parser.add_option_group(experiments)

    sess = OptionGroup(parser, "Session options",
                                "WebLab-Deusto may store sessions in a database, in memory or in redis."
                                "Choose one system and configure it." )

    sess.add_option("--session-storage",          dest="session_storage", choices = SESSION_ENGINES, default='memory',
                                                  help = "Session storage used. Values: %s." % (', '.join(SESSION_ENGINES)) )

    sess.add_option("--session-db-engine",        dest="session_db_engine", type="string", default="sqlite",
                                                  help = "Select the engine of the sessions database.")

    sess.add_option("--session-db-host",          dest="session_db_host", type="string", default="localhost",
                                                  help = "Select the host of the session server, if any.")

    sess.add_option("--session-db-name",          dest="session_db_name", type="string", default="WebLabSessions",
                                                  help = "Select the name of the sessions database.")

    sess.add_option("--session-db-user",          dest="session_db_user", type="string", default="",
                                                  help = "Select the username to access the sessions database.")

    sess.add_option("--session-db-passwd",        dest="session_db_passwd", type="string", default="",
                                                  help = "Select the password to access the sessions database.")
                                                  
    sess.add_option("--session-redis-db",         dest="session_redis_db", type="int", default=1,
                                                  help = "Select the redis db on which store the sessions.")

    sess.add_option("--session-redis-host",       dest="session_redis_host", type="string", default="localhost",
                                                  help = "Select the redis server host on which store the sessions.")

    sess.add_option("--session-redis-port",       dest="session_redis_port", type="int", default=6379,
                                                  help = "Select the redis server port on which store the sessions.")

    parser.add_option_group(sess)

    dbopt = OptionGroup(parser, "Database options",
                                "WebLab-Deusto uses a relational database for storing users, permissions, etc."
                                "The database must be configured: which engine, database name, user and password." )

    dbopt.add_option("--db-engine",               dest="db_engine",       choices = DATABASE_ENGINES, default = 'sqlite',
                                                  help = "Core database engine to use. Values: %s." % (', '.join(DATABASE_ENGINES)))

    dbopt.add_option("--db-name",                 dest="db_name",         type="string", default="WebLab",
                                                  help = "Core database name.")

    dbopt.add_option("--db-host",                 dest="db_host",         type="string", default="localhost",
                                                  help = "Core database host.")

    dbopt.add_option("--db-user",                 dest="db_user",         type="string", default="weblab",
                                                  help = "Core database username.")

    dbopt.add_option("--db-passwd",               dest="db_passwd",       type="string", default="weblab",
                                                  help = "Core database password.")

    
    parser.add_option_group(dbopt)

    coord = OptionGroup(parser, "Scheduling options",
                                "These options are related to the scheduling system.  "
                                "You must select if you want to use a database or redis, and configure it.")

    coord.add_option("--coordination-engine",    dest="coord_engine",    choices = COORDINATION_ENGINES, default = 'sql',
                                                  help = "Coordination engine used. Values: %s." % (', '.join(COORDINATION_ENGINES)))

    coord.add_option("--coordination-db-engine", dest="coord_db_engine", choices = DATABASE_ENGINES, default = 'sqlite',
                                                  help = "Coordination database engine used, if the coordination is based on a database. Values: %s." % (', '.join(DATABASE_ENGINES)))

    coord.add_option("--coordination-db-name",   dest="coord_db_name",   type="string", default="WebLabCoordination",

                                                  help = "Coordination database name used, if the coordination is based on a database.")

    coord.add_option("--coordination-db-user",   dest="coord_db_user",   type="string", default="",
                                                  help = "Coordination database userused, if the coordination is based on a database.")

    coord.add_option("--coordination-db-passwd", dest="coord_db_passwd",  type="string", default="",
                                                  help = "Coordination database password used, if the coordination is based on a database.")

    coord.add_option("--coordination-db-host",    dest="coord_db_host",    type="string", default="localhost",
                                                  help = "Coordination database host used, if the coordination is based on a database.")

    coord.add_option("--coordination-redis-db",  dest="coord_redis_db",   type="int", default=None,
                                                  help = "Coordination redis DB used, if the coordination is based on redis.")

    coord.add_option("--coordination-redis-passwd",  dest="coord_redis_passwd",   type="string", default=None,
                                                  help = "Coordination redis password used, if the coordination is based on redis.")

    coord.add_option("--coordination-redis-port",  dest="coord_redis_port",   type="int", default=None,
                                                  help = "Coordination redis port used, if the coordination is based on redis.")

    parser.add_option_group(coord)

    options, args = parser.parse_args()

    verbose = options.verbose

    ###########################################
    # 
    # Validate basic options
    # 

    if verbose: print "Validating basic operations...",; sys.stdout.flush()

    if options.coord_engine == 'sql':
        coord_engine = 'sqlalchemy'
    else:
        coord_engine = options.coord_engine

    if options.session_storage == 'sql':
        session_storage = 'sqlalchemy'
    elif options.session_storage == 'memory':
        session_storage = 'Memory'
    else:
        session_storage = options.session_storage

    if options.cores > 1:
        if (coord_engine == 'sqlalchemy' and options.coord_db_engine == 'sqlite') or options.db_engine == 'sqlite':
            sqlite_purpose = ''
            if coord_engine == 'sqlalchemy' and options.coord_db_engine == 'sqlite':
                sqlite_purpose = 'coordination'
            if options.db_engine =='sqlite':
                if sqlite_purpose:
                    sqlite_purpose += ', '
                sqlite_purpose += 'general database'
                
            print >> sys.stderr, "ERROR: sqlite engine selected for %s is incompatible with multiple cores" % sqlite_purpose
            sys.exit(-1)

    if options.cores <= 0:
        print >> sys.stderr, "ERROR: There must be at least one core server."
        sys.exit(-1)

    base_url = options.base_url
    if base_url != '' and not base_url.startswith('/'):
        base_url = '/' + base_url
    if base_url.endswith('/'):
        base_url = base_url[:len(base_url) - 1]
    if options.enable_https:
        protocol = 'https://'
    else:
        protocol = 'http://'
    server_url = protocol + options.server_host + base_url + '/weblab/'



    if options.start_ports < 1 or options.start_ports >= 65535:
        print >> sys.stderr, "ERROR: starting port number must be at least 1"
        sys.exit(-1)

    if options.inline_lab_serv and options.cores > 1:
        print >> sys.stderr, "ERROR: Inline lab server is incompatible with more than one core servers. It would require the lab server to be replicated in all the processes, which does not make sense."
        sys.exit(-1)
        
    if verbose: print "[done]"

    if os.path.exists(directory) and not options.force:
        print >> sys.stderr, "ERROR: Directory %s already exists. Use --force if you want to overwrite the contents." % directory
        sys.exit(-1)

    if os.path.exists(directory):
        if not os.path.isdir(directory):
            print >> sys.stderr, "ERROR: %s is not a directory. Delete it before proceeding." % directory
            sys.exit(-1)
    else:
        try:
            os.mkdir(directory)
        except Exception as e:
            print >> sys.stderr, "ERROR: Could not create directory %s: %s" % (directory, str(e))
            sys.exit(-1)

    ###########################################
    # 
    # Validate database configurations
    # 

    if verbose: print "Start building database configuration"; sys.stdout.flush()

    db_dir = os.path.join(directory, 'db')
    if not os.path.exists(db_dir):
        os.mkdir(db_dir)

    if options.coord_engine == 'redis':
        redis_passwd = options.coord_redis_passwd
        redis_port   = options.coord_redis_port
        redis_db     = options.coord_redis_db
        redis_host   = None
        _test_redis('coordination', verbose, redis_port, redis_passwd, redis_db, redis_host)
    elif options.coord_engine in ('sql', 'sqlalchemy'):
        db_engine  = options.coord_db_engine
        db_host    = options.coord_db_host
        db_name    = options.coord_db_name
        db_user    = options.coord_db_user
        db_passwd  = options.coord_db_passwd
        import weblab.core.coordinator.sql.model as CoordinatorModel
        CoordinatorModel.load()
        _check_database_connection("coordination", CoordinatorModel.Base.metadata, directory, verbose, db_engine, db_host, db_name, db_user, db_passwd)
    else:
        print >> sys.stderr, "The coordination engine %s is not registered" % options.coord_engine
        sys.exit(-1)
        

    if options.session_storage == 'redis':
        redis_passwd = None
        redis_port   = options.session_redis_port
        redis_db     = options.session_redis_db
        redis_host   = options.session_redis_host
        _test_redis('sessions', verbose, redis_port, redis_passwd, redis_db, redis_host)
    elif options.session_storage in ('sql', 'sqlalchemy'):
        db_engine = options.session_db_engine
        db_host   = options.session_db_host
        db_name   = options.session_db_name
        db_user   = options.session_db_user
        db_passwd = options.session_db_passwd
        _check_database_connection("sessions", SessionSqlalchemyData.SessionBase.metadata, directory, verbose, db_engine, db_host, db_name, db_user, db_passwd)
        _check_database_connection("sessions locking", DbLockData.SessionLockBase.metadata, directory, verbose, db_engine, db_host, db_name, db_user, db_passwd)
    elif options.session_storage != 'memory':
        print >> sys.stderr, "The session engine %s is not registered" % options.session_storage
        sys.exit(-1)

    db_engine = options.db_engine
    db_name   = options.db_name
    db_host   = options.db_host
    db_user   = options.db_user
    db_passwd = options.db_passwd
    engine = _check_database_connection("core database", Model.Base.metadata, directory, verbose, db_engine, db_host, db_name, db_user, db_passwd)
    
    if verbose: print "Adding required initial data...",; sys.stdout.flush()
    deploy.insert_required_initial_data(engine)
    if verbose: print "[done]"
    if options.add_test_data:
        if verbose: print "Adding test data...",; sys.stdout.flush()
        deploy.populate_weblab_tests(engine, '1')
        if verbose: print "[done]"
    
    Session = sessionmaker(bind=engine)
    group_name = 'Administrators'
    deploy.add_group(Session, group_name)
    deploy.add_user(Session, options.admin_user, options.admin_password, options.admin_name, options.admin_mail)
    deploy.add_users_to_group(Session, group_name, options.admin_user)

    # dummy@Dummy experiments (local)
    deploy.add_experiment_and_grant_on_group(Session, 'Dummy experiments', options.dummy_name, group_name, 200)

    # external-robot-movement@Robot experiments (federated)
    deploy.add_experiment_and_grant_on_group(Session, 'Robot experiments', 'external-robot-movement', group_name, 200)

    # visir@Visir experiments (optional)
    if options.visir_server:
        deploy.add_experiment_and_grant_on_group(Session, 'Visir experiments', options.visir_experiment_name, group_name, 1800)

    # vm@VM experiments (optional)
    if options.vm_server:
        deploy.add_experiment_and_grant_on_group(Session, 'VM experiments', 'vm', group_name, 200)

    # logic@PIC experiments (optional)
    if options.logic_server:
        deploy.add_experiment_and_grant_on_group(Session, 'PIC experiments', 'ud-logic', group_name, 1800)

    ###########################################
    # 
    # Create voodoo infrastructure
    # 

    if options.inline_lab_serv:
        laboratory_instance_name = 'core_server1' 
    else:
        laboratory_instance_name = 'laboratory'

    if verbose: print "Creating configuration files and directories...",; sys.stdout.flush()

    open(os.path.join(directory, 'configuration.xml'), 'w').write("""<?xml version="1.0" encoding="UTF-8"?>""" 
    """<machines
        xmlns="http://www.weblab.deusto.es/configuration" 
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="global_configuration.xsd"
    >

    <machine>core_machine</machine>"""
    "\n\n</machines>\n")

    machine_dir = os.path.join(directory, 'core_machine')
    if not os.path.exists(machine_dir):
        os.mkdir(machine_dir)

    machine_configuration_xml = ("""<?xml version="1.0" encoding="UTF-8"?>"""
    """<instances
        xmlns="http://www.weblab.deusto.es/configuration" 
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="machine_configuration.xsd"
    >

    <runner file="run.py"/>

    <configuration file="machine_config.py"/>

    """)
    for core_n in range(1, options.cores + 1):
        machine_configuration_xml += "<instance>core_server%s</instance>\n    " % core_n

    machine_configuration_xml += "\n"
    if not options.inline_lab_serv:
        machine_configuration_xml += "    <instance>laboratory</instance>\n\n"
    machine_configuration_xml += "</instances>\n"

    local_experiments = ""
    local_scheduling  = ""


    local_experiments += "            'exp1|%(dummy)s|Dummy experiments'        : 'dummy@dummy',\n" % { 'dummy' : options.dummy_name }
    local_scheduling  += "        'dummy'            : ('PRIORITY_QUEUE', {}),\n"

    if options.visir_server:
        for n in xrange(1, options.visir_slots + 1):
            local_experiments += "            'exp%(n)s|%(name)s|Visir experiments'        : 'visir%(n)s@visir',\n" % { 'n' : n, 'name' : options.visir_experiment_name }
        local_scheduling  += "        'visir'            : ('PRIORITY_QUEUE', {}),\n"

    machine_config_py =("# It must be here to retrieve this information from the dummy\n"
                        "core_universal_identifier       = %(core_universal_identifier)r\n"
                        "core_universal_identifier_human = %(core_universal_identifier_human)r\n"
                        "\n"
                        "db_engine          = %(db_engine)r\n"
                        "db_host            = %(db_host)r\n"
                        "db_database        = %(db_name)r\n"
                        "weblab_db_username = %(db_user)r\n"
                        "weblab_db_password = %(db_password)r\n"
                        "\n"
                        "debug_mode   = True\n"
                        "\n"
                        "#########################\n"
                        "# General configuration #\n"
                        "#########################\n"
                        "\n"
                        "server_hostaddress = %(server_hostaddress)r\n"
                        "server_admin       = %(server_admin)r\n"
                        "\n"
                        "################################\n"
                        "# Admin Notifier configuration #\n"
                        "################################\n"
                        "\n"
                        "mail_notification_enabled = False\n"
                        "\n"
                        "##########################\n"
                        "# Sessions configuration #\n"
                        "##########################\n"
                        "\n"
                        "core_session_type = %(session_storage)r\n"
                        "\n"
                        "%(session_db)ssession_sqlalchemy_engine   = %(session_db_engine)r\n"
                        "%(session_db)ssession_sqlalchemy_host     = %(session_db_host)r\n"
                        "%(session_db)ssession_sqlalchemy_username = %(session_db_user)r\n"
                        "%(session_db)ssession_sqlalchemy_password = %(session_db_passwd)r\n"
                        "\n"
                        "%(session_db)ssession_lock_sqlalchemy_engine   = %(session_db_engine)r\n"
                        "%(session_db)ssession_lock_sqlalchemy_host     = %(session_db_host)r\n"
                        "%(session_db)ssession_lock_sqlalchemy_username = %(session_db_user)r\n"
                        "%(session_db)ssession_lock_sqlalchemy_password = %(session_db_passwd)r\n"
                        "\n"
                        "%(session_redis)ssession_redis_host = %(session_redis_host)r\n"
                        "%(session_redis)ssession_redis_port = %(session_redis_port)r\n"
                        "%(session_redis)ssession_redis_db   = %(session_redis_db)r\n"
                        "\n"
                        "##############################\n"
                        "# Core generic configuration #\n"
                        "##############################\n"
                        "core_store_students_programs      = False\n"
                        "core_store_students_programs_path = 'files_stored'\n"
                        "core_experiment_poll_time         = %(poll_time)r # seconds\n"
                        "\n"
                        "core_server_url = %(server_url)r\n"
                        "\n"
                        "############################\n"
                        "# Scheduling configuration #\n"
                        "############################\n"
                        "\n"
                        "core_coordination_impl = %(core_coordinator_engine)r\n"
                        "\n"
                        "%(coord_redis)scoordinator_redis_db       = %(core_coordinator_redis_db)r\n"
                        "%(coord_redis)scoordinator_redis_password = %(core_coordinator_redis_password)r\n"
                        "%(coord_redis)scoordinator_redis_port     = %(core_coordinator_redis_port)r\n"
                        "\n"
                        "%(coord_db)score_coordinator_db_name      = %(core_coordinator_db_name)r\n"
                        "%(coord_db)score_coordinator_db_engine    = %(core_coordinator_db_engine)r\n"
                        "%(coord_db)score_coordinator_db_host      = %(core_coordinator_db_host)r\n"
                        "%(coord_db)score_coordinator_db_username  = %(core_coordinator_db_username)r\n"
                        "%(coord_db)score_coordinator_db_password  = %(core_coordinator_db_password)r\n"
                        "\n"
                        "core_coordinator_laboratory_servers = {\n"
                        "    'laboratory:%(laboratory_instance_name)s@core_machine' : {\n"
                        "%(local_experiments)s"
                        "        }\n"
                        "}\n"
                        "\n"
                        "core_coordinator_external_servers = {\n"
                        "    'external-robot-movement@Robot experiments'   : [ 'robot_external' ],\n"
                        "}\n"
                        "\n"
                        "weblabdeusto_federation_demo = ('EXTERNAL_WEBLAB_DEUSTO', {\n"
                        "                                    'baseurl' : 'https://www.weblab.deusto.es/weblab/',\n"
                        "                                    'login_baseurl' : 'https://www.weblab.deusto.es/weblab/',\n"
                        "                                    'username' : 'weblabfed',\n"
                        "                                    'password' : 'password',\n"
                        "                                    'experiments_map' : {'external-robot-movement@Robot experiments' : 'robot-movement@Robot experiments'}\n"
                        "                            })\n"
                        "\n"
                        "core_scheduling_systems = {\n"
                        "%(local_scheduling)s"
                        "        'robot_external'   : weblabdeusto_federation_demo,\n"
                        "    }\n"
                        "\n") % {
        'core_universal_identifier'       : str(uuid.uuid4()),
        'core_universal_identifier_human' : options.system_identifier or 'Generic system; not identified',
        'db_engine'                       : options.db_engine,
        'db_host'                         : options.db_host,
        'db_name'                         : options.db_name,
        'db_user'                         : options.db_user,
        'db_password'                     : options.db_passwd,
        'server_hostaddress'              : options.server_host,
        'server_admin'                    : options.admin_mail,
        'server_url'                      : server_url,
        'poll_time'                       : options.poll_time,
        'local_experiments'               : local_experiments,
        'local_scheduling'                : local_scheduling,

        'session_storage'                 : session_storage,

        'session_db_engine'               : options.session_db_engine,
        'session_db_host'                 : options.session_db_host,
        'session_db_name'                 : options.session_db_name,
        'session_db_user'                 : options.session_db_user,
        'session_db_passwd'               : options.session_db_passwd,

        'session_redis_host'              : options.session_redis_host,
        'session_redis_port'              : options.session_redis_port,
        'session_redis_db'                : options.session_redis_db,

        'core_coordinator_engine'         : coord_engine,

        'core_coordinator_redis_db'       : options.coord_redis_db,
        'core_coordinator_redis_password' : options.coord_redis_passwd,
        'core_coordinator_redis_port'     : options.coord_redis_port,

        'core_coordinator_db_username'    : options.coord_db_user,
        'core_coordinator_db_password'    : options.coord_db_passwd,
        'core_coordinator_db_name'        : options.coord_db_name,
        'core_coordinator_db_engine'      : options.coord_db_engine,
        'core_coordinator_db_host'        : options.coord_db_host,

        'laboratory_instance_name'        : laboratory_instance_name,

        'coord_db'                        : '' if options.coord_engine == 'sql' else '# ',
        'coord_redis'                     : '' if options.coord_engine == 'redis' else '# ',
        'session_db'                      : '' if session_storage == 'sqlalchemy' else '# ',
        'session_redis'                   : '' if session_storage == 'redis' else '# ',
    }


    open(os.path.join(machine_dir, 'configuration.xml'), 'w').write(machine_configuration_xml)
    open(os.path.join(machine_dir, 'machine_config.py'), 'w').write(machine_config_py)

    ports = {
        'core'  : [],
        'login' : [],
    }

    current_port = options.start_ports

    latest_core_server_directory = None
    for core_number in range(1, options.cores + 1):
        core_instance_dir = os.path.join(machine_dir, 'core_server%s' % core_number)
        latest_core_server_directory = core_instance_dir
        if not os.path.exists(core_instance_dir):
           os.mkdir(core_instance_dir)
       
        instance_configuration_xml = (
        """<?xml version="1.0" encoding="UTF-8"?>"""
		"""<servers \n"""
		"""    xmlns="http://www.weblab.deusto.es/configuration" \n"""
		"""    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n"""
		"""    xsi:schemaLocation="instance_configuration.xsd"\n"""
		""">\n"""
		"""    <user>weblab</user>\n"""
		"""\n"""
		"""    <server>login</server>\n"""
		"""    <server>core</server>\n""")

        if options.inline_lab_serv:
            instance_configuration_xml += """    <server>laboratory</server>\n"""
            if not options.xmlrpc_experiment:
                instance_configuration_xml += """    <server>experiment</server>\n"""
            if options.visir_server:
                instance_configuration_xml += """    <server>visir</server>\n"""
            
            
        instance_configuration_xml += (
        """\n"""
		"""</servers>\n""")

        open(os.path.join(core_instance_dir, 'configuration.xml'), 'w').write(instance_configuration_xml)

        core_dir = os.path.join(core_instance_dir, 'core')
        if not os.path.exists(core_dir):
            os.mkdir(core_dir)

        login_dir = os.path.join(core_instance_dir, 'login')
        if not os.path.exists(login_dir):
            os.mkdir(login_dir)


        open(os.path.join(login_dir, 'configuration.xml'), 'w').write(
        """<?xml version="1.0" encoding="UTF-8"?>"""
		"""<server\n"""
		"""    xmlns="http://www.weblab.deusto.es/configuration" \n"""
		"""    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n"""
		"""    xsi:schemaLocation="http://www.weblab.deusto.es/configuration server_configuration.xsd"\n"""
		""">\n"""
		"""\n"""
		"""    <configuration file="server_config.py" />\n"""
		"""\n"""
		"""    <type>weblab.data.server_type::Login</type>\n"""
		"""    <methods>weblab.methods::Login</methods>\n"""
		"""\n"""
		"""    <implementation>weblab.login.server.LoginServer</implementation>\n"""
		"""\n"""
		"""    <protocols>\n"""
		"""        <!-- This server supports both Direct calls, as SOAP calls -->\n"""
		"""        <protocol name="Direct">\n"""
		"""            <coordinations>\n"""
		"""                <coordination></coordination>\n"""
		"""            </coordinations>\n"""
		"""            <creation></creation>\n"""
		"""        </protocol>\n"""
		"""    </protocols>\n"""
		"""</server>\n""")

        login_config = {
            'soap'   : current_port + 0,
            'xmlrpc' : current_port + 1,
            'json'   : current_port + 2,
            'web'    : current_port + 3,
            'route'  : 'route%s' % core_number,
        }
        ports['login'].append(login_config)

        core_config = {
            'soap'   : current_port + 4,
            'xmlrpc' : current_port + 5,
            'json'   : current_port + 6,
            'web'    : current_port + 7,
            'admin'  : current_port + 8,
            'route'  : 'route%s' % core_number,
            'clean'  : core_number == 1
        }
        ports['core'].append(core_config)

        core_port = current_port + 9

        current_port += 10

        open(os.path.join(login_dir, 'server_config.py'), 'w').write((
        "login_facade_server_route = %(route)r\n"
		"login_facade_soap_port    = %(soap)r\n"
		"login_facade_xmlrpc_port  = %(xmlrpc)r\n"
		"login_facade_json_port    = %(json)r\n"
		"login_web_facade_port     = %(web)r\n") % login_config)

        open(os.path.join(core_dir, 'configuration.xml'), 'w').write(
        """<?xml version="1.0" encoding="UTF-8"?>"""
		"""<server\n"""
		"""    xmlns="http://www.weblab.deusto.es/configuration" \n"""
		"""    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n"""
		"""    xsi:schemaLocation="http://www.weblab.deusto.es/configuration server_configuration.xsd"\n"""
		""">\n"""
		"""\n"""
		"""    <configuration file="server_config.py" />\n"""
		"""\n"""
		"""    <type>weblab.data.server_type::UserProcessing</type>\n"""
		"""    <methods>weblab.methods::UserProcessing</methods>\n"""
		"""\n"""
		"""    <implementation>weblab.core.server.UserProcessingServer</implementation>\n"""
		"""\n"""
		"""    <!-- <restriction>something else</restriction> -->\n"""
		"""\n"""
		"""    <protocols>\n"""
		"""        <!-- This server supports both Direct calls, as SOAP calls -->\n"""
		"""        <protocol name="Direct">\n"""
		"""            <coordinations>\n"""
		"""                <coordination></coordination>\n"""
		"""            </coordinations>\n"""
		"""            <creation></creation>\n"""
		"""        </protocol>\n"""
		"""        <protocol name="SOAP">\n"""
		"""            <coordinations>\n"""
		"""                <coordination>\n"""
		"""                    <parameter name="address" value="127.0.0.1:%(port)s@NETWORK" />\n"""
		"""                </coordination>\n"""
		"""            </coordinations>\n"""
		"""            <creation>\n"""
		"""                <parameter name="address" value=""     />\n"""
		"""                <parameter name="port"    value="%(port)s" />\n"""
		"""            </creation>\n"""
		"""        </protocol>\n"""
		"""    </protocols>\n"""
		"""</server>\n""" % { 'port' : core_port })

        open(os.path.join(core_dir, 'server_config.py'), 'w').write((
        "core_coordinator_clean   = %(clean)r\n"
        "core_facade_server_route = %(route)r\n"
		"core_facade_soap_port    = %(soap)r\n"
		"core_facade_xmlrpc_port  = %(xmlrpc)r\n"
		"core_facade_json_port    = %(json)r\n"
		"core_web_facade_port     = %(web)r\n"
        "admin_facade_json_port   = %(admin)r\n") % core_config)

    if options.inline_lab_serv:
        lab_instance_dir = latest_core_server_directory
    else:
        lab_instance_dir = os.path.join(machine_dir, 'laboratory')
        if not os.path.exists(lab_instance_dir):
            os.mkdir(lab_instance_dir)

        lab_instance_configuration_xml = (
            """<?xml version="1.0" encoding="UTF-8"?>\n"""
            """<servers \n"""
            """    xmlns="http://www.weblab.deusto.es/configuration" \n"""
            """    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n"""
            """    xsi:schemaLocation="instance_configuration.xsd"\n"""
            """>\n"""
            """    <user>weblab</user>\n"""
            """\n"""
            """    <server>laboratory</server>\n"""
            """    <server>experiment</server>\n"""
            )

        if options.visir_server:
            lab_instance_configuration_xml += """    <server>visir</server>\n"""

        lab_instance_configuration_xml += """</servers>\n"""

        open(os.path.join(lab_instance_dir, 'configuration.xml'), 'w').write( lab_instance_configuration_xml )

    lab_dir = os.path.join(lab_instance_dir, 'laboratory')
    if not os.path.exists(lab_dir):
        os.mkdir(lab_dir)

    open(os.path.join(lab_dir, 'configuration.xml'), 'w').write((
		"""<?xml version="1.0" encoding="UTF-8"?>\n"""
		"""<server\n"""
		"""    xmlns="http://www.weblab.deusto.es/configuration" \n"""
		"""    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n"""
		"""    xsi:schemaLocation="http://www.weblab.deusto.es/configuration server_configuration.xsd"\n"""
		""">\n"""
		"""\n"""
		"""    <configuration file="server_config.py" />\n"""
		"""\n"""
		"""    <type>weblab.data.server_type::Laboratory</type>\n"""
		"""    <methods>weblab.methods::Laboratory</methods>\n"""
		"""\n"""
		"""    <implementation>weblab.lab.server.LaboratoryServer</implementation>\n"""
		"""\n"""
		"""    <protocols>\n"""
		"""        <protocol name="Direct">\n"""
		"""            <coordinations>\n"""
		"""                <coordination></coordination>\n"""
		"""            </coordinations>\n"""
		"""            <creation></creation>\n"""
		"""        </protocol>\n"""
		"""        <protocol name="SOAP">\n"""
		"""            <coordinations>\n"""
		"""                <coordination>\n"""
		"""                    <parameter name="address" value="127.0.0.1:%(port)s@NETWORK" />\n"""
		"""                </coordination>\n"""
		"""            </coordinations>\n"""
		"""            <creation>\n"""
		"""                <parameter name="address" value=""     />\n"""
		"""                <parameter name="port"    value="%(port)s" />\n"""
		"""            </creation>\n"""
		"""        </protocol>\n"""
		"""    </protocols>\n"""
		"""</server>\n""") % {'port' : current_port})
    current_port += 1

    laboratory_config_py = (
		"""##################################\n"""
		"""# Laboratory Server configuration #\n"""
		"""##################################\n"""
		"""\n"""
		"""laboratory_assigned_experiments = {\n"""
    )

    laboratory_config_py += (
		"""        'exp1:%(dummy)s@Dummy experiments' : {\n"""
		"""                'coord_address' : 'experiment:%(instance)s@core_machine',\n"""
		"""                'checkers' : ()\n"""
		"""            },\n"""
    ) % { 'instance' : laboratory_instance_name, 'dummy' : options.dummy_name }

    if options.visir_server:
        for n in xrange(1, options.visir_slots + 1):
            laboratory_config_py += (
                """        'exp%(n)s:%(visir_name)s@Visir experiments' : {\n"""
                """                'coord_address' : 'visir:%(instance)s@core_machine',\n"""
                """                'checkers' : ()\n"""
                """            },\n"""
            ) % { 'instance' : laboratory_instance_name, 'visir_name' : options.visir_experiment_name, 'n' : n }       

    laboratory_config_py += """    }\n"""

    open(os.path.join(lab_dir, 'server_config.py'), 'w').write(laboratory_config_py)

    experiment_dir = os.path.join(lab_instance_dir, 'experiment')
    if not os.path.exists(experiment_dir):
        os.mkdir(experiment_dir)

    open(os.path.join(experiment_dir, 'configuration.xml'), 'w').write((
		"""<?xml version="1.0" encoding="UTF-8"?>\n"""
		"""<server\n"""
		"""    xmlns="http://www.weblab.deusto.es/configuration" \n"""
		"""    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n"""
		"""    xsi:schemaLocation="http://www.weblab.deusto.es/configuration server_configuration.xsd"\n"""
		""">\n"""
		"""\n"""
		"""    <configuration file="server_config.py" />\n"""
		"""\n"""
		"""    <type>weblab.data.server_type::Experiment</type>\n"""
		"""    <methods>weblab.methods::Experiment</methods>\n"""
		"""\n"""
		"""    <implementation>experiments.dummy.DummyExperiment</implementation>\n"""
		"""\n"""
		"""    <restriction>%(dummy)s@Dummy experiments</restriction>\n"""
		"""\n"""
		"""    <protocols>\n"""
		"""        <protocol name="Direct">\n"""
		"""            <coordinations>\n"""
		"""                <coordination></coordination>\n"""
		"""            </coordinations>\n"""
		"""            <creation></creation>\n"""
		"""        </protocol>\n"""
		"""    </protocols>\n"""
		"""</server>\n""") % { 'dummy' : options.dummy_name } )

    open(os.path.join(experiment_dir, 'server_config.py'), 'w').write(
        "dummy_verbose = True\n")


    if options.visir_server:
        visir_dir = os.path.join(lab_instance_dir, 'visir')
        if not os.path.exists(visir_dir):
            os.mkdir(visir_dir)

        open(os.path.join(visir_dir, 'configuration.xml'), 'w').write((
            """<?xml version="1.0" encoding="UTF-8"?>\n"""
            """<server\n"""
            """    xmlns="http://www.weblab.deusto.es/configuration" \n"""
            """    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n"""
            """    xsi:schemaLocation="http://www.weblab.deusto.es/configuration server_configuration.xsd"\n"""
            """>\n"""
            """\n"""
            """    <configuration file="server_config.py" />\n"""
            """\n"""
            """    <type>weblab.data.server_type::Experiment</type>\n"""
            """    <methods>weblab.methods::Experiment</methods>\n"""
            """\n"""
            """    <implementation>experiments.visir.VisirExperiment</implementation>\n"""
            """\n"""
            """    <protocols>\n"""
            """        <protocol name="Direct">\n"""
            """            <coordinations>\n"""
            """                <coordination></coordination>\n"""
            """            </coordinations>\n"""
            """            <creation></creation>\n"""
            """        </protocol>\n"""
            """    </protocols>\n"""
            """</server>\n"""))

        if options.visir_measurement_server is not None:
            if not ':' in options.visir_measurement_server or options.visir_measurement_server.startswith(('http://','https://')) or '/' in options.visir_measurement_server.split(':')[1]:
                print >> sys.stderr, "VISIR measurement server invalid format. Expected: server:port Change the configuration file"
            visir_measurement_server = options.visir_measurement_server
        else:
            result = urllib2.urlparse.urlparse(options.visir_base_url)
            visir_measurement_server = result.netloc.split(':')[0] + ':8080'

        if options.visir_use_php:
            visir_php = ("""vt_use_visir_php = True\n"""
            """vt_base_url = "%(visir_base_url)s"\n"""
            """vt_login_url = "%(visir_base_url)sindex.php?sel=login_check"\n"""
            """vt_login_email = "%(visir_login)s"\n"""
            """vt_login_password = "%(visir_password)s"\n""" % {
                'visir_base_url' : options.visir_base_url,
                'visir_login'    : options.visir_login,
                'visir_password' : options.visir_password,
            })
        else:
            visir_php = """vt_use_visir_php = False\n"""
           

        open(os.path.join(visir_dir, 'server_config.py'), 'w').write((
            """vt_measure_server_addr = "%(visir_measurement_server)s"\n"""
            """vt_measure_server_target = "/measureserver"\n"""
            """\n"""
            + visir_php +
            """\n"""
            """# You can also specify a directory where different circuits will be loaded, such as:\n"""
            """#\n"""
            """# vt_circuits_dir = "/home/weblab/Dropbox/VISIR-Circuits/"\n"""
            """#\n"""
            """#\n"""
            """# You can also define your own library.xml in this configuration file by uncommenting:\n"""
            """#\n"""
            """# vt_library = \"\"\"\n"""
            """# <!DOCTYPE components PUBLIC "-//Open labs//DTD COMPONENTS 1.0//EN" "http://openlabs.bth.se/DTDs/components-1.0.dtd">\n"""
            """# <components>\n"""
            """#    <component type="R" value="1.5M" pins="2">\n"""
            """#        <rotations>\n"""
            """#            <rotation ox="-27" oy ="-6" image="r_1.5M.png" rot="0">\n"""
            """#                <pins><pin x="-26" y="0" /><pin x="26"  y="0" /></pins>\n"""
            """#            </rotation>\n"""
            """#            <rotation ox="-7" oy ="-27" image="r_1.5M.png" rot="90">\n"""
            """#                <pins><pin x="0" y="-26" /><pin x="0" y="26" /></pins>\n"""
            """#            </rotation>\n"""
            """#        </rotations>\n"""
            """#    </component>\n"""
            """#    <!-- More components -->\n"""
            """#\n"""
            """# </components>\n"""
            """# \"\"\"\n"""
            """#\n"""
            """\n""") % {'visir_measurement_server' : visir_measurement_server })



    files_stored_dir = os.path.join(directory, 'files_stored')
    if not os.path.exists(files_stored_dir):
        os.mkdir(files_stored_dir)

    if verbose: print "[done]"

    ###########################################
    # 
    # Generate logs directory and config
    # 

    if verbose: print "Creating logs directories and configuration files...",; sys.stdout.flush()

    logs_dir = os.path.join(directory, 'logs')
    if not os.path.exists(logs_dir):
        os.mkdir(logs_dir)

    logs_config_dir = os.path.join(logs_dir, 'config')
    if not os.path.exists(logs_config_dir):
        os.mkdir(logs_config_dir)

    # TODO: use the generation module instead of hardcoding it here

    server_names = []
    for core_number in range(1, options.cores + 1):
        server_names.append('server%s' % core_number)

    if not options.inline_lab_serv:
        server_names.append('laboratory')
    if options.xmlrpc_experiment or not options.inline_lab_serv:
        server_names.append('experiment')

    for server_name in server_names:
        logging_file = (
            """# \n"""
            """# logging module file generated by generate_logging_file.py\n"""
            """# \n"""
            """# You should change the script configuration instead of\n"""
            """# this file directly.\n"""
            """# \n"""
            """# Call it like: \n"""
            """#   Generator( \n"""
            """#       {'weblab.core.coordinator': ('WARNING', False), 'weblab.login': ('INFO', True), 'weblab.login.database': ('WARNING', False), 'weblab.lab': ('INFO', True), 'weblab.facade': ('INFO', True), 'weblab.core.facade': ('WARNING', False), 'weblab': ('WARNING', True), 'weblab.core.database': ('WARNING', False), 'weblab.login.facade': ('WARNING', False), 'voodoo': ('WARNING', True), 'weblab.core': ('INFO', True)}, \n"""
            """#       logs/sample_, \n"""
            """#       logs.txt, \n"""
            """#       52428800, \n"""
            """#       1099511627776, \n"""
            """#       False  \n"""
            """#   )\n"""
            """# \n"""
            """\n"""
            """[loggers]\n"""
            """keys=root,weblab_core_coordinator,weblab_login,weblab_login_database,weblab.lab,weblab_facade,weblab_core_facade,weblab,weblab_core_database,weblab_login_facade,voodoo,weblab_core\n"""
            """\n"""
            """[handlers]\n"""
            """keys=root_handler,weblab_login_handler,weblab.lab_handler,weblab_facade_handler,weblab_handler,voodoo_handler,weblab_core_handler\n"""
            """\n"""
            """[formatters]\n"""
            """keys=simpleFormatter\n"""
            """\n"""
            """[logger_root]\n"""
            """level=NOTSET\n"""
            """handlers=root_handler\n"""
            """propagate=0\n"""
            """parent=\n"""
            """channel=\n"""
            """\n"""
            """[logger_voodoo]\n"""
            """level=WARNING\n"""
            """handlers=voodoo_handler\n"""
            """qualname=voodoo\n"""
            """propagate=0\n"""
            """parent=root\n"""
            """channel=voodoo\n"""
            """\n"""
            """[logger_weblab]\n"""
            """level=WARNING\n"""
            """handlers=weblab_handler\n"""
            """qualname=weblab\n"""
            """propagate=0\n"""
            """parent=root\n"""
            """channel=weblab\n"""
            """\n"""
            """[logger_weblab_facade]\n"""
            """level=INFO\n"""
            """handlers=weblab_facade_handler\n"""
            """qualname=weblab.facade\n"""
            """propagate=0\n"""
            """parent=weblab\n"""
            """channel=weblab_facade\n"""
            """\n"""
            """[logger_weblab.lab]\n"""
            """level=INFO\n"""
            """handlers=weblab.lab_handler\n"""
            """qualname=weblab.lab\n"""
            """propagate=0\n"""
            """parent=weblab\n"""
            """channel=weblab.lab\n"""
            """\n"""
            """[logger_weblab_core]\n"""
            """level=INFO\n"""
            """handlers=weblab_core_handler\n"""
            """qualname=weblab.core\n"""
            """propagate=0\n"""
            """parent=weblab\n"""
            """channel=weblab_core\n"""
            """\n"""
            """[logger_weblab_core_facade]\n"""
            """level=WARNING\n"""
            """handlers=weblab_core_handler\n"""
            """qualname=weblab.core.facade\n"""
            """propagate=1\n"""
            """parent=weblab_core\n"""
            """channel=weblab_core_facade\n"""
            """\n"""
            """[logger_weblab_core_coordinator]\n"""
            """level=WARNING\n"""
            """handlers=weblab_core_handler\n"""
            """qualname=weblab.core.coordinator\n"""
            """propagate=1\n"""
            """parent=weblab_core\n"""
            """channel=weblab_core_coordinator\n"""
            """\n"""
            """[logger_weblab_core_database]\n"""
            """level=WARNING\n"""
            """handlers=weblab_core_handler\n"""
            """qualname=weblab.core.database\n"""
            """propagate=1\n"""
            """parent=weblab_core\n"""
            """channel=weblab_core_database\n"""
            """\n"""
            """[logger_weblab_login]\n"""
            """level=INFO\n"""
            """handlers=weblab_login_handler\n"""
            """qualname=weblab.login\n"""
            """propagate=0\n"""
            """parent=weblab\n"""
            """channel=weblab_login\n"""
            """\n"""
            """[logger_weblab_login_facade]\n"""
            """level=WARNING\n"""
            """handlers=weblab_login_handler\n"""
            """qualname=weblab.login.facade\n"""
            """propagate=1\n"""
            """parent=weblab_login\n"""
            """channel=weblab_login_facade\n"""
            """\n"""
            """[logger_weblab_login_database]\n"""
            """level=WARNING\n"""
            """handlers=weblab_login_handler\n"""
            """qualname=weblab.login.database\n"""
            """propagate=1\n"""
            """parent=weblab_login\n"""
            """channel=weblab_login_database\n"""
            """\n"""
            """[handler_root_handler]\n"""
            """class=handlers.RotatingFileHandler\n"""
            """formatter=simpleFormatter\n"""
            """args=('logs/sample__root_logs.%(server_number)s.txt','a',52428800,20971)\n"""
            """\n"""
            """[handler_weblab_login_handler]\n"""
            """class=handlers.RotatingFileHandler\n"""
            """formatter=simpleFormatter\n"""
            """args=('logs/sample__weblab_login_logs.%(server_number)s.txt','a',52428800,20971)\n"""
            """\n"""
            """[handler_weblab.lab_handler]\n"""
            """class=handlers.RotatingFileHandler\n"""
            """formatter=simpleFormatter\n"""
            """args=('logs/sample__weblab.lab_logs.%(server_number)s.txt','a',52428800,20971)\n"""
            """\n"""
            """[handler_weblab_facade_handler]\n"""
            """class=handlers.RotatingFileHandler\n"""
            """formatter=simpleFormatter\n"""
            """args=('logs/sample__weblab_facade_logs.%(server_number)s.txt','a',52428800,20971)\n"""
            """\n"""
            """[handler_weblab_handler]\n"""
            """class=handlers.RotatingFileHandler\n"""
            """formatter=simpleFormatter\n"""
            """args=('logs/sample__weblab_logs.%(server_number)s.txt','a',52428800,20971)\n"""
            """\n"""
            """[handler_voodoo_handler]\n"""
            """class=handlers.RotatingFileHandler\n"""
            """formatter=simpleFormatter\n"""
            """args=('logs/sample__voodoo_logs.%(server_number)s.txt','a',52428800,20971)\n"""
            """\n"""
            """[handler_weblab_core_handler]\n"""
            """class=handlers.RotatingFileHandler\n"""
            """formatter=simpleFormatter\n"""
            """args=('logs/sample__weblab_core_logs.%(server_number)s.txt','a',52428800,20971)\n"""
            """\n"""
            """[formatter_simpleFormatter]\n"""
            """format=%(asctime)s - %(name)s - %(levelname)s - %(message)s\n"""
            """datefmt=\n"""
            """class=logging.Formatter\n""") % {
                'server_number' : server_name,
                'asctime'       : '%(asctime)s',
                'name'          : '%(name)s',
                'levelname'     : '%(levelname)s',
                'message'       : '%(message)s',
            }
        open(os.path.join(logs_config_dir, 'logging.configuration.%s.txt' % server_name), 'w').write(logging_file)


    if verbose: print "[done]"

    ###########################################
    # 
    # Generate launch script
    # 

    if verbose: print "Creating launch file...",; sys.stdout.flush()

    launch_script = (
        """#!/usr/bin/env python\n"""
        """#-*-*- encoding: utf-8 -*-*-\n"""
        """try:\n"""
        """    import signal\n"""
        """    \n"""
        """    import voodoo.gen.loader.Launcher as Launcher\n"""
        """    \n"""
        """    def before_shutdown():\n"""
        """        print "Stopping servers..."\n"""
        """    \n"""
        """    launcher = Launcher.MachineLauncher(\n"""
        """                '.',\n"""
        """                'core_machine',\n"""
        """                (\n"""
        """                    Launcher.SignalWait(signal.SIGTERM),\n"""
        """                    Launcher.SignalWait(signal.SIGINT),\n"""
        """                    Launcher.RawInputWait("Press <enter> or send a sigterm or a sigint to finish\\n")\n"""
        """                ),\n"""
        """                {\n""")
    for core_number in range(1, options.cores + 1):
        launch_script += """                    "core_server%s"     : "logs%sconfig%slogging.configuration.server%s.txt",\n""" % (core_number, os.sep, os.sep, core_number)
    
    if not options.inline_lab_serv:
        launch_script += ("""                    "laboratory" : "logs%sconfig%slogging.configuration.laboratory.txt",\n""" % (os.sep, os.sep))
    launch_script += (
        """                },\n"""
        """                before_shutdown,\n"""
        """                (\n"""
        """                     Launcher.FileNotifier("_file_notifier", "server started"),\n"""
        """                ),\n"""
        """                pid_file = 'weblab.pid',\n""")
    waiting_port = current_port
    current_port += 1
    launch_script += """                waiting_port = %r,\n""" % waiting_port
    launch_script += """                debugger_ports = { \n"""
    debugging_ports = []
    for core_number in range(1, options.cores + 1):
        debugging_core_port = current_port
        debugging_ports.append(debugging_core_port)
        current_port += 1
        launch_script += """                     'core_server%s' : %s, \n""" % (core_number, debugging_core_port)
    launch_script += ("""                }\n"""
        """            )\n"""
        """    launcher.launch()\n"""
        """except:\n"""
        """    import traceback\n"""
        """    traceback.print_exc()\n"""
        """    raise\n"""
    )
    
    debugging_config = "# SERVERS is used by the WebLab Monitor to gather information from these ports.\n# If you open them, you'll see a Python shell.\n"
    debugging_config += "SERVERS = [\n"
    for debugging_port in debugging_ports:
        debugging_config += "    ('127.0.0.1','%s'),\n" % debugging_port
    debugging_config += "]\n\n"
    debugging_config += "BASE_URL = %r\n\n" % base_url
    debugging_config += "# PORTS is used by the WebLab Bot to know what\n# ports it should wait prior to start using\n# the simulated clients.\n"
    debugging_config += "PORTS = {\n"
    for protocol in ('soap','xmlrpc','json'):
        protocol_configuration = []
        for core_configuration in ports['core']:
            core_protocol_configuration = core_configuration.get(protocol, None)
            if core_protocol_configuration:
                protocol_configuration.append(core_protocol_configuration)
        debugging_config += """    %r : %r, \n""" % (protocol, protocol_configuration)

        protocol_configuration = []
        for login_configuration in ports['login']:
            login_protocol_configuration = login_configuration.get(protocol, None)
            if login_protocol_configuration:
                protocol_configuration.append(login_protocol_configuration)
        debugging_config += """    %r : %r, \n""" % (protocol + '_login', protocol_configuration)
    debugging_config += "}\n"


        


    open(os.path.join(directory, 'run.py'), 'w').write( launch_script )
    open(os.path.join(directory, 'debugging.py'), 'w').write( debugging_config )
    os.chmod(os.path.join(directory, 'run.py'), stat.S_IRWXU)

    if verbose: print "[done]"

    ###########################################
    # 
    # Generate apache configuration file
    # 

    if verbose: print "Creating apache configuration files...",; sys.stdout.flush()

    apache_dir = os.path.join(directory, 'apache')
    if not os.path.exists(apache_dir):
        os.mkdir(apache_dir)

    client_dir = os.path.join(directory, 'client')
    if not os.path.exists(client_dir):
        os.mkdir(client_dir)

    client_images_dir = os.path.join(client_dir, 'images')
    if not os.path.exists(client_images_dir):
        os.mkdir(client_images_dir)

    apache_conf = (
        "\n"
        """# Apache redirects the regular paths to the particular directories \n"""
        """RedirectMatch ^%(root)s$ %(root)s/weblab/client\n"""
        """RedirectMatch ^%(root)s/$ %(root)s/weblab/client\n"""
        """RedirectMatch ^%(root)s/weblab/$ %(root)s/weblab/client\n"""
        """RedirectMatch ^%(root)s/weblab/client/$ %(root)s/weblab/client/index.html\n"""
        """\n"""
        """Alias %(root)s/weblab/client/weblabclientlab/configuration.js      %(directory)s/client/configuration.js\n"""
        """Alias %(root)s/weblab/client/weblabclientadmin/configuration.js %(directory)s/client/configuration.js\n"""
        """\n"""
        """Alias %(root)s/weblab/client/weblabclientlab//img%(root-img)s/         %(directory)s/client/images/\n"""
        """Alias %(root)s/weblab/client/weblabclientadmin//img%(root-img)s/    %(directory)s/client/images/\n"""
        """\n"""        
        """Alias %(root)s/weblab/client                                    %(war_path)s\n"""
        """Alias %(root)s/weblab/                                          %(webserver_path)s\n"""
        """\n"""
        """<Directory "%(directory)s">\n"""
        """        Options Indexes\n"""
        """        Order allow,deny\n"""
        """        Allow from all\n"""
        """</Directory>\n"""
        """\n"""        
        """<Directory "%(war_path)s">\n"""
        """        Options Indexes\n"""
        """        Order allow,deny\n"""
        """        Allow from all\n"""
        """</Directory>\n"""
        """\n"""        
        """<Directory "%(webserver_path)s">\n"""
        """        Options Indexes\n"""
        """        Order allow,deny\n"""
        """        Allow from all\n"""
        """</Directory>\n"""
        """\n"""        
        """# Apache redirects the requests retrieved to the particular server, using a stickysession if the sessions are based on memory\n"""
        """ProxyVia On\n"""
        """\n"""
        """ProxyPass                       %(root)s/weblab/soap/                 balancer://%(root-no-slash)s_weblab_cluster_soap/           stickysession=weblabsessionid lbmethod=bybusyness\n"""
        """ProxyPassReverse                %(root)s/weblab/soap/                 balancer://%(root-no-slash)s_weblab_cluster_soap/           stickysession=weblabsessionid\n"""
        """ProxyPass                       %(root)s/weblab/json/                 balancer://%(root-no-slash)s_weblab_cluster_json/           stickysession=weblabsessionid lbmethod=bybusyness\n"""
        """ProxyPassReverse                %(root)s/weblab/json/                 balancer://%(root-no-slash)s_weblab_cluster_json/           stickysession=weblabsessionid\n"""
        """ProxyPass                       %(root)s/weblab/xmlrpc/               balancer://%(root-no-slash)s_weblab_cluster_xmlrpc/         stickysession=weblabsessionid lbmethod=bybusyness\n"""
        """ProxyPassReverse                %(root)s/weblab/xmlrpc/               balancer://%(root-no-slash)s_weblab_cluster_xmlrpc/         stickysession=weblabsessionid\n"""
        """ProxyPass                       %(root)s/weblab/web/                  balancer://%(root-no-slash)s_weblab_cluster_web/            stickysession=weblabsessionid lbmethod=bybusyness\n"""
        """ProxyPassReverse                %(root)s/weblab/web/                  balancer://%(root-no-slash)s_weblab_cluster_web/            stickysession=weblabsessionid\n"""
        """ProxyPass                       %(root)s/weblab/login/soap/           balancer://%(root-no-slash)s_weblab_cluster_login_soap/     stickysession=loginweblabsessionid lbmethod=bybusyness\n"""
        """ProxyPassReverse                %(root)s/weblab/login/soap/           balancer://%(root-no-slash)s_weblab_cluster_login_soap/     stickysession=loginweblabsessionid\n"""
        """ProxyPass                       %(root)s/weblab/login/json/           balancer://%(root-no-slash)s_weblab_cluster_login_json/     stickysession=loginweblabsessionid lbmethod=bybusyness\n"""
        """ProxyPassReverse                %(root)s/weblab/login/json/           balancer://%(root-no-slash)s_weblab_cluster_login_json/     stickysession=loginweblabsessionid\n"""
        """ProxyPass                       %(root)s/weblab/login/xmlrpc/         balancer://%(root-no-slash)s_weblab_cluster_login_xmlrpc/   stickysession=loginweblabsessionid lbmethod=bybusyness\n"""
        """ProxyPassReverse                %(root)s/weblab/login/xmlrpc/         balancer://%(root-no-slash)s_weblab_cluster_login_xmlrpc/   stickysession=loginweblabsessionid\n"""
        """ProxyPass                       %(root)s/weblab/login/web/            balancer://%(root-no-slash)s_weblab_cluster_login_web/      stickysession=loginweblabsessionid lbmethod=bybusyness\n"""
        """ProxyPassReverse                %(root)s/weblab/login/web/            balancer://%(root-no-slash)s_weblab_cluster_login_web/      stickysession=loginweblabsessionid\n"""
        """ProxyPass                       %(root)s/weblab/administration/       balancer://%(root-no-slash)s_weblab_cluster_administration/ stickysession=weblabsessionid lbmethod=bybusyness\n"""
        """ProxyPassReverse                %(root)s/weblab/administration/       balancer://%(root-no-slash)s_weblab_cluster_administration/ stickysession=weblabsessionid\n"""
        "\n")


    apache_conf += "\n"
    apache_conf += "<Proxy balancer://%(root-no-slash)s_weblab_cluster_soap>\n"
    
    for core_configuration in ports['core']:
        apache_conf += "    BalancerMember http://localhost:%(port)s/weblab/soap route=%(route)s\n" % {
            'port' : core_configuration['soap'], 'route' : core_configuration['route'], 'root' : '%(root)s' }
    
    apache_conf += "</Proxy>\n"
    apache_conf += "\n"
    
    apache_conf += """<Proxy balancer://%(root-no-slash)s_weblab_cluster_json>\n"""

    for core_configuration in ports['core']:
        apache_conf += """    BalancerMember http://localhost:%(port)s/weblab/json route=%(route)s\n""" % {
            'port' : core_configuration['json'], 'route' : core_configuration['route'], 'root' : '%(root)s' }

    apache_conf += """</Proxy>\n"""
    apache_conf += """\n"""

    apache_conf += """<Proxy balancer://%(root-no-slash)s_weblab_cluster_xmlrpc>\n"""

    for core_configuration in ports['core']:
        apache_conf += """    BalancerMember http://localhost:%(port)s/weblab/xmlrpc route=%(route)s\n""" % {
            'port' : core_configuration['xmlrpc'], 'route' : core_configuration['route'], 'root' : '%(root)s' }

    apache_conf += """</Proxy>\n"""
    apache_conf += """\n"""
    apache_conf += """<Proxy balancer://%(root-no-slash)s_weblab_cluster_web>\n"""

    for core_configuration in ports['core']:
        apache_conf += """    BalancerMember http://localhost:%(port)s/weblab/web route=%(route)s\n""" % {
            'port' : core_configuration['web'], 'route' : core_configuration['route'], 'root' : '%(root)s' }

    apache_conf += """</Proxy>\n"""
    apache_conf += """\n"""
    apache_conf += """<Proxy balancer://%(root-no-slash)s_weblab_cluster_administration>\n"""

    for core_configuration in ports['core']:
        apache_conf += """    BalancerMember http://localhost:%(port)s/weblab/administration/ route=%(route)s\n""" % {
            'port' : core_configuration['admin'], 'route' : core_configuration['route'], 'root' : '%(root)s' }

    apache_conf += """</Proxy>\n"""
    apache_conf += """\n"""

    apache_conf += """<Proxy balancer://%(root-no-slash)s_weblab_cluster_login_soap>\n"""

    for core_configuration in ports['login']:
        apache_conf += """    BalancerMember http://localhost:%(port)s/weblab/login/soap route=%(route)s \n""" % {
            'port' : core_configuration['soap'], 'route' : core_configuration['route'], 'root' : '%(root)s' }

    apache_conf += """</Proxy>\n"""
    apache_conf += """\n"""
    apache_conf += """<Proxy balancer://%(root-no-slash)s_weblab_cluster_login_json>\n"""

    for core_configuration in ports['login']:
        apache_conf += """    BalancerMember http://localhost:%(port)s/weblab/login/json route=%(route)s\n""" % {
            'port' : core_configuration['json'], 'route' : core_configuration['route'], 'root' : '%(root)s' }

    apache_conf += """</Proxy>\n"""
    apache_conf += """\n"""
    apache_conf += """<Proxy balancer://%(root-no-slash)s_weblab_cluster_login_xmlrpc>\n"""

    for core_configuration in ports['login']:
        apache_conf += """    BalancerMember http://localhost:%(port)s/weblab/login/xmlrpc route=%(route)s\n""" % {
            'port' : core_configuration['xmlrpc'], 'route' : core_configuration['route'], 'root' : '%(root)s' }

    apache_conf += """</Proxy>\n"""
    apache_conf += """\n"""
    apache_conf += """<Proxy balancer://%(root-no-slash)s_weblab_cluster_login_web>\n"""

    for core_configuration in ports['login']:
        apache_conf += """    BalancerMember http://localhost:%(port)s/weblab/login/web route=%(route)s\n""" % {
            'port' : core_configuration['web'], 'route' : core_configuration['route'], 'root' : '%(root)s' }

    apache_conf += """</Proxy>\n"""
    apache_conf += """\n"""
    
    if base_url in ('','/'):
        apache_root    = ''
        apache_img_dir = '/sample' 
    else:
        apache_root    = base_url
        apache_img_dir = base_url

    apache_root_without_slash = apache_root[1:] if apache_root.startswith('/') else apache_root

    apache_conf = apache_conf % { 'root' : apache_root,  'root-no-slash' : apache_root_without_slash,
                'root-img' : apache_img_dir, 'directory' : os.path.abspath(directory).replace('\\','/'), 
                'war_path' : data_filename('war').replace('\\','/'), 'webserver_path' : data_filename('webserver').replace('\\','/') }

    apache_conf_path = os.path.join(apache_dir, 'apache_weblab_generic.conf')

    open(apache_conf_path, 'w').write( apache_conf )

    if sys.platform.find('win') == 0:
        apache_windows_conf = """# At least in Debian based distributions as Debian itself
        # or Ubuntu, this can be done with the a2enmod command:
        # 
        #   root@plunder:~# a2enmod proxy
        #   root@plunder:~# a2enmod proxy_balancer_module
        #   root@plunder:~# a2enmod proxy_http_module
        #   root@plunder:~# /etc/init.d/apache2 force-reload
        #  
        # However, in Microsoft Windows or other distributions, this 
        # might become slightly more difficult. To make it easy, you
        # can uncomment the following lines in Microsoft Windows if
        # using XAMPP as installer, or if you are under Mac OS X:
        # 
        <IfModule !mod_proxy.c>
            LoadModule proxy_module modules/mod_proxy.so
        </IfModule>
        <IfModule !mod_proxy_balancer.c>
            LoadModule proxy_balancer_module modules/mod_proxy_balancer.so
        </IfModule>
        <IfModule !mod_proxy_http.c>
            LoadModule proxy_http_module modules/mod_proxy_http.so
        </IfModule>
        <IfModule !mod_lbmethod_byrequests>
        LoadModule lbmethod_byrequests_module modules/mod_lbmethod_byrequests.so
        </IfModule>
        <IfModule !mod_lbmethod_bybusyness>
        LoadModule lbmethod_bybusyness_module modules/mod_lbmethod_bybusyness.so
        </IfModule>
        <IfModule !mod_slotmem_shm>
        LoadModule slotmem_shm_module modules/mod_slotmem_shm.so
        </IfModule>
        """
        apache_windows_conf_path = os.path.join(apache_dir, 'apache_weblab_windows.conf')
        open(apache_windows_conf_path, 'w').write( apache_windows_conf )

    if verbose: print "[done]"

    ###########################################
    # 
    #     Generate configuration.js files
    #
    configuration_js = {}

    lines = open(data_filename(os.path.join('war','weblabclientlab','configuration.js'))).readlines()
    new_lines = uncomment_json(lines)
    configuration_js_data = json.loads(''.join(new_lines))
    configuration_js['experiments']                    = configuration_js_data['experiments']

    dummy_list = list(configuration_js['experiments']['dummy'])
    found      = False
    for element in dummy_list:
        if element['experiment.name'] == options.dummy_name:
            found = True
    if not found:
        dummy_list.append({'experiment.name' : options.dummy_name, 'experiment.category' : 'Dummy experiments'})
    configuration_js['experiments']['dummy']           = dummy_list
    configuration_js['development']                    = False
    configuration_js['demo.available']                 = False
    configuration_js['sound.enabled']                  = False
    configuration_js['admin.email']                    = 'weblab@deusto.es'
    configuration_js['experiments.default_picture']    = '/img/experiments/default.jpg'
    # TODO: Add a sample image
    if base_url != '' and base_url != '/':
        configuration_js['base.location']                  = base_url
        configuration_js['host.entity.image.login']        = '/img%s%s.png'        % (base_url, base_url) 
        configuration_js['host.entity.image']              = '/img%s%s.png'        % (base_url, base_url)
        configuration_js['host.entity.image.mobile']       = '/img%s%s-mobile.png' % (base_url, base_url)
    else:
        configuration_js['base.location']                  = ''
        configuration_js['host.entity.image.login']        = '/img/sample/sample.png'
        configuration_js['host.entity.image']              = '/img/sample/sample.png'
        configuration_js['host.entity.image.mobile']       = '/img/sample/sample-mobile.png'

    configuration_js['host.entity.link']               = options.entity_link
    configuration_js['facebook.like.box.visible']      = False
    configuration_js['create.account.visible']         = False
    json.dump(configuration_js, open(os.path.join(client_dir, 'configuration.js'), 'w'), indent = True)

    print
    print "Congratulations!"
    print "WebLab-Deusto system created"
    print 
    apache_httpd_path = r'your apache httpd.conf ( typically /etc/apache2/httpd.conf or C:\xampp\apache\conf\ )'
    if os.path.exists("/etc/apache2/httpd.conf"):
        apache_httpd_path = '/etc/apache2/httpd.conf'
    elif os.path.exists('C:\\xampp\\apache\\conf\\httpd.conf'):
        apache_httpd_path = 'C:\\xampp\\apache\\conf\\httpd.conf'

    print r"Append the following to", apache_httpd_path
    print 
    print "    Include \"%s\"" % os.path.abspath(apache_conf_path).replace('\\','/')
    if sys.platform.find('win') == 0:
        print "    Include \"%s\"" % os.path.abspath(apache_windows_conf_path).replace('\\','/')
    else:
        print
        print "And enable the modules proxy proxy_balancer proxy_http."
        print "For instance, in Ubuntu you can run: "
        print 
        print "    $ sudo a2enmod proxy proxy_balancer proxy_http"
    print 
    print "Then restart apache and execute:"
    print 
    print "     %s start %s" % (os.path.basename(sys.argv[0]), directory)
    print 
    print "to start the WebLab-Deusto system. From that point, you'll be able to access: "
    print
    print "     %s " % server_url
    print
    print "And log in as '%s' using '%s' as password." % (options.admin_user, options.admin_password)
    print 
    print "You should also configure the images directory with two images called:"
    print 
    print "     %s.png and %s-mobile.png " % (base_url or 'sample', base_url or 'sample')
    print 
    print "You can also add users, permissions, etc. from the admin CLI by typing:"
    print
    print "    %s admin %s" % (os.path.basename(sys.argv[0]), directory)
    print 
    print "Enjoy!"
    print 

#########################################################################################
# 
# 
# 
#      W E B L A B     R U N N I N G      A N D     S T O P P I N G 
# 
# 
# 

def weblab_start(directory):
    parser = OptionParser(usage="%prog create DIR [options]")

    parser.add_option("-m", "--machine",           dest="machine", default=None, metavar="MACHINE",
                                                   help = "If there is more than one machine in the configuration, which one should be started.")
    parser.add_option("-l", "--list-machines",     dest="list_machines", action='store_true', default=False, 
                                                   help = "List machines.")

    parser.add_option("-s", "--script",            dest="script", default=None, metavar="SCRIPT",
                                                   help = "If the runner option is not available, which script should be used.")

    options, args = parser.parse_args()

    old_cwd = os.getcwd()
    os.chdir(directory)
    try:
        if options.script: # If a script is provided, ignore the rest
            if os.path.exists(options.script):
                execfile(options.script)
            elif os.path.exists(os.path.join(old_cwd, options.script)):
                execfile(os.path.join(old_cwd, options.script))
            else:
                print >> sys.stderr, "Provided script %s does not exist" % options.script
                sys.exit(-1)
        else:
            parser = GlobalParser()
            global_configuration = parser.parse('.')
            if options.list_machines:
                for machine in global_configuration.machines:
                    print ' - %s' % machine
                sys.exit(0)

            machine_name = options.machine
            if machine_name is None: 
                if len(global_configuration.machines) == 1:
                    machine_name = global_configuration.machines.keys()[0]
                else:
                    print >> sys.stderr, "System has more than one machine (see -l). Please detail which machine you want to start with the -m option."
                    sys.exit(-1)

            if not machine_name in global_configuration.machines:
                print >> sys.stderr, "Error: %s machine does not exist. Use -l to see the list of existing machines." % machine_name
                sys.exit(-1)

            machine_config = global_configuration.machines[machine_name]
            if machine_config.runner is None:
                if os.path.exists('run.py'):
                    execfile('run.py')
                else:
                    print >> sys.stderr, "No runner was specified, and run.py was not available. Please the -s argument to specify the script or add the <runner file='run.py'/> option in %s." % machine_name
                    sys.exit(-1)
            else:
                if os.path.exists(machine_config.runner):
                    execfile(machine_config.runner)
                else:
                    print >> sys.stderr, "Misconfigured system. Machine %s points to %s which does not exist." % (machine_name, os.path.abspath(machine_config.runner))
                    sys.exit(-1)
    finally:
        os.chdir(old_cwd)

def weblab_stop(directory):
    if sys.platform.lower().startswith('win'):
        print >> sys.stderr, "Stopping not yet supported. Try killing the process from the Task Manager or simply press enter"
        sys.exit(-1)
    os.kill(int(open(os.path.join(directory, 'weblab.pid')).read()), signal.SIGTERM)

#########################################################################################
# 
# 
# 
#      W E B L A B     A D M I N
# 
# 
# 

def weblab_admin(directory):
    old_cwd = os.getcwd()
    os.chdir(directory)
    try:
        parser = GlobalParser()
        global_configuration = parser.parse('.')
        configuration_files = []
        configuration_files.extend(global_configuration.configurations)
        for machine in global_configuration.machines:
            machine_config = global_configuration.machines[machine]
            configuration_files.extend(machine_config.configurations)

            for instance in machine_config.instances:
                instance_config = machine_config.instances[instance]
                configuration_files.extend(instance_config.configurations)

                for server in instance_config.servers:
                    server_config = instance_config.servers[server]
                    configuration_files.extend(server_config.configurations)

        Controller(configuration_files)
    finally:
        os.chdir(old_cwd)

#########################################################################################
# 
# 
# 
#      W E B L A B     M O N I T O R I N G
# 
# 
# 

def weblab_monitor(directory):
    new_globals = {}
    new_locals  = {}
    execfile(os.path.join(directory, 'debugging.py'), new_globals, new_locals)

    SERVERS = new_locals['SERVERS']

    def list_users(experiment):
        information, ups_orphans, coordinator_orphans = wl.list_users(experiment)

        print "%15s\t%25s\t%11s\t%11s" % ("LOGIN","STATUS","UPS_SESSID","RESERV_ID")
        for login, status, ups_session_id, reservation_id in information:
            if isinstance(status, WebLabQueueStatus.WaitingQueueStatus) or isinstance(status, WebLabQueueStatus.WaitingInstancesQueueStatus):
                status_str = "%s: %s" % (status.status, status.position)
            else:
                status_str = status.status

            if options.full_info:
                    print "%15s\t%25s\t%8s\t%8s" % (login, status_str, ups_session_id, reservation_id)
            else:
                    print "%15s\t%25s\t%8s...\t%8s..." % (login, status_str, ups_session_id[:8], reservation_id)

        if len(ups_orphans) > 0:
            print 
            print "UPS ORPHANS"
            for ups_info in ups_orphans:
                print ups_info

        if len(coordinator_orphans) > 0:
            print 
            print "COORDINATOR ORPHANS"
            for coordinator_info in coordinator_orphans:
                print coordinator_info

    def show_server(number):
        if number > 0:
            print 
        print "Server %s" % (number + 1)

    option_parser = OptionParser()

    option_parser.add_option( "-e", "--list-experiments",
                              action="store_true",
                              dest="list_experiments",
                              help="Lists all the available experiments" )
                            
    option_parser.add_option( "-u", "--list-users",
                              dest="list_users",
                              nargs=1,
                              default=None,
                              help="Lists all users using a certain experiment (format: experiment@category)" )

    option_parser.add_option( "-a", "--list-experiment-users",
                              action="store_true",
                              dest="list_experiment_users",
                              help="Lists all users using any experiment" )

    option_parser.add_option( "-l", "--list-all-users",
                              action="store_true",
                              dest="list_all_users",
                              help="Lists all connected users" )

    option_parser.add_option( "-f", "--full-info",
                      action="store_true",
                              dest="full_info",
                              help="Shows full information (full session ids instead of only the first characteres)" )
                             
    option_parser.add_option( "-k", "--kick-session",
                              dest="kick_session",
                              nargs=1,
                              default=None,
                              help="Given the full UPS Session ID, it kicks out a user from the system" )

    option_parser.add_option( "-b", "--kick-user",
                              dest="kick_user",
                              nargs=1,
                              default=None,
                              help="Given the user login, it kicks him out from the system" )

    options, _ = option_parser.parse_args()

    for num, server in enumerate(SERVERS):
        wl = WebLabMonitor(server)

        if options.list_experiments:
            print wl.list_experiments(),

        elif options.list_experiment_users:
            show_server(num)
            experiments = wl.list_experiments()
            if experiments != '':
                for experiment in experiments.split('\n')[:-1]:
                    print 
                    print "%s..." % experiment
                    print 
                    list_users(experiment)
            
        elif options.list_users != None:
            show_server(num)
            list_users(options.list_users)
            
        elif options.list_all_users:
            show_server(num)
            all_users = wl.list_all_users()

            print "%15s\t%11s\t%17s\t%24s" % ("LOGIN","UPS_SESSID","FULL_NAME","LATEST TIMESTAMP")

            for ups_session_id, user_information, latest_timestamp in all_users:
                latest = time.asctime(time.localtime(latest_timestamp))
                if options.full_info:
                    print "%15s\t%11s\t%17s\t%24s" % (user_information.login, ups_session_id.id, user_information.full_name, latest)
                else:
                    if len(user_information.full_name) <= 14:
                        print "%15s\t%8s...\t%s\t%24s" % (user_information.login, ups_session_id.id[:8], user_information.full_name, latest)
                    else:
                        print "%15s\t%8s...\t%14s...\t%24s" % (user_information.login, ups_session_id.id[:8], user_information.full_name[:14], latest)
            
        elif options.kick_session != None:
            show_server(num)
            wl.kick_session(options.kick_session)

        elif options.kick_user != None:
            show_server(num)
            wl.kick_user(options.kick_user)
           
        else:
            option_parser.print_help()
            break

#########################################################################################
# 
# 
# 
#      W E B L A B     R E B U I L D     D A T A B A S E
# 
# 
# 


def weblab_rebuild_db(directory):
    print >> sys.stderr, "Rebuilding database is not yet implemented"
    sys.exit(-1)

