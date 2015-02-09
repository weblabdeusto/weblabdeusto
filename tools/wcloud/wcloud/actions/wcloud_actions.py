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
*** As of 9 aprl 2014 this file (previously taskmanager.py) is being ported to celery wcloud_tasks.py.

TaskManager: monothread system that deploys WebLab-Deusto instances.

This system is monothread (and therefore, it can not be deployed as
a regular WSGI system with multiple processes) and listens in local.
Whenever a local client requests it, it will create a new WebLab-Deusto
configuration, providing a RESTful API for retrieving the current status
of the deployment.
"""

import os
import time
import traceback
import urllib2
import json
import tempfile
from cStringIO import StringIO

from flask import Flask
import sqlalchemy
from sqlalchemy.orm import sessionmaker
import sys
from wcloud.actions import db_actions, redis_actions

from weblab.admin.script import weblab_create, Creation

from wcloud import deploymentsettings
# import deploymentsettings

from wcloud.models import User, Entity
from wcloud.tasks.celery_app import celery_app


# TODO: Currently "models" is trying to load the "wcloud" database. A way to override that
# session when in tests would be very useful.


# TODO: Remove the dependency on this.
import wcloud.config.wcloud_settings_default as wcloud_settings_default
import wcloud.config.wcloud_settings as wcloud_settings

flask_app = Flask(__name__)
flask_app.config.from_object(wcloud_settings_default)
flask_app.config.from_object(wcloud_settings)
flask_app.config.from_envvar('WCLOUD_SETTINGS', silent=True)

# TODO: Check that the config order is consistent.


def connect_to_database(user, passwd, db_name):
    """
    Connects to the MySQL database using the specified username and password.
    Assumes the DB is in localhost and listening on port 3306.

    @param user: Username, which will need to be root to create new databases.
    @param passwd: Password for the Username.

    @return: Connection object and the Session() maker.
    """
    conn_string = 'mysql://%s:%s@%s:%d' % (user, passwd, '127.0.0.1', 3306)
    engine = sqlalchemy.create_engine(conn_string)
    connection = engine.connect()
    connection.execute("SELECT 1")
    connection.execute("USE %s" % db_name)

    Session = sessionmaker(bind=connection)

    return connection, Session


def prepare_system(self, wcloud_user_email, admin_user, admin_name, admin_password, admin_email, wcloud_settings):
    """
    Prepare the system. Ports and databases are assigned.

    @param wcloud_user_email: User email to identify the account of the wcloud user that is making the request.
    @param admin_user: Username of the wcloud instance admin.
    @param admin_password: Password for the wcloud instance admin.
    @param admin_email: Email address for the wcloud instance admin.
    @param wcloud_settings: Dictionary containing settings. Those will override both the default_settings and the ones
    declared through the WCLOUD_SETTINGS environment variable.
    """
    #self.update_state(state="PROGRESS", meta={"action": "Preparing system"})

    # Override the items in the config that are contained in the explicit wcloud_settings dictionary.
    flask_app.config.update(wcloud_settings)

    # Connect to the database
    connection, Session = connect_to_database(flask_app.config["DB_USERNAME"], flask_app.config["DB_PASSWORD"],
                                              flask_app.config["DB_NAME"])
    session = Session()
    session._model_changes = {}  # Bypass flask issue.

    # Get the wcloud user.
    user = session.query(User).filter_by(email=wcloud_user_email).first()
    entity = user.entity

    #
    # Write the logo to disc
    #
    tmp_logo = tempfile.NamedTemporaryFile()
    tmp_logo.write(user.entity.logo)
    tmp_logo.flush()

    #
    # Prepare the parameters
    #

    # Copy the default settings from the deploymentsettings file.
    settings = deploymentsettings.DEFAULT_DEPLOYMENT_SETTINGS.copy()

    # settings[Creation.BASE_URL] = 'w/' + entity.base_url
    settings[Creation.BASE_URL] = entity.base_url

    # TODO: Originally a w/ was preppended. That is confusing because knowing the BASE_URL
    # is required in other parts of the code. For instance, for the create itself.
    # We remove it for now. May have side effects, and maybe should be added somehow.

    if user.entity.logo != None and user.entity.logo != "":
        settings[Creation.LOGO_PATH] = tmp_logo.name
    else:
        settings[Creation.LOGO_PATH] = None

    # TODO: Change the DB system.

    # Create a new database and assign the DB name.
    # TODO: Unhardcode / tidy this up.
    db_name = db_actions.create_db("wcloud_creator", flask_app.config["DB_WCLOUD_CREATOR_PASSWORD"],
                                 "wcloud_%s" % entity.base_url, flask_app.config["DB_USERNAME"],
                                 flask_app.config["DB_PASSWORD"])
    entity.db_name = db_name
    session.commit()

    # settings[Creation.DB_NAME] = 'wcloud%s' % entity.id
    settings[Creation.DB_NAME] = db_name

    settings[Creation.DB_USER] = flask_app.config['DB_USERNAME']
    settings[Creation.DB_PASSWD] = flask_app.config['DB_PASSWORD']

    databases_per_port = flask_app.config['REDIS_DBS_PER_PORT']
    initial_redis_port = flask_app.config['REDIS_START_PORT']

    settings[Creation.COORD_REDIS_DB] = entity.id % databases_per_port
    settings[Creation.COORD_REDIS_PORT] = initial_redis_port + entity.id / databases_per_port

    # TODO: Tidy this up. Remove redis_env hardcoding.
    # Ensure REDIS is present.
    try:
        redis_actions.deploy_redis_instance(flask_app.config["REDIS_FOLDER"], settings[Creation.COORD_REDIS_PORT])
    except (redis_actions.AlreadyDeployedException) as ex:
        pass

    redis_actions.check_redis_deployment(flask_app.config["REDIS_FOLDER"], settings[Creation.COORD_REDIS_PORT])

    settings[Creation.ADMIN_USER] = admin_user
    settings[Creation.ADMIN_NAME] = admin_name
    settings[Creation.ADMIN_PASSWORD] = admin_password
    settings[Creation.ADMIN_MAIL] = admin_email


    # Retrieve the last assigned port from the database, so that we can assign the
    # next one as the starting point of the new instance.
    last_port = session.query(sqlalchemy.func.max(Entity.end_port_number)).one()[0]
    if last_port is None:
        last_port = deploymentsettings.MIN_PORT

    settings[Creation.START_PORTS] = last_port + 1
    settings[Creation.SYSTEM_IDENTIFIER] = user.entity.name
    settings[Creation.ENTITY_LINK] = user.entity.link_url

    Session.close_all()
    connection.close()

    return settings


def create_weblab_environment(self, directory, settings):
    """
    2. Create the full WebLab-Deusto environment.

    @param directory: Directory to create.
    @param settings: Deployment settings to use.
    @return: Results of the Weblab creation process. They may be required to take further action, such as
    adding the new instance to the Web Server configuration.
    """

    #self.update_state(state="PROGRESS", meta={"action": "Creating deployment directory"})

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


def configure_web_server(self, creation_results):
    """
    3. Configures the Apache web server. (Adds a new, specific .conf to the Apache configuration files, so that
    the new Weblab-Deusto instance is run appropriately).

    REQUIREMENT: For this to work, the Apache Reloader script must be listening for requests on the
    APACHER_RELOADER_PORT, which is 1662 by default.
    """

    ##########################################################
    #
    # 3. Configure the web server
    #
    #self.update_state(state="PROGRESS", meta={"action": "Configuring Web Server"})

    # Create Apache configuration
    with open(os.path.join(flask_app.config['DIR_BASE'],
                           deploymentsettings.APACHE_CONF_NAME), 'a') as f:
        conf_dir = creation_results['apache_file']
        f.write('Include "%s"\n' % conf_dir)

    # Reload apache
    opener = urllib2.build_opener(urllib2.ProxyHandler({}))
    print(opener.open('http://127.0.0.1:%s/' % flask_app.config['APACHE_RELOADER_PORT']).read())


def weblab_starter_running():
    try:
        url = 'http://127.0.0.1:%s' % flask_app.config['WEBLAB_STARTER_PORT']
        req = urllib2.Request(url)
        opener = urllib2.build_opener(urllib2.ProxyHandler({}))
        response = opener.open(req).read()
        return True
    except:
        return False


def register_and_start_instance(self, wcloud_user_email, explicit_wcloud_settings):
    """
    Registers and starts the new WebLab-Deusto instance.
    This might take a while.

    REQUIREMENTS: The WebLab Starter must be running on WEBLAB_STARTER_PORT
    as defined in the configuration files. By defualt, this port is 1663.

    @param wcloud_user_email: The email of the wcloud user whose instance we are deploying.
    """
    #self.update_state(state="PROGRESS", meta={"action": "Registering and Starting the new Weblab Instance"})

    print "[DBG]: ON REGISTER AND START INSTANCE"

    # Override the items in the config that are contained in the explicit_wcloud_settings dictionary.
    flask_app.config.update(explicit_wcloud_settings)

    # Connect to the database
    connection, Session = connect_to_database(flask_app.config["DB_USERNAME"], flask_app.config["DB_PASSWORD"],
                                              flask_app.config["DB_NAME"])
    session = Session()
    session._model_changes = {}  # Bypass flask issue.

    try:
        # Get the wcloud entity.
        user = session.query(User).filter_by(email=wcloud_user_email).first()
        entity = user.entity

        if entity is None:
            result = "[register_and_start_instance]: ERROR: Could not retrieve entity from the database %s" % flask_app.config["DB_NAME"]
            sys.stderr.write(result)
            raise Exception(result)
    except:
        sys.stderr.write(
            "[register_and_start_instance]: ERROR: Recovering wcloud user from DB. DB_NAME: %s" % flask_app.config[
                "DB_NAME"])

    Session.close_all()

    global response
    import urllib2
    import traceback

    response = None
    is_error = False

    # Verify that the Weblab Starter seems to be running
    starter_running = weblab_starter_running()
    if not starter_running:
        print "Apparently the WebLab starter is not running."
        is_error = True
        response = "Apparently the WebLab starter is not running."

    try:
        url = 'http://127.0.0.1:%s/deployments/' % flask_app.config['WEBLAB_STARTER_PORT']
        req = urllib2.Request(url, json.dumps({'name': entity.base_url}), {'Content-Type': 'application/json'})
        opener = urllib2.build_opener(urllib2.ProxyHandler({}))
        response = opener.open(req).read()
    except:
        is_error = True
        reason = traceback.format_exc()
        response = "There was an error registering or starting the service. Contact the administrator: %s" % reason
        traceback.print_exc()

    print "Ended. is_error=%s; response=%s" % (is_error, response)

    if is_error:
        raise Exception(response)


def finish_deployment(self, wcloud_user_email, settings, start_port, end_port, wcloud_settings):
    """
    Finishes the deployment, marks the entity as deployed and
    configures the response.
    """
    #self.update_state(state="PROGRESS", meta={"action": "Finishing the deployment."})

    # Override the items in the config that are contained in the explicit wcloud_settings dictionary.
    flask_app.config.update(wcloud_settings)

    # Connect to the database
    connection, Session = connect_to_database(flask_app.config["DB_USERNAME"], flask_app.config["DB_PASSWORD"],
                                              flask_app.config["DB_NAME"])
    session = Session()
    session._model_changes = {}  # Bypass flask issue.

    # Get the wcloud entity.
    user = session.query(User).filter_by(email=wcloud_user_email).first()
    entity = user.entity

    url = settings[Creation.SERVER_HOST] + "/" + entity.base_url

    # Save in database data like last port
    # Note: this is thread-safe since the task manager is
    # monothread
    user.entity.start_port_number = start_port
    user.entity.end_port_number = end_port

    # Save
    session.add(user)
    session.commit()

    Session.close_all()




def deploy_weblab_instance(self):
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




