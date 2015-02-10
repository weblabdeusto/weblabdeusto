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
# Author: Pablo Orduña <pablo.orduna@deusto.es>
# Author: Luis Rodriguez <luis.rodriguezgil@deusto.es>
#
# These authors would like to acknowledge the Spanish Ministry of science
# and innovation, for the support in the project IPT-2011-1558-430000
# "mCloud: http://innovacion.grupogesfor.com/web/mcloud"
#

import sys
from wcloud.actions import wcloud_actions
from wcloud.tasks.celery_app import celery_app

import shutil
import traceback
import cStringIO as StringIO

from weblab.admin.script import Creation

def _store_progress(task, result, output, step):
    result['output'] = output.getvalue()
    result['step'] = step
    if not task.request.called_directly:
        task.update_state(state='PROGRESS', meta=result)

class TransactionProcessor(object):
    def __init__(self, task, result, output):
        self.rollback_functions = []
        self.task = task 
        self.result = result
        self.output = output
        self.message = ""
        self.step = 0
 
    def register_rollback(self, rollback_func, *args, **kwargs):
        self.rollback_functions.append((rollback_func, args, kwargs))
 
    def __call__(self, message):
        self.message = message
        return self
 
    def __enter__(self):
        self.output.write(self.message + "... ")
        print(self.message + "... ")
        _store_progress(self.task, self.result, self.output, self.step)
        return self
 
    def __exit__(self, error_type, error_instance, tb):
        if error_instance is not None:
            print("[error]\n")
            traceback.print_exc()
            for func, args, kwargs in self.rollback_functions[::-1]:
                try:
                    func(*args, **kwargs)
                except:
                    traceback.print_exc()
            
            raise Exception("Error while %s" % self.message)
        else: 
            print("[done]\n")
            self.output.write("[done]\n")
            _store_progress(self.task, self.result, self.output, self.step)
        self.step += 1

@celery_app.task(bind=True, name = 'deploy_weblab_instance')
def deploy_weblab_instance(self, directory, email, admin_user, admin_name, admin_email, admin_password, base_url):
    """
    Deploys a new WebLab instance with the specified parameters.

    :param self: Reference to the Task itself, provided by Celery automatically.
    :param directory: The directory (file system) on which the WebLab-Deusto instance will be created.
    :param email: wCloud login of the user creating this instance.
    :param admin_user: generated WebLab-Deusto instance admin login.
    :param admin_name: generated WebLab-Deusto instance admin full name.
    :param admin_email: generated WebLab-Deusto instance admin e-mail.
    :param admin_password: generated WebLab-Deusto instance admin password.
    :param base_url: Relative URL of the system (e.g., /w/deusto/ or whatever).
    :return:
    """
    output = StringIO.StringIO()
    result = {'output' : output.getvalue(), 'step' : 0, 'email' : email }
    transaction = TransactionProcessor(self, result, output)

    ######################################
    #
    # 1. Prepare the system
    #
    transaction.register_rollback(wcloud_actions.rollback_prepare_system, email)

    with transaction("preparing requirements"):
        current_instance_settings = wcloud_actions.prepare_system(email, admin_user, admin_name, admin_password, admin_email)

    #########################################################
    #
    # 2. Create the full WebLab-Deusto environment
    #
    transaction.register_rollback(wcloud_actions.rollback_create_weblab_environment, directory)

    with transaction("creating deployment directory"):
        creation_results = wcloud_actions.create_weblab_environment(directory, current_instance_settings)

    ##########################################################
    #
    # 3. Configure the web server
    #
    transaction.register_rollback(wcloud_actions.rollback_configure_web_server, creation_results)

    with transaction("configuring web server"):
        wcloud_actions.configure_web_server(creation_results)

    ##########################################################
    #
    # 4. Register and start the new WebLab-Deusto instance
    #
    transaction.register_rollback(wcloud_actions.rollback_register_and_start_instance, directory)

    with transaction("registering and starting instance"):
        wcloud_actions.register_and_start_instance(email, directory)

    ##########################################################
    #
    # 5. Check the deployment
    #
    transaction.register_rollback(wcloud_actions.rollback_finish_deployment, email)

    with transaction("checking deployment"):
        wcloud_actions.finish_deployment(email, creation_results["start_port"], creation_results["end_port"])
    
    ##########################################################
    #
    # 6. Service deployed. Configure the response
    #

    output.write("\nCongratulations, your system is ready!")
    result['output'] = output.getvalue()
    result['url'] = base_url + current_instance_settings[Creation.BASE_URL]
    return result

