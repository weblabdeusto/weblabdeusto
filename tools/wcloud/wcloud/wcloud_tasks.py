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

from weblab.admin.script import weblab_create, Creation

from celery import task, Task

#from wcloud import deploymentsettings, db
import deploymentsettings
from models import User, Entity


# TODO: Remove the dependency on this.
import default_settings
app = Flask(__name__)
app.config.from_object(default_settings)
app.config.from_envvar('WCLOUD_SETTINGS', silent=True)


@task(bind=True)
def prepare_system(self, wcloud_user_email, admin_user, admin_name, admin_password, admin_email):
    """
    Prepare the system.
    """
    self.update_state(state="PROGRESS", meta={"action": "Preparing system"})
    user = User.query.filter_by(email=wcloud_user_email).first()
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

    settings[Creation.LOGO_PATH] = tmp_logo.name

    settings[Creation.DB_NAME] = 'wcloud%s' % entity.id
    settings[Creation.DB_USER] = app.config['DB_USERNAME']
    settings[Creation.DB_PASSWD] = app.config['DB_PASSWORD']

    databases_per_port = app.config['REDIS_DBS_PER_PORT']
    initial_redis_port = app.config['REDIS_START_PORT']

    settings[Creation.COORD_REDIS_DB] = entity.id % databases_per_port
    settings[Creation.COORD_REDIS_PORT] = initial_redis_port + entity.id / databases_per_port

    settings[Creation.ADMIN_USER] = admin_user
    settings[Creation.ADMIN_NAME] = admin_name
    settings[Creation.ADMIN_PASSWORD] = admin_password
    settings[Creation.ADMIN_MAIL] = admin_email

    last_port = Entity.last_port()
    if last_port is None:
        last_port = deploymentsettings.MIN_PORT

    settings[Creation.START_PORTS] = last_port + 1
    settings[Creation.SYSTEM_IDENTIFIER] = user.entity.name
    settings[Creation.ENTITY_LINK] = user.entity.link_url



@task(bind=True)
def deploy_weblab_instance(self):

    prepare_system()

    #
    #     #########################################################
    #     #
    #     # 2. Create the full WebLab-Deusto environment
    #     #
    #     output.write("[Done]\nCreating deployment directory...")
    #     results = weblab_create(task['directory'],
    #                             settings,
    #                             task['stdout'],
    #                             task['stderr'],
    #                             task['exit_func'])
    #     time.sleep(0.5)
    #
    #     settings.update(task)
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

    def test_prepare_system(self):
        prepare_system("admin", "Administrador", "password", "admin@admin.com")

    def setUp(self):
        pass

    def tearDown(self):
        pass

