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
from __future__ import print_function, unicode_literals

from __future__ import print_function, unicode_literals

import os
import re
import subprocess
import sys
import abc
import json
from collections import OrderedDict

try:
    import argparse
except ImportError:
    print("argparse not found. You must upgrade Python to Python 2.7 or higher", file=sys.stderr)
    sys.exit(-1)

import six
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import weblab.db.model as model
from weblab.admin.script.dbutils import DbConfiguration
from weblab.admin.script.utils import run_with_config, ordered_dump
from weblab.admin.script.httpd_config_generate import httpd_config_generate

import xml.dom.minidom as minidom

from weblab.db.upgrade import DbUpgrader

import re

#########################################################################################
# 
# 
# 
#      W E B L A B     U P G R A D E
# 
# 
# 


def weblab_upgrade(directory):
    def on_dir(directory, configuration_files, configuration_values):
        original_argv = sys.argv
        sys.argv = [sys.argv[0]] + sys.argv[3:]
        parser = argparse.ArgumentParser(description="WebLab upgrade tool.")
        parser.add_argument('-y', '--yes', dest='yes', action='store_true', help='Say yes to everything')
        sys_args = parser.parse_args()
        sys.argv = original_argv

        if not check_updated(directory, configuration_files, configuration_values, sys_args):
            upgrade(directory, configuration_files, configuration_values, sys_args)
        else:
            print("Already upgraded to the latest version.")

    run_with_config(directory, on_dir)


def check_updated(directory, configuration_files, configuration_values, sys_args=None):
    updated = True
    for upgrader_kls in Upgrader.upgraders():
        upgrader = upgrader_kls(directory, configuration_files, configuration_values, sys_args)
        if not upgrader.check_updated():
            updated = False
            # Don't break / return here. We want to display all the settings

    return updated


def ask_yes(message, sys_args):
    if sys_args and sys_args.yes:
        print(message)
        print("  > Answered yes since --yes is provided")
        return True

    return raw_input("%s (y/N) " % message) == 'y'


def upgrade(directory, configuration_files, configuration_values, sys_args=None):
    print(
        "The system is outdated. Please, make a backup of the current deployment (copy the directory and make a backup of the database).")
    if ask_yes("Do you want to continue with the upgrade?", sys_args):
        for upgrader_kls in Upgrader.upgraders():
            upgrader = upgrader_kls(directory, configuration_files, configuration_values, sys_args)
            if not upgrader.check_updated():
                upgrader.upgrade()
    else:
        print("Upgrade aborted.")


class Upgrader(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, directory, configuration_files, configuration_values, sys_args):
        self.directory = directory
        self.configuration_files = configuration_files
        self.configuration_values = configuration_values
        self.sys_args = sys_args

    @classmethod
    def get_priority(self):
        """ The higher, the later it will be applied """
        return 0

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

        upgraders_priority = [(upgrader, upgrader.get_priority()) for upgrader in upgraders]
        upgraders_priority.sort(lambda (u1, p1), (u2, p2): cmp(p1, p2))
        return [upgrader for (upgrader, priority) in upgraders_priority]


class DatabaseUpgrader(Upgrader):
    def __init__(self, directory, configuration_files, configuration_values, *args, **kwargs):
        super(DatabaseUpgrader, self).__init__(directory, configuration_files, configuration_values, *args, **kwargs)
        db_conf = DbConfiguration(configuration_files, configuration_values)
        regular_url = db_conf.build_url()
        coord_url = db_conf.build_coord_url()
        self.upgrader = DbUpgrader(regular_url, coord_url)

    def check_updated(self):
        updated = self.upgrader.check_updated()
        if not updated:
            print(" - The database requires some changes and it is going to be upgraded.")
        return updated

    def upgrade(self):
        print("Upgrading database.")
        sys.stdout.flush()
        self.upgrader.upgrade()
        print("Upgrade completed.")


class JSClientUpgrader(Upgrader):
    def __init__(self, directory, configuration_files, configuration_values, *args, **kwargs):
        super(JSClientUpgrader, self).__init__(directory, configuration_files, configuration_values, *args, **kwargs)
        self.config_file = os.path.join(directory, 'httpd', 'simple_server_config.py')
        self.db_conf = DbConfiguration(configuration_files, configuration_values)

    def check_updated(self):
        """
        Check whether we need to apply this updater.
        :return:
        """
        # We need to update if the simple_server_config.py has a Redirect from /weblab to /weblab/client (which was done for GWT
        # but which should not be done anymore).
        contents = open(self.config_file, "r").read()
        result = re.search(r"u'.*\$', u'redirect:.*/weblab/client'", contents)

        return result is None

    def upgrade(self):

        print("[Upgrader]: Starting update: Changing from GWT to new Non-GWT client")



        # UPGRADE ACTION 1: Old 'dummy' type experiments are now 'js' experiments.
        connection_url = self.db_conf.build_url()
        engine = create_engine(connection_url, echo=False, convert_unicode=True)

        Session = sessionmaker(bind=engine)
        session = Session()
        try:
            db_experiments = session.query(model.DbExperiment).filter_by(client='dummy').all()
            for db_exp in db_experiments:
                db_exp.client = 'js'

                # Add html.file
                db_param = model.DbExperimentClientParameter()
                db_param.experiment_id = db_exp.id
                db_param.parameter_name = 'html.file'
                db_param.value = 'nativelabs/dummy.html'
                db_param.parameter_type = 'string'

                session.add(db_exp)
                session.add(db_param)

                print("Experiment {0} had client 'dummy' and now has client 'js'".format(db_exp.name))
            session.commit()
        finally:
            session.close()
        print("[Upgrader]: DONE: Changed Dummy experiments to type JS")

        # UPGRADE ACTION 2: JS experiments should have builtin set to true (all of them are builtin for now).

        session = Session()
        try:
            db_experiments = session.query(model.DbExperiment).filter_by(client='js').all()
            for db_exp in db_experiments:
                db_builtin_param = session.query(model.DbExperimentClientParameter).filter_by(experiment_id=db_exp.id,
                                                                                              parameter_name='builtin').first()
                if db_builtin_param is None:
                    db_builtin_param = model.DbExperimentClientParameter()
                    db_builtin_param.experiment = db_exp
                    db_builtin_param.parameter_name = 'builtin'
                    db_builtin_param.parameter_type = 'bool'
                db_builtin_param.value = "True"
                session.add(db_builtin_param)
            session.commit()
        finally:
            session.close()
        print("[Upgrader]: DONE: All JS experiments now have a builtin parameter set to True")

        # UPGRADE ACTION 3: Call httpd-config-generate script.
        httpd_config_generate(self.directory)
        print("[Upgrader]: DONE: Called http-config-generate to upgrade Apache configuration files")

        print("[Upgrader]: UPGRADE FINISHED.")


class ConfigurationExperiments2db(Upgrader):
    def __init__(self, directory, configuration_files, configuration_values, *args, **kwargs):
        super(ConfigurationExperiments2db, self).__init__(directory, configuration_files, configuration_values, *args,
                                                          **kwargs)
        self.db_conf = DbConfiguration(configuration_files, configuration_values)
        self.config_js = os.path.join(directory, 'client', 'configuration.js')
        if os.path.exists(self.config_js):
            self.config = json.load(open(self.config_js))
        else:
            self.config = {}

    @classmethod
    def get_priority(self):
        """ After database """
        return 1

    def check_updated(self):
        # In the future, this file will not exist.
        if not os.path.exists(self.config_js):
            return True

        # But if it exists and it has an 'experiments' section, it has 
        # not been upgraded.
        if 'experiments' in self.config:
            print(
                " - configuration.js contains experiments. The experiments in the configuration.js are going to be migrated to the database.")
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

                    db_category = session.query(model.DbExperimentCategory).filter_by(name=experiment_category).first()
                    if not db_category:
                        # Experiment not in database
                        continue

                    db_experiment = session.query(model.DbExperiment).filter_by(category=db_category,
                                                                                name=experiment_name).first()
                    if not db_experiment:
                        # Experiment not in database
                        continue

                    db_experiment.client = client_id
                    for key in experiment:
                        if key in ('experiment.category', 'experiment.name'):
                            # Already processed
                            continue

                        existing_parameter = session.query(model.DbExperimentClientParameter).filter_by(
                            parameter_name=key, experiment=db_experiment).first()
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
                            print("Error: invalid parameter type %s for key %s of experiment %s" % (
                            type(value), key, experiment_name))
                            continue

                        param = model.DbExperimentClientParameter(db_experiment, key, param_type,
                                                                  unicode(experiment[key]))
                        session.add(param)
            session.commit()
        finally:
            session.close()

        self.config.pop('experiments')
        json.dump(self.config, open(self.config_js, 'w'), indent=4)


class RemoveOldWebAndLoginPorts(Upgrader):
    def __init__(self, directory, configuration_files, configuration_values, *args, **kwargs):
        super(RemoveOldWebAndLoginPorts, self).__init__(directory, configuration_files, configuration_values, *args,
                                                        **kwargs)

    @classmethod
    def get_priority(self):
        """ After configuration.js has been parsed """
        return 2

    def check_updated(self):
        """ True => it's upgraded. False => needs to be upgraded """
        login_config_files = [f for f in self.configuration_files if '/login/' in f]
        for fname in login_config_files:
            with open(fname) as f:
                for line in f:
                    if line.startswith(('login_facade_json_port', 'login_facade_web_port')):
                        print(
                            " - login server is going to be removed, as well as certain port configurations. Everything you have in login will be now part of core.")
                        return False
        return True

    def upgrade(self):
        login_config_files = [f for f in self.configuration_files if '/login/' in f]
        login_replacements = {
            # 'login_server_config' : 'core_server_config'
        }
        login_directories = []  # To be removed

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
                print("Error finding the core server directory for login server: %s" % fname, file=sys.stderr)
                return

        # Here we know what are the directories to be removed and what are the configuration_files to be removed
        if not os.path.exists('debugging.py'):
            print("debugging.py file not found in the root directory of the deployment", file=sys.stderr)
            return

        debugging_ports = {}
        execfile('debugging.py', debugging_ports)

        simple_server = {}
        simple_server_config_filename = os.path.join('httpd', 'simple_server_config.py')
        execfile(simple_server_config_filename, simple_server)
        KEYS = ('/weblab/json/', '/weblab/login/json/', '/weblab/login/web/', '/weblab/web/', '/weblab/administration')

        ports_per_path = {}
        for key, value in dict(simple_server['PATHS']).iteritems():
            for url_key in KEYS:
                if url_key in key:
                    ports = [port_str[1:-1] for port_str in re.findall(":[0-9]+/", value)]
                    ports_per_path[url_key] = ports

        for url_key in KEYS:
            if url_key not in ports_per_path:
                print("Error: Key %s expected and not found in %s" % (
                url_key, os.path.abspath(simple_server_config_filename)), file=sys.stderr)
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

        print("Start migrating old login and web ports")


        # Step 1: debugging.py

        print(" - Upgrading debugging.py")

        new_contents = ''.join([line for line in open('debugging.py') if 'json_login' not in line])
        open('debugging.py', 'w').write(new_contents)

        # Steps 2 & 3: apache_weblab_generic.conf & simple_server_config.py

        print(" - Upgrading httpd files")

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
            print(" - Upgrading %s" % os.path.abspath(core_replacement))
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

        print("Old login and web ports migration completed.")


class RemoveXmlsAndAddYaml(Upgrader):
    def __init__(self, directory, *args, **kwargs):
        super(RemoveXmlsAndAddYaml, self).__init__(directory, *args, **kwargs)
        self.yml_file = os.path.join(self.directory, 'configuration.yml')

    @classmethod
    def get_priority(self):
        """ After login has been removed """
        return 3

    def check_updated(self):
        """ True => it's upgraded. False => needs to be upgraded """
        if os.path.exists(self.yml_file):
            return True

        print(
            " - The existing infrastructure of configuration.xml and directories is going to be simplified into a single configuration.yml file.")
        return False

    def _update_with_config(self, config, base_dir, node):
        files = []
        for config_node in node.getElementsByTagName('configuration'):
            file_name = config_node.getAttribute('file')
            full_path = os.path.join(base_dir, file_name)
            files.append(full_path)

        files_to_delete = []

        if len(files) == 1:
            fglobals = {}
            flocals = {}
            replace = False
            try:
                execfile(files[0], fglobals, flocals)
            except:
                pass
            else:
                if len(flocals) <= 3:
                    replace = True
                    for value in flocals.values():
                        if not isinstance(value, int) and not isinstance(value, float) and not isinstance(value,
                                                                                                          basestring):
                            replace = False
                        elif isinstance(value, basestring) and len(value) > 80:
                            replace = False
                    for name in flocals:
                        if 'password' in name or 'passwd' in name or 'secret' in name:
                            replace = False

            if replace:
                if flocals:
                    config['config'] = flocals
                files_to_delete.append(files[0])
            else:
                config['config_file'] = files[0]
        elif len(files) > 1:
            config['config_files'] = files

        return files_to_delete

    def upgrade(self):
        files_to_delete = []
        directories_to_delete = []
        global_config = {
            # if single file:
            #   'config_file' : 'filename.py',
            # if multiple:
            #   'config_files' : [ ... ],
            # 'hosts' : {
            #    'main' : {
            #        # If present
            #        'host' : '127.0.0.1',
            #        'runner' : 'launch_plunder.py'
            #        'config_file/files' : ...
            #        'processes' : { 
            #            'process1' : {
            #                 # 'config_file/files': ...
            #                 'components' : { # list or dictionary
            #                     # 'config_file/files': ...
            #                     'laboratory' : {
            #                         'type' : 'laboratory'
            #                         'impl' : '...',
            #                         # config_file/files,
            #                         'protocols': {
            #                              # 'bind' : ''
            #                              'port' : 12345,
            #                              'xmlrpc' : {
            #                                  'path' : '/RPC2'
            #                              }
            #                         }
            #                     }
            #                 }
            #            }
            #        }
            #    }
            # }
        }

        protocol_regex = re.compile("(.*):([0-9]*)(.*)@.*")

        global_config_xml = os.path.join(self.directory, 'configuration.xml')
        files_to_delete.append(global_config_xml)
        global_config_xml_node = minidom.parse(global_config_xml)
        files_to_delete.extend(self._update_with_config(global_config, '.', global_config_xml_node))

        all_runners = set(['run.py'])

        for machine in global_config_xml_node.getElementsByTagName('machine'):
            host_name = machine.firstChild.nodeValue
            directories_to_delete.append(os.path.join(self.directory, host_name))
            host_config = global_config.setdefault('hosts', OrderedDict())[host_name] = OrderedDict()

            machine_config_xml = os.path.join(self.directory, host_name, 'configuration.xml')
            files_to_delete.append(machine_config_xml)
            machine_config_xml_node = minidom.parse(machine_config_xml)
            files_to_delete.extend(self._update_with_config(host_config, host_name, machine_config_xml_node))

            runners = machine_config_xml_node.getElementsByTagName('runner')
            if len(runners):
                runner = runners[0]
                runner_filename = runner.getAttribute('file')
                host_config['runner'] = runner_filename
                all_runners.add(runner_filename)

            for instance in machine_config_xml_node.getElementsByTagName('instance'):
                process_name = instance.firstChild.nodeValue
                directories_to_delete.append(os.path.join(self.directory, host_name, process_name))
                process_config = OrderedDict()

                instance_config_xml = os.path.join(self.directory, host_name, process_name, 'configuration.xml')
                files_to_delete.append(instance_config_xml)
                instance_config_xml_node = minidom.parse(instance_config_xml)
                files_to_delete.extend(self._update_with_config(process_config, os.path.join(host_name, process_name),
                                                                instance_config_xml_node))

                for server in instance_config_xml_node.getElementsByTagName('server'):

                    component_name = server.firstChild.nodeValue
                    directories_to_delete.append(os.path.join(self.directory, host_name, process_name, component_name))
                    component_config = process_config.setdefault('components', OrderedDict())[
                        component_name] = OrderedDict()

                    server_config_xml = os.path.join(self.directory, host_name, process_name, component_name,
                                                     'configuration.xml')
                    files_to_delete.append(server_config_xml)
                    server_config_xml_node = minidom.parse(server_config_xml)
                    files_to_delete.extend(self._update_with_config(component_config,
                                                                    os.path.join(host_name, process_name,
                                                                                 component_name),
                                                                    server_config_xml_node))

                    method_name = server_config_xml_node.getElementsByTagName('methods')[0].firstChild.nodeValue
                    server_types = {
                        'weblab.methods::UserProcessing': 'core',
                        'weblab.methods::Laboratory': 'laboratory',
                        'weblab.methods::Experiment': 'experiment'
                    }
                    try:
                        server_type = server_types[method_name]
                    except KeyError:
                        raise Exception("Invalid server type %s" % method_name)
                    component_config['type'] = server_type
                    if server_type not in ('laboratory', 'core'):
                        implementation = server_config_xml_node.getElementsByTagName('implementation')[
                            0].firstChild.nodeValue
                        component_config['class'] = implementation

                    # Core does not have any method. Any protocol (e.g., SOAP, XML-RPC or so) assigned to it is an error
                    if server_type != 'core':
                        for protocol_node in server_config_xml_node.getElementsByTagName('protocol'):
                            protocol_name = protocol_node.getAttribute('name')
                            if protocol_name == 'Direct':
                                continue  # Implicitly, every server supports direct

                            coordinations = []
                            hosts = set()
                            ports = set()
                            paths = set()
                            for coordination_node in protocol_node.getElementsByTagName('coordination'):
                                address = coordination_node.getElementsByTagName('parameter')[0].getAttribute('value')
                                host_ip, port, path = protocol_regex.match(address).groups()
                                hosts.add(host_ip)
                                ports.add(port)
                                paths.add(path)
                                coordinations.append({'host': host_ip, 'port': port, 'path': path})

                            if coordinations:
                                # If it was established by somebody else, put it
                                current_host_ip = host_config.get('host')
                                if current_host_ip:
                                    hosts.add(current_host_ip)

                                hosts = list(hosts)
                                non_localhost = [h for h in hosts if h not in ('localhost', '127.0.0.1')]
                                if non_localhost:
                                    host_config['host'] = non_localhost[0]
                                else:
                                    host_config['host'] = hosts[0]

                                component_config.setdefault('protocols', {})['port'] = int(list(ports)[0])

                                protocol_name = 'http' if protocol_name == 'SOAP' else 'xmlrpc'
                                component_config['protocols'][protocol_name] = {}
                                paths = [path for path in paths if path]
                                if paths:
                                    component_config['protocols']['path'] = paths[0]

                            if 'protocols' in component_config:
                                protocols_config = component_config['protocols']
                                if 'http' in protocols_config:
                                    protocols_config.pop('http', None)
                                    protocols_config.pop('xmlrpc', None)
                                else:
                                    protocols_config.pop('xmlrpc', None)
                                    protocols_config['supports'] = 'xmlrpc'

                host_config.setdefault('processes', OrderedDict())[process_name] = process_config

        global_config = eval(repr(global_config).replace("u'", "'").replace('u"', '"'))
        new_config_yaml = ordered_dump(global_config, width=5, default_flow_style=False)
        open(self.yml_file, 'w').write(new_config_yaml)

        for runner in all_runners:
            if os.path.exists(runner):
                new_contents = open(runner).read().replace('import voodoo.gen.loader.Launcher as Launcher',
                                                           'import voodoo.gen.launcher as Launcher')
                open(runner, 'w').write(new_contents)

        if ask_yes(
                "There are many configuration.xml files that are not required anymore. There might be some configuration files which are also not required anymore. Do you want to delete them all?",
                self.sys_args):
            for file_to_delete in files_to_delete:
                os.remove(file_to_delete)

            for dir_to_delete in directories_to_delete:
                if len(os.listdir(dir_to_delete)) == 0:
                    os.rmdir(dir_to_delete)


class ClientConfiguration2db(Upgrader):
    def __init__(self, directory, configuration_files, configuration_values, *args, **kwargs):
        super(ClientConfiguration2db, self).__init__(directory, configuration_files, configuration_values, *args,
                                                     **kwargs)
        self.db_conf = DbConfiguration(configuration_files, configuration_values)
        self.config_js = os.path.join(directory, 'client', 'configuration.js')
        if os.path.exists(self.config_js):
            self.config = json.load(open(self.config_js))
        else:
            self.config = {}

    @classmethod
    def get_priority(self):
        """ After database """
        return 4

    def check_updated(self):
        # In the future, this file will not exist.
        if not os.path.exists(self.config_js):
            return True

        print(
            " - There is a client/configuration.js file, which contains the generic configuration. Now that configuration is managed by the administration panel, and stored in the database. So all those values that you are using will be migrated to the database.")
        return False

    def upgrade(self):
        connection_url = self.db_conf.build_url()
        engine = create_engine(connection_url, echo=False, convert_unicode=True)

        Session = sessionmaker(bind=engine)
        session = Session()
        try:
            for key, value in six.iteritems(self.config):
                if key in ('development', 'host.entity.image.mobile', 'host.entity.image', 'sound.enabled',
                           'experiments.default_picture', 'host.entity.image.login', 'facebook.like.box.visible',
                           'create.account.visible'):
                    continue
                new_property = model.DbClientProperties(key, value)
                session.add(new_property)

            session.commit()
        finally:
            session.close()

        os.remove(self.config_js)

        simple_server_config_filename = os.path.join('httpd', 'simple_server_config.py')
        lines = []
        for line in open(simple_server_config_filename):
            if 'weblabclientadmin' not in line and 'configuration.js' not in line and 'webserver' not in line and 'client/images' not in line:
                lines.append(line)

        open(simple_server_config_filename, 'w').write(''.join(lines))

        apache_weblab_generic_conf_filename = os.path.join('httpd', 'apache_weblab_generic.conf')
        lines = []
        bad_pos = -1
        recording = True
        for pos, line in enumerate(open(apache_weblab_generic_conf_filename)):
            if bad_pos >= 0:
                bad_pos -= 1
                continue

            if 'LocationMatch (.*)configuration\.js' in line:
                bad_pos = 1
                continue

            if 'configuration.js' in line or 'weblabclientadmin' in line or 'client/images' in line:
                continue

            if 'webserver' in line and '<Directory' in line:
                recording = False
            if not recording and '</Directory' in line:
                recording = True
                continue

            if recording:
                lines.append(line)

        open(apache_weblab_generic_conf_filename, 'w').write(''.join(lines))
