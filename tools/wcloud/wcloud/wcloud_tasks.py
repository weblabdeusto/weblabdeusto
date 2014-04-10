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
import sys

import shutil
import Queue
import threading
import time
import traceback
import unittest
import urllib2
import json
import uuid
import tempfile
from cStringIO import StringIO

from flask import Flask, request
import sqlalchemy
from sqlalchemy.orm import sessionmaker

from weblab.admin.script import weblab_create, Creation

from celery import task, Task

#from wcloud import deploymentsettings
import deploymentsettings

from wcloud.models import User, Entity

import redis_tasks
import db_tasks

# TODO: Currently "models" is trying to load the "wcloud" database. A way to override that
# session when in tests would be very useful.


# TODO: Remove the dependency on this.
import wcloud.config.wcloud_settings_default as wcloud_settings_default
import wcloud.config.wcloud_settings as wcloud_settings

app = Flask(__name__)
app.config.from_object(wcloud_settings_default)
app.config.from_object(wcloud_settings)
app.config.from_envvar('WCLOUD_SETTINGS', silent=True)


def connect_to_database(user, passwd, db_name):
    """
    Connects to the MySQL database using the specified username and password.
    Assumes the DB is in localhost and listening on port 3306.

    @param user: Username, which will need to be root to create new databases.
    @param passwd: Password for the Username.

    @return: Engine object and the Session() maker.
    """
    conn_string = 'mysql://%s:%s@%s:%d' % (user, passwd, '127.0.0.1', 3306)
    engine = sqlalchemy.create_engine(conn_string)
    engine.execute("SELECT 1")
    engine.execute("USE %s" % db_name)

    Session = sessionmaker()
    Session.configure(bind=engine)

    return engine, Session


@task(bind=True)
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
    self.update_state(state="PROGRESS", meta={"action": "Preparing system"})

    # Override the items in the config that are contained in the explicit wcloud_settings dictionary.
    app.config.update(wcloud_settings)

    # Connect to the database
    engine, Session = connect_to_database(app.config["DB_USERNAME"], app.config["DB_PASSWORD"], app.config["DB_NAME"])
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

    settings[Creation.BASE_URL] = 'w/' + entity.base_url

    if user.entity.logo != None and user.entity.logo != "":
        settings[Creation.LOGO_PATH] = tmp_logo.name
    else:
        settings[Creation.LOGO_PATH] = None

    # TODO: Change the DB system.

    # Create a new database and assign the DB name.
    # TODO: Unhardcode / tidy this up.
    db_name = db_tasks.create_db("root", "password", "wcloudtest", app.config["DB_USERNAME"], app.config["DB_PASSWORD"])
    entity.db_name = db_name
    session.commit()

    # settings[Creation.DB_NAME] = 'wcloud%s' % entity.id
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
        redis_tasks.deploy_redis_instance("../redis_env", settings[Creation.COORD_REDIS_PORT])
    except (redis_tasks.AlreadyDeployedException) as ex:
        pass

    redis_tasks.check_redis_deployment("../redis_env", settings[Creation.COORD_REDIS_PORT])


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

    return settings


# TODO: Fix this.
def exit_func(code):
    traceback.print_exc()
    # print "Output:", output.getvalue()
    raise Exception("Error creating weblab: %s" % code)


@task(bind=True)
def create_weblab_environment(self, directory, settings):
    """
    2. Create the full WebLab-Deusto environment.
    """

    self.update_state(state="PROGRESS", meta={"action": "Creating deployment directory"})

    output = StringIO()
    command_output = StringIO()



    results = weblab_create(directory,
                            settings,
                            command_output,
                            command_output,
                            exit_func)

    time.sleep(0.5)

    # Don't know what was this done originally for.
    # settings.update(task)


@task(bind=True)
def deploy_weblab_instance(self):
    prepare_system()
    create_weblab_environment()

    #
    #     ##########################################################
    #     #
    #     # 3. Configure the web server
    #     #
    #     output.write("[Done]\nConfiguring web server...")
    #
    #     # Create Apache configuration
    #     with open(os.path.join(app.config['DIR_BASE'],
    #                            deploymentsettings.APACHE_CONF_NAME), 'a') as f:
    #         conf_dir = results['apache_file']
    #         f.write('Include "%s"\n' % conf_dir)
    #
    #     # Reload apache
    #     opener = urllib2.build_opener(urllib2.ProxyHandler({}))
    #     print(opener.open('http://127.0.0.1:%s/' % app.config['APACHE_RELOADER_PORT']).read())
    #
    #     ##########################################################
    #     #
    #     # 4. Register and start the new WebLab-Deusto instance
    #     #
    #     output.write("[Done]\nRegistering and starting instance...")
    #
    #     global response
    #     response = None
    #     is_error = False
    #
    #     def register():
    #         global response
    #         import urllib2
    #         import traceback
    #
    #         try:
    #             url = 'http://127.0.0.1:%s/deployments/' % app.config['WEBLAB_STARTER_PORT']
    #             req = urllib2.Request(url, json.dumps({'name': entity.base_url}), {'Content-Type': 'application/json'})
    #             response = opener.open(req).read()
    #         except:
    #             is_error = True
    #             response = "There was an error registering or starting the service. Contact the administrator"
    #             traceback.print_exc()
    #
    #     print "Executing 'register' in other thread...",
    #     t = threading.Thread(target=register)
    #     t.start()
    #     while t.isAlive() and response is None:
    #         time.sleep(1)
    #         output.write(".")
    #     print "Ended. is_error=%s; response=%s" % (is_error, response)
    #
    #     if is_error:
    #         raise Exception(response)
    #
    #     ##########################################################
    #     #
    #     # 5. Service deployed. Configure the response
    #     #
    #
    #     output.write("[Done]\n\nCongratulations, your system is ready!")
    #     task['url'] = task['url_root'] + entity.base_url
    #     self.task_status[task['task_id']] = TaskManager.STATUS_FINISHED
    #
    #     #
    #     # Save in database data like last port
    #     # Note: this is thread-safe since the task manager is
    #     # monothread
    #     user.entity.start_port_number = results['start_port']
    #     user.entity.end_port_number = results['end_port']
    #
    #     # Save
    #     db.session.add(user)
    #     db.session.commit()
    #
    # except:
    #     import traceback
    #
    #     print(traceback.format_exc())
    #     sys.stdout.flush()
    #     self.task_status[task['task_id']] = TaskManager.STATUS_ERROR
    #
    #     # Revert changes:
    #     #
    #     # 1. Delete the directory
    #     shutil.rmtree(task['directory'], ignore_errors=True)
    #
    #     #
    #     # 2. Remove from apache and reload
    #     # TODO
    #
    #     #
    #     # 3. Remove from the instances to be loaded
    #     # TODO
    #
    #     #
    #     # 4. Remove from the database
    #     # TODO


if __name__ == "__main__":
    pass




######################################
#
# UNIT TESTS BELOW
#
######################################

from nose.tools import assert_is_not_none


class TestWcloudTasks(unittest.TestCase):

    wcloud_settings = {
        "DB_USERNAME": "weblabtest",
        "DB_PASSWORD": "weblabtest",
        "DB_NAME": "wcloudtest"
    }

    def test_prepare_system(self):
        prepare_system("testuser@testuser.com", "admin", "Administrador", "password", "admin@admin.com",
                       self.wcloud_settings)

    def test_create_weblab_environment(self):

        settings = prepare_system("testuser@testuser.com", "admin", "Administrador", "password", "admin@admin.com",
               self.wcloud_settings)

        create_weblab_environment("weblabtest", settings)


    def setUp(self):
        import wcloud.test.prepare as prepare

        prepare.prepare_test_database("root", "password")

    def tearDown(self):

        # Delete the deployed directory.
        try:
            shutil.rmtree("weblabtest")
        except:
            pass

