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
    if raw_input("Do you want to continue with the upgrade? (y/n)") == 'y':
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
                        elif isinstance(value, float):
                            param_type = 'floating'
                        elif isinstance(value, int):
                            param_type = 'integer'
                        elif isinstance(value, bool):
                            param_type = 'bool'
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

