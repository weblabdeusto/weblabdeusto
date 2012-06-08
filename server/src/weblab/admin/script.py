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
import uuid
from optparse import OptionParser, OptionGroup

COMMANDS = {
    'create'     : 'Create a new weblab instance', 
    'rebuild-db' : 'Rebuild the database of the weblab instance', 
    'start'      : 'Start an existing weblab instance', 
    'stop'       : 'Stop an existing weblab instance',
    'admin'      : 'Adminstrate a weblab instance',
    'monitor'    : 'Monitor the current use of a weblab instance',
}

def weblab():
    if len(sys.argv) in (1, 2) or sys.argv[1] not in COMMANDS:
        command_list = ""
        for command, help_text in COMMANDS.items():
            command_list += "\t%s\t\t%s\n" % (command, help_text)
        print >> sys.stderr, "Usage: %s option DIR [option arguments]\n\n%s\n" % (sys.argv[0], command_list)
        sys.exit(0)
    main_command = sys.argv[1]
    if main_command == 'create':
        weblab_create(sys.argv[2])
    else:
        print >>sys.stderr, "Command %s not yet implemented" % sys.argv[1]

COORDINATION_ENGINES = ['sql',   'redis'  ]
DATABASE_ENGINES     = ['mysql', 'sqlite' ]
SESSION_ENGINES      = ['sql',   'redis', 'memory']

def weblab_create(directory):
    parser = OptionParser(usage="%prog create DIR [options]")

    parser.add_option("--cores",                  dest="cores",           type="int",    default=1,
                                                  help = "Number of core servers.")

    parser.add_option("--start-port",             dest="start_ports",     type="int",    default=10000,
                                                  help = "From which port start counting.")

    parser.add_option("-i", "--system-identifier",dest="system_identifier", type="string", default="",
                                                  help = "A human readable identifier for this system.")

    parser.add_option("--admin-mail",             dest="admin_mail",     type="string",    default="",
                                                  help = "E-mail address of the system administrator.")

    parser.add_option("--server-url",             dest="server_url",     type="string",    default="http://localhost/weblab/",
                                                  help = "Final public application address. Example: http://weblab.domain/weblab/.")

    parser.add_option("--server-host",            dest="server_host",     type="string",    default="localhost",
                                                  help = "Host address of this machine. Example: weblab.domain.")

    parser.add_option("--inline-lab-server",      dest="inline_lab_serv", action="store_true", default=False,
                                                  help = "Laboratory server included in the same process as the core server. " 
                                                         "Only available if a single core is used." )

    parser.add_option("-f", "--force",            dest="force", action="store_true", default=False,
                                                   help = "Overwrite the contents even if the directory already existed.")

    sess = OptionGroup(parser, "Session options",
                                "WebLab-Deusto may store sessions in a database, in memory or in redis."
                                "Choose one system and configure it." )

    sess.add_option("--session-storage",          dest="session_storage", choices = SESSION_ENGINES, default='sql',
                                                  help = "Session storage used. Values: %s." % (', '.join(SESSION_ENGINES)) )

    sess.add_option("--session-db-name",          dest="session_db_name", type="string", default="WebLabSessions",
                                                  help = "Select the name of the sessions database.")

    sess.add_option("--session-db-user",          dest="session_db_user", type="string", default="",
                                                  help = "Select the username to access the sessions database.")

    sess.add_option("--session-db-passwd",        dest="session_db_passwd", type="string", default="",
                                                  help = "Select the password to access the sessions database.")
                                                  
    sess.add_option("--session-redis-db",         dest="session_redis_db", type="int", default=1,
                                                  help = "Select the redis db on which store the sessions.")

    parser.add_option_group(sess)

    dbopt = OptionGroup(parser, "Database options",
                                "WebLab-Deusto uses a relational database for storing users, permissions, etc."
                                "The database must be configured: which engine, database name, user and password." )

    dbopt.add_option("--db-engine",               dest="db_engine",       choices = DATABASE_ENGINES, default = 'sqlite',
                                                  help = "Core database engine to use. Values: %s." % (', '.join(DATABASE_ENGINES)))

    dbopt.add_option("--db-name",                 dest="db_name",         type="string", default="WebLabTests",
                                                  help = "Core database name.")

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

    coord.add_option("--coordination-db-passwd", dest="coord_db_passwd",   type="string", default="",
                                                  help = "Coordination database password used, if the coordination is based on a database.")

    coord.add_option("--coordination-redis-db",  dest="coord_redis_db",   type="int", default=0,
                                                  help = "Coordination redis DB used, if the coordination is based on redis.")

    parser.add_option_group(coord)

    (options, args) = parser.parse_args()

    if options.cores <= 0:
        print >> sys.stderr, "ERROR: There must be at least one core server."
        sys.exit(-1)

    if options.start_ports < 1 or options.start_ports >= 65535:
        print >> sys.stderr, "ERROR: starting port number must be at least 1"
        sys.exit(-1)

    if options.inline_lab_serv and options.cores > 1:
        print >> sys.stderr, "ERROR: Inline lab server is incompatible with more than one core servers. It would require the lab server, which does not make sense."
        sys.exit(-1)
        

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

    <configuration file="machine_config.py"/>

    """)
    for core_n in range(1, options.cores + 1):
        machine_configuration_xml += "<instance>core_server%s</instance>\n    " % core_n

    machine_configuration_xml += ("\n"
    "    <instance>laboratory</instance>\n\n"
    "</instances>\n"
    )

    machine_config_py =("# It must be here to retrieve this information from the dummy\n"
                        "core_universal_identifier       = %(core_universal_identifier)r\n"
                        "core_universal_identifier_human = %(core_universal_identifier_human)r\n"
                        "\n"
                        "db_database = %(db_name)r\n"
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
                        "\n"
                        "##############################\n"
                        "# Core generic configuration #\n"
                        "##############################\n"
                        "core_store_students_programs      = False\n"
                        "core_store_students_programs_path = 'files_stored'\n"
                        "core_experiment_poll_time         = 350 # seconds\n"
                        "\n"
                        "core_server_url = ''\n"
                        "\n"
                        "############################\n"
                        "# Scheduling configuration #\n"
                        "############################\n"
                        "\n"
                        "%(coord_db)score_coordinator_db_username = %(core_coordinator_db_username)r\n"
                        "%(coord_db)score_coordinator_db_password = %(core_coordinator_db_password)r\n"
                        "\n"
                        "core_coordinator_laboratory_servers = {\n"
                        "    'laboratory:laboratory@core_machine' : {\n"
                        "            'exp1|dummy1|Dummy experiments'        : 'dummy@dummy',\n"
                        "        }\n"
                        "}\n"
                        "\n"
                        "core_coordinator_external_servers = {\n"
                        "    'external-robot-movement@Robot experiments'   : [ 'robot_external' ],\n"
                        "}\n"
                        "\n"
                        "_provider1_scheduling_config = ('EXTERNAL_WEBLAB_DEUSTO', {\n"
                        "                                    'baseurl' : 'https://www.weblab.deusto.es/weblab/',\n"
                        "                                    'login_baseurl' : 'https://www.weblab.deusto.es/weblab/',\n"
                        "                                    'username' : 'weblabfed',\n"
                        "                                    'password' : 'password',\n"
                        "                                    'experiments_map' : {'external-robot-movement@Robot experiments' : 'robot-movement@Robot experiments'}\n"
                        "                            })\n"
                        "\n"
                        "core_scheduling_systems = {\n"
                        "        'dummy'            : ('PRIORITY_QUEUE', {}),\n"
                        "        'robot_external'   : weblabdeusto_federation_demo,\n"
                        "    }\n"
                        "\n") % {
        'core_universal_identifier'       : uuid.uuid4(),
        'core_universal_identifier_human' : options.system_identifier or 'Generic system; not identified',
        'db_name'                         : options.db_name,
        'db_user'                         : options.db_user,
        'db_password'                     : options.db_passwd,
        'server_hostaddress'              : options.server_host,
        'server_admin'                    : options.admin_mail,
        'core_coordinator_db_username'    : options.coord_db_user,
        'core_coordinator_db_password'    : options.coord_db_passwd,
        'coord_db'                        : '' if options.coord_engine == 'sql' else '#',
    }


    # TODO: provide the rest of fields: sessions, coordination...

    open(os.path.join(machine_dir, 'configuration.xml'), 'w').write(machine_configuration_xml)
    open(os.path.join(machine_dir, 'machine_config.py'), 'w').write(machine_config_py)

    ports = {
        'core'  : [],
        'login' : [],
    }

    current_port = options.start_ports

    for core_number in range(1, options.cores + 1):
        core_instance_dir = os.path.join(machine_dir, 'core_server%s' % core_number)
        if not os.path.exists(core_instance_dir):
           os.mkdir(core_instance_dir)
       
        open(os.path.join(core_instance_dir, 'configuration.xml'), 'w').write("""<?xml version="1.0" encoding="UTF-8"?>"""
		"""<servers \n"""
		"""    xmlns="http://www.weblab.deusto.es/configuration" \n"""
		"""    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n"""
		"""    xsi:schemaLocation="instance_configuration.xsd"\n"""
		""">\n"""
		"""    <user>weblab</user>\n"""
		"""\n"""
		"""    <server>login</server>\n"""
		"""    <server>core</server>\n"""
        """\n"""
		"""</servers>\n""")

        core_dir = os.path.join(core_instance_dir, 'core')
        if not os.path.exists(core_dir):
            os.mkdir(core_dir)

        login_dir = os.path.join(core_instance_dir, 'login')
        if not os.path.exists(login_dir):
            os.mkdir(login_dir)


        open(os.path.join(login_dir, 'configuration.xml'), 'w').write("""?xml version="1.0" encoding="UTF-8"?>"""
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
        }

        core_port = current_port + 9

        current_port += 10

        open(os.path.join(login_dir, 'server_config.py'), 'w').write((
        "login_facade_server_route = %(route)r\n"
		"login_facade_soap_port    = %(soap)r\n"
		"login_facade_xmlrpc_port  = %(xmlrpc)r\n"
		"login_facade_json_port    = %(json)r\n"
		"login_web_facade_port     = %(web)r\n") % login_config)

        # TODO: ports
        open(os.path.join(core_dir, 'configuration.xml'), 'w').write("""?xml version="1.0" encoding="UTF-8"?>"""
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
        "core_facade_server_route = %(route)r\n"
		"core_facade_soap_port    = %(soap)r\n"
		"core_facade_xmlrpc_port  = %(xmlrpc)r\n"
		"core_facade_json_port    = %(json)r\n"
		"core_web_facade_port     = %(web)r\n"
        "admin_facade_json_port   = %(admin)r\n") % core_config)

    lab_instance_dir = os.path.join(machine_dir, 'laboratory')
    if not os.path.exists(lab_instance_dir):
        os.mkdir(lab_instance_dir)

    open(os.path.join(lab_instance_dir, 'configuration.xml'), 'w').write((
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
		"""</servers>\n"""
    ))

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
		"""    <restriction>ud-dummy@Dummy experiments</restriction>\n"""
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

    print options.cores, options.db_engine, options.inline_lab_serv
    
