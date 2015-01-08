#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2012 onwards University of Deusto
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#
# This software consists of contributions made by many individuals,
# listed below:
#
# Author: Pablo Orduña <pablo@ordunya.com>
#         Luis Rodriguez <luis.rodriguez@opendeusto.es>
# 

import os
import re
import sys
import abc
import json

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import weblab.db.model as model
from weblab.admin.cli.controller import DbConfiguration
from weblab.admin.script.utils import run_with_config

from weblab.db.upgrade import DbUpgrader

#########################################################################################
# 
# 
# 
#      W E B L A B     U P G R A D E
# 
# 
# 


def weblab_upgrade(directory):
    def on_dir(directory, configuration_files):
        if not check_updated(directory, configuration_files):
            upgrade(directory, configuration_files)
        else:
            print "Already upgraded to the latest version."

    run_with_config(directory, on_dir)

def check_updated(directory, configuration_files):
    for upgrader_kls in Upgrader.upgraders():
        upgrader = upgrader_kls(directory, configuration_files)
        if not upgrader.check_updated():
            return False

    return True

def upgrade(directory, configuration_files):
    print "The system is outdated. Please, make a backup of the current deployment (copy the directory and make a backup of the database)."
    if raw_input("Do you want to continue with the upgrade? (y/N) ") == 'y':
        for upgrader_kls in Upgrader.upgraders():
            upgrader = upgrader_kls(directory, configuration_files)
            if not upgrader.check_updated():
                upgrader.upgrade()
    else:
        print "Upgrade aborted."

class Upgrader(object):

    __metaclass__ = abc.ABCMeta

    def __init__(self, directory, configuration_files):
        self.directory = directory
        self.configuration_files = configuration_files

    @abc.abstractmethod
    def check_updated(self):
        """ True => it's upgraded. False => needs to be upgraded """
        return True

    @abc.abstractmethod
    def upgrade(self):
        pass

    @classmethod
    def upgraders(kls):
        """ Recursive class method to obtain all the final child subclasses """
        upgraders = []
        for upgrader in Upgrader.__subclasses__():
            if len(upgrader.__subclasses__()) == 0:
                upgraders.append(upgrader)
            else:
                for child_upgrader in upgrader.upgraders():
                    upgraders.append(child_upgrader)
        return upgraders

class DatabaseUpgrader(Upgrader):

    def __init__(self, directory, configuration_files):
        db_conf = DbConfiguration(configuration_files)
        regular_url = db_conf.build_url()
        coord_url   = db_conf.build_coord_url()
        self.upgrader = DbUpgrader(regular_url, coord_url)

    def check_updated(self):
        return self.upgrader.check_updated()

    def upgrade(self):
        print "Upgrading database."
        sys.stdout.flush()
        self.upgrader.upgrade()
        print "Upgrade completed."

class ConfigurationExperiments2db(Upgrader):
    def __init__(self, directory, configuration_files):
        self.db_conf = DbConfiguration(configuration_files)
        self.config_js = os.path.join(directory, 'client', 'configuration.js')
        if os.path.exists(self.config_js):
            self.config = json.load(open(self.config_js))
        else:
            self.config = {}
       
    def check_updated(self):
        # In the future, this file will not exist.
        if not os.path.exists(self.config_js):
            return True
        
        # But if it exists and it has an 'experiments' section, it has 
        # not been upgraded.
        if 'experiments' in self.config:
            return False

        return True

    def upgrade(self):
        connection_url = self.db_conf.build_url()
        engine = create_engine(connection_url, echo=False, convert_unicode=True)

        Session = sessionmaker(bind=engine)
        session = Session()
        try:
            for client_id, experiments in self.config['experiments'].iteritems():
                for experiment in experiments:
                    experiment_category = experiment['experiment.category']
                    experiment_name = experiment['experiment.name']
                    
                    db_category = session.query(model.DbExperimentCategory).filter_by(name = experiment_category).first()
                    if not db_category:
                        # Experiment not in database
                        continue

                    db_experiment = session.query(model.DbExperiment).filter_by(category = db_category, name = experiment_name).first()
                    if not db_experiment:
                        # Experiment not in database
                        continue

                    db_experiment.client = client_id
                    for key in experiment:
                        if key in ('experiment.category','experiment.name'):
                            # Already processed
                            continue
                        
                        existing_parameter = session.query(model.DbExperimentClientParameter).filter_by(parameter_name = key, experiment = db_experiment).first()
                        if existing_parameter:
                            # Already processed in the past
                            continue

                        value = experiment[key]
                        if isinstance(value, basestring):
                            param_type = 'string'
                        elif isinstance(value, bool):
                            param_type = 'bool'
                        elif isinstance(value, float):
                            param_type = 'floating'
                        elif isinstance(value, int):
                            param_type = 'integer'
                        else:
                            print "Error: invalid parameter type %s for key %s of experiment %s" % (type(value), key, experiment_name)
                            continue

                        param = model.DbExperimentClientParameter(db_experiment, key, param_type, unicode(experiment[key]))
                        session.add(param)
            session.commit()
        finally:
            session.close()

        self.config.pop('experiments')
        json.dump(self.config, open(self.config_js, 'w'), indent = 4)

class RemoveOldWebAndLoginPorts(Upgrader):
    def __init__(self, directory, configuration_files):
        self.directory = directory
        self.configuration_files = configuration_files

    def check_updated(self):
        """ True => it's upgraded. False => needs to be upgraded """
        login_config_files = [ f for f in self.configuration_files if '/login/' in f ]
        for fname in login_config_files:
            with open(fname) as f:
                for line in f:
                    if line.startswith(('login_facade_json_port', 'login_facade_web_port')):
                        return False
        return True

    def upgrade(self):
        login_config_files = [ f for f in self.configuration_files if '/login/' in f ]
        login_replacements = {
            # 'login_server_config' : 'core_server_config'
        }
        login_directories = [] # To be removed

        for fname in login_config_files:
            login_dir = os.path.dirname(fname)
            parent_dir = os.path.dirname(login_dir)
            core_dir = os.path.join(parent_dir, 'core')
            found = False
            if os.path.exists(core_dir):
                core_config = os.path.join(core_dir, 'server_config.py')
                if os.path.exists(core_config) and core_config in self.configuration_files:
                    login_replacements[fname] = core_config
                    login_directories.append(login_dir)
                    found = True
            if not found:
                print >> sys.stderr, "Error finding the core server directory for login server: %s" % fname
                return

        # Here we know what are the directories to be removed and what are the configuration_files to be removed
        if not os.path.exists('debugging.py'):
            print >> sys.stderr, "debugging.py file not found in the root directory of the deployment"
            return
        
        debugging_ports = {}
        execfile('debugging.py', debugging_ports)
        
        simple_server = {}
        simple_server_config_filename = os.path.join('httpd','simple_server_config.py')
        execfile(simple_server_config_filename, simple_server)
        KEYS = ('/weblab/json/', '/weblab/login/json/', '/weblab/login/web/', '/weblab/web/', '/weblab/administration')

        ports_per_path = {}
        for key, value in dict(simple_server['PATHS']).iteritems():
            for url_key in KEYS:
                if url_key in key:
                    ports = [ port_str[1:-1] for port_str in re.findall(":[0-9]+/", value) ]
                    ports_per_path[url_key] = ports
        
        for url_key in KEYS:
            if url_key not in ports_per_path:
                print >> sys.stderr, "Error: Key %s expected and not found in %s" % (url_key, os.path.abspath(simple_server_config_filename))
                return

        # final_ports = [ '10000', '10010', '10020' ]
        final_ports = ports_per_path.pop('/weblab/json/')
        # replacement_ports = [ ('10001', '10002', '10003', '10004'), ('10011', '10012', '10013', '10014'), ('10021', '10022', '10023', '10024') ]
        replacement_ports = zip(*ports_per_path.values())
        # replacement_pairs = [ ('10000', ('10001', '10002', '10003', '10004')), ... ]
        replacement_pairs = zip(final_ports, replacement_ports)
        # replacement_pairs = { '10000' : ('10001', '10002', '10003') ... }
        replacement_pairs = dict(replacement_pairs)
        
        # 
        # Now everything is ready.
        # 
        # We need to migrate:
        #  1. debugging.py, removing the 'json_login' line.
        #  2. httpd/apache_weblab_generic.conf, using replacement_pairs to change old ports by new single port.
        #  3. httpd/simple_server_config.py, doing the same as in step 2.
        #  4. For each login configuration file:
        #  4.1 Take the login/server_config.py and put it in the corresponding core/server_config.py
        #  4.2 In the core/server_config.py, remove the old variables (and create the new one)
        #  4.3 Remove the login/server_config.py, login/configuration.xml and try to remove the directory
        #  4.4 Remove the <server>login</server> from parent/configuration.xml
        # 
        # Profit!
        # 

        print "Start migrating old login and web ports"


        # Step 1: debugging.py

        print " - Upgrading debugging.py"

        new_contents = ''.join([ line for line in open('debugging.py') if 'json_login' not in line ])
        open('debugging.py', 'w').write(new_contents)

        # Steps 2 & 3: apache_weblab_generic.conf & simple_server_config.py

        print " - Upgrading httpd files"

        apache_weblab_generic_conf_filename = os.path.join('httpd', 'apache_weblab_generic.conf')
        apache_weblab_generic_conf = open(apache_weblab_generic_conf_filename).read()

        simple_server_config = open(simple_server_config_filename).read()

        # TODO: Verify there is no issue with trailing / in administration/ in Apache
        simple_server_config = simple_server_config.replace('weblab/json,', 'weblab/json/,')
        simple_server_config = simple_server_config.replace('weblab/web,', 'weblab/web/,')
        simple_server_config = simple_server_config.replace('weblab/login/json,', 'weblab/login/json/,')
        simple_server_config = simple_server_config.replace('weblab/login/web,', 'weblab/login/web/,')

        for new_port, old_ports in replacement_pairs.iteritems():
            for old_port in old_ports:
                apache_weblab_generic_conf = apache_weblab_generic_conf.replace(':%s/' % old_port, ':%s/' % new_port)
                simple_server_config = simple_server_config.replace(':%s/' % old_port, ':%s/' % new_port)

        open(apache_weblab_generic_conf_filename, 'w').write(apache_weblab_generic_conf)
        open(simple_server_config_filename, 'w').write(simple_server_config)
        
        # Step 4: login files
        for login_replacement, core_replacement in login_replacements.iteritems():
            print " - Upgrading %s" % os.path.abspath(core_replacement)
            # Steps 4.1 & 4.2: Copy configuration to core/server_config.py & clean
            lines = []
            TO_REMOVE = (
                        'login_facade_server_route', 
                        'login_facade_json_port', 
                        'login_web_facade_port', 

                        'core_web_facade_port', 
                        'admin_facade_json_port', 
                        'login_facade_json_bind', 
                        
                        'login_facade_xmlrpc_bind',
                        'login_facade_xmlrpc_port',
                        'login_facade_soap_bind', 
                        'login_facade_soap_port', 
                        'login_facade_soap_service_name', 

                        'core_facade_soap_bind',
                        'core_facade_soap_port',
                        'core_facade_soap_service_name',

                        'core_facade_xmlrpc_bind', 
                        'core_facade_xmlrpc_port',

                        'core_facade_json_bind'
                )

            for line in open(core_replacement):
                variable_name = line.split(' ')[0].split('=')[0]
                if not variable_name.startswith(TO_REMOVE):
                    if variable_name == 'core_facade_json_port':
                        line = line.replace('core_facade_json_port', 'core_facade_port')

                    lines.append(line)

            lines.append('\n')

            for line in open(login_replacement):
                variable_name = line.split(' ')[0].split('=')[0]
                if not variable_name.startswith(TO_REMOVE):
                    lines.append(line)

            contents = ''.join(lines)
            open(core_replacement, 'w').write(contents)

            # Step 4.3: Remove login
            os.remove(login_replacement)
            login_dir = os.path.dirname(login_replacement)
            configuration_xml_filename = os.path.join(login_dir, 'configuration.xml')
            if os.path.exists(configuration_xml_filename):
                os.remove(configuration_xml_filename)

            if len(os.listdir(login_dir)) == 0:
                os.rmdir(login_dir)

            # Step 4.4: Remove <server>login</server>
            parent_dir = os.path.dirname(login_dir)
            parent_config_xml = os.path.join(parent_dir, 'configuration.xml')
            if os.path.exists(parent_config_xml):
                contents = open(parent_config_xml).read()
                contents = contents.replace('<server>login</server>', '')
                open(parent_config_xml, 'w').write(contents)

        print "Old login and web ports migration completed."

