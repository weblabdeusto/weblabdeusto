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
# Author: Xabier Larrakoetxea <xabier.larrakoetxea@deusto.es>
#         Pablo Orduña <pablo.orduna@deusto.es>
#         Luis Rodríguez <luis.rodriguezgil@deusto.es>
#
# These authors would like to acknowledge the Spanish Ministry of science
# and innovation, for the support in the project IPT-2011-1558-430000
# "mCloud: http://innovacion.grupogesfor.com/web/mcloud"
#

"""
TaskManager: monothread system that deploys WebLab-Deusto instances.

This system is monothread (and therefore, it can not be deployed as
a regular WSGI system with multiple processes) and listens in local.
Whenever a local client requests it, it will create a new WebLab-Deusto
configuration, providing a RESTful API for retrieving the current status
of the deployment.
"""

import os
import time
import shutil
import traceback
import urllib2
import sys
import json
import tempfile
from cStringIO import StringIO

import sqlalchemy

from wcloud import app, db
from wcloud.actions import db_actions, redis_actions
from wcloud.models import User, Entity
from wcloud.tasks.celery_app import celery_app
from wcloud.tasks.admin_tasks import apache_reload
from wcloud.tasks.starter_tasks import start_weblab, stop_weblab

from weblab.admin.script import weblab_create, Creation

# TODO: Currently "models" is trying to load the "wcloud" database. A way to override that
# session when in tests would be very useful.

def rollback_prepare_system(wcloud_user_email):
    user = db.session.query(User).filter_by(email=wcloud_user_email).first()
    try:
        db_name = db_actions.destroy_db("wcloud_creator", app.config["DB_WCLOUD_CREATOR_PASSWORD"], "wcloud_%s" % user.entity.base_url)
    except:
        traceback.print_exc()
    
    try:
        user.entity.db_name = None
        db.session.add(user.entity)
        db.session.commit()
    except:
        traceback.print_exc()

def prepare_system(wcloud_user_email, admin_user, admin_name, admin_password, admin_email):
    """
    Prepare the system. Ports and databases are assigned.

    @param wcloud_user_email: User email to identify the account of the wcloud user that is making the request.
    @param admin_user: Username of the wcloud instance admin.
    @param admin_password: Password for the wcloud instance admin.
    @param admin_email: Email address for the wcloud instance admin.
    @param wcloud_settings: Dictionary containing settings. Those will override both the default_settings and the ones
    declared through the WCLOUD_SETTINGS environment variable.
    """

    # Get the wcloud user.
    user = db.session.query(User).filter_by(email=wcloud_user_email).first()
    entity = user.entity

    #
    # Write the logo to disc
    #
    tmp_logo = tempfile.NamedTemporaryFile()
    tmp_logo.write(entity.logo)
    tmp_logo.flush()

    #
    # Prepare the parameters
    #

    # Copy the default settings from the config file.
    settings = app.config['DEFAULT_DEPLOYMENT_SETTINGS'].copy()

    # settings[Creation.BASE_URL] = 'w/' + entity.base_url
    settings[Creation.BASE_URL] = entity.base_url

    # TODO: Originally a w/ was preppended. That is confusing because knowing the BASE_URL
    # is required in other parts of the code. For instance, for the create itself.
    # We remove it for now. May have side effects, and maybe should be added somehow.

    if entity.logo != None and entity.logo != "":
        settings[Creation.LOGO_PATH] = tmp_logo.name
    else:
        settings[Creation.LOGO_PATH] = None

    # TODO: Change the DB system.

    # Create a new database and assign the DB name.
    # TODO: Unhardcode / tidy this up.
    db_name = db_actions.create_db("wcloud_creator", app.config["DB_WCLOUD_CREATOR_PASSWORD"],
                                 "wcloud_%s" % entity.base_url, app.config["DB_USERNAME"],
                                 app.config["DB_PASSWORD"])
    entity.db_name = db_name
    db.session.add(entity)
    db.session.commit()

    settings[Creation.DB_NAME] = db_name
    settings[Creation.DB_USER] = app.config['DB_USERNAME']
    settings[Creation.DB_PASSWD] = app.config['DB_PASSWORD']

    databases_per_port = app.config['REDIS_DBS_PER_PORT']
    initial_redis_port = app.config['REDIS_START_PORT']

    settings[Creation.COORD_REDIS_DB] = entity.id % databases_per_port
    settings[Creation.COORD_REDIS_PORT] = initial_redis_port + entity.id / databases_per_port

    # TODO: Tidy this up. Remove redis_env hardcoding.
    # Ensure REDIS is present.
    try:
        redis_actions.deploy_redis_instance(app.config["REDIS_FOLDER"], settings[Creation.COORD_REDIS_PORT])
    except (redis_actions.AlreadyDeployedException) as ex:
        traceback.print_exc()
        pass

    redis_actions.check_redis_deployment(app.config["REDIS_FOLDER"], settings[Creation.COORD_REDIS_PORT])

    settings[Creation.ADMIN_USER] = admin_user
    settings[Creation.ADMIN_NAME] = admin_name
    settings[Creation.ADMIN_PASSWORD] = admin_password
    settings[Creation.ADMIN_MAIL] = admin_email


    # Retrieve the last assigned port from the database, so that we can assign the
    # next one as the starting point of the new instance.
    last_port = db.session.query(sqlalchemy.func.max(Entity.end_port_number)).one()[0]
    if last_port is None:
        last_port = app.config['MIN_PORT']

    settings[Creation.START_PORTS] = last_port + 1
    settings[Creation.SYSTEM_IDENTIFIER] = user.entity.name
    settings[Creation.ENTITY_LINK] = user.entity.link_url
    return settings

def rollback_create_weblab_environment(directory):
    shutil.rmtree(directory)

def create_weblab_environment(directory, settings):
    """
    2. Create the full WebLab-Deusto environment.

    @param directory: Directory to create.
    @param settings: Deployment settings to use.
    @return: Results of the Weblab creation process. They may be required to take further action, such as
    adding the new instance to the Web Server configuration.
    """

    output = StringIO()
    command_output = StringIO()

    def exit_func(code):
        traceback.print_exc()
        print "[WebLabCreate] Output:", command_output.getvalue()
        raise Exception("Error creating weblab: %s" % code)

    results = weblab_create(directory,
                            settings,
                            command_output,
                            command_output,
                            exit_func)

    time.sleep(0.5)

    # Don't know what was this done originally for.
    # settings.update(task)

    return results


def rollback_configure_web_server(creation_results):
    try:
        apache_filename = os.path.join(app.config['DIR_BASE'], app.config['APACHE_CONF_NAME'])
        new_line = 'Include "%s"\n' % creation_results['apache_file']
        lines = [ line for line in open(apache_filename) if line != new_line ]
        new_contents = ''.join(lines)
        open(apache_filename, 'w').write(new_contents)
    except:
        traceback.print_exc()

def configure_web_server(creation_results):
    """
    3. Configures the Apache web server. (Adds a new, specific .conf to the Apache configuration files, so that
    the new Weblab-Deusto instance is run appropriately).
    """

    ##########################################################
    #
    # 3. Configure the web server
    #

    # Create Apache configuration
    with open(os.path.join(app.config['DIR_BASE'], app.config['APACHE_CONF_NAME']), 'a') as f:
        conf_dir = creation_results['apache_file']
        f.write('Include "%s"\n' % conf_dir)

    # Reload apache
    apache_reload.delay().get()


def rollback_register_and_start_instance(directory):
    stop_weblab(directory)

def register_and_start_instance(wcloud_user_email, directory):
    """
    Registers and starts the new WebLab-Deusto instance.
    This might take a while.

    REQUIREMENTS: The WebLab Starter must be running on Celery

    @param wcloud_user_email: The email of the wcloud user whose instance we are deploying.
    """
    print "[DBG]: ON REGISTER AND START INSTANCE"

    try:
        # Get the wcloud entity.
        user = db.session.query(User).filter_by(email=wcloud_user_email).first()
        entity = user.entity
    except:
        sys.stderr.write(
            "[register_and_start_instance]: ERROR: Recovering wcloud user from DB. DB_NAME: %s" % flask_app.config[
                "DB_NAME"])
        raise

    if entity is None:
        result = "[register_and_start_instance]: ERROR: Could not retrieve entity from the database %s" % app.config["DB_NAME"]
        sys.stderr.write(result)
        raise Exception(result)
    
    start_weblab.delay(directory, True).get()
    

def rollback_finish_deployment(wcloud_user_email):
    user = db.session.query(User).filter_by(email=wcloud_user_email).first()
    if user is not None:
        user.entity.start_port_number = None
        user.entity.end_port_number = None
        db.session.add(user.entity)
        db.session.commit()

def finish_deployment(wcloud_user_email, start_port, end_port):
    """
    Finishes the deployment, marks the entity as deployed and
    configures the response.
    """
    # Get the wcloud entity.
    user = db.session.query(User).filter_by(email=wcloud_user_email).first()

    # Save in database data like last port
    # Note: this is thread-safe since the task manager is
    # monothread
    user.entity.start_port_number = start_port
    user.entity.end_port_number = end_port

    # Save
    db.session.add(user.entity)
    db.session.commit()

def deploy_weblab_instance():
    """
    TODO: This method should probably be removed once the taskmanager invokes the methods by itself.

    As of now this function does not run and is not meant to.
    Just for reference purposes.
    """
    prepare_system()
    create_weblab_environment()
    configure_web_server()
    register_and_start_instance()
    finish_deployment()
