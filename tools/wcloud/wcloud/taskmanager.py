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

"""
TaskManager: monothread system that deploys WebLab-Deusto instances.

This system is monothread (and therefore, it can not be deployed as
a regular WSGI system with multiple processes) and listens in local.
Whenever a local client requests it, it will create a new WebLab-Deusto
configuration, providing a RESTful API for retrieving the current status
of the deployment.
"""

import os
import sys
from wcloud.tasks import wcloud_tasks

path_aux = sys.path[0].split('/')
path_aux = os.path.join('/', *path_aux[0:len(path_aux) - 1])
sys.path.append(path_aux)
import shutil
import Queue
import threading
import traceback
import json
import uuid
from cStringIO import StringIO

from flask import Flask, request

from weblab.admin.script import Creation


class TaskManager(threading.Thread):
    STATUS_WAITING = 'waiting'
    STATUS_STARTED = 'started'
    STATUS_FINISHED = 'finished'
    STATUS_ERROR = 'error'

    def __init__(self):
        """Task manager constructor"""
        threading.Thread.__init__(self)
        self.queue = Queue.Queue()   # Queue
        self._shutdown = False        # While not shutdown run task manager
        self.task_status = {}        # Task status ('waiting', 'started', 'finished'...)
        self.task_data = {}        # Task data ( {'stdout' : ..., 'stderr' : ... } )
        self.lock = threading.Lock()
        self.task_ids = {}

    def submit_task(self, task):
        """Adds a task to the queue of jobs and initializes all the neccessary
        data of the task status
        
        :param task: A dict with all the necessary data to run the job
        """

        with self.lock:
            task_id = (str(uuid.uuid4()))
            while task_id in self.task_status:
                task_id = (str(uuid.uuid4()))

            # Store data
            self.task_status[task_id] = TaskManager.STATUS_WAITING
            self.task_data[task_id] = task
            task['task_id'] = task_id

            self.queue.put(task)
            return task_id


    def retrieve_task_status(self, task_id):
        with self.lock:
            return self.task_status.get(task_id)

    def retrieve_task_data(self, task_id):
        with self.lock:
            return self.task_data.get(task_id)


    def shutdown(self):
        """Shuts down the task manager (stop task manager)"""

        self._shutdown = True

    def run(self):
        """Loop of the task manager. pops a job in each iteration and executes
        the task until no tasks remain in the queue. The task manager will
        remain executing and awaiting for a task/job until _shutdown is true.
        This avoids concurrency problems: no more than one task will be executed
        at the same time.
        """

        while not self._shutdown:
            try:
                task = self.queue.get(timeout=0.1)
            except Queue.Empty:
                continue

            print "Processing task: ", task['task_id']
            output = task['output']
            output.write('Starting process...')
            self.task_status[task['task_id']] = TaskManager.STATUS_STARTED
            try:

                ######################################
                # 
                # 1. Prepare the system
                #
                output.write('[done]\nPreparing requirements...')
                settings = wcloud_tasks.prepare_system.delay(task[u'email'], task['admin_user'], task['admin_name'], task['admin_password'], task['admin_email'], {}).get()


                #########################################################
                # 
                # 2. Create the full WebLab-Deusto environment
                #
                output.write("[Done]\nCreating deployment directory...")
                creation_results = wcloud_tasks.create_weblab_environment.delay(task["directory"], settings).get()
                # TODO: settings vs wcloud_settings. It is confusing.


                ##########################################################
                # 
                # 3. Configure the web server
                # 
                output.write("[Done]\nConfiguring web server...")
                wcloud_tasks.configure_web_server.delay(creation_results).get()


                ##########################################################
                # 
                # 4. Register and start the new WebLab-Deusto instance
                #
                output.write("[Done]\nRegistering and starting instance...")
                wcloud_tasks.register_and_start_instance.delay(task[u'email'], {}).get()


                ##########################################################
                # 
                # 5. Service deployed. Configure the response
                #
                output.write("[Done]\n\nCongratulations, your system is ready!")
                start_port, end_port = creation_results["start_port"], creation_results["end_port"]
                wcloud_tasks.finish_deployment.delay(task[u'email'], settings, start_port, end_port, {}).get()

                task['url'] = task['url_root'] + settings[Creation.BASE_URL]
                self.task_status[task['task_id']] = TaskManager.STATUS_FINISHED

            except:
                import traceback

                print(traceback.format_exc())
                sys.stdout.flush()
                self.task_status[task['task_id']] = TaskManager.STATUS_ERROR

                # Revert changes:
                # 
                # 1. Delete the directory 
                shutil.rmtree(task['directory'], ignore_errors=True)

                # 
                # 2. Remove from apache and reload
                # TODO

                # 
                # 3. Remove from the instances to be loaded
                # TODO

                # 
                # 4. Remove from the database
                # TODO


app = Flask(__name__)


@app.route('/task/', methods=['GET', 'POST'])
def create_task():
    if request.method == 'GET':
        return 'POST expected'

    task = request.json

    print "Creating new task: %s" % task

    output = StringIO()
    command_output = StringIO()

    def exit_func(code):
        traceback.print_exc()
        print "Output:", output.getvalue()
        raise Exception("Error creating weblab: %s" % code)

    # Create task settings and submit to the task manager
    task.update({'stdout': command_output,
                 'stderr': command_output,
                 'output': output,
                 'exit_func': exit_func,
                 'url': 'not available yet'})

    # Submit task
    task_id = task_manager.submit_task(task)

    # Send response to client with the client id
    print "Task created: ", task_id
    return task_id


@app.route('/task/<task_id>/')
def get_task(task_id):
    task_status = task_manager.retrieve_task_status(task_id)
    task_data = task_manager.retrieve_task_data(task_id)
    if task_status:
        response = {
            'status': task_status,
            'output': task_data['output'].getvalue(),
            'url': task_data['url'],
        }
    else:
        response = {}

    return json.dumps(response)


task_manager = None


def main():
    global task_manager
    task_manager = TaskManager()
    task_manager.start()

    def handler(*args, **kwargs):
        task_manager.shutdown()

    print("Task manager started in  127.0.0.1:%d" % app.config['TASK_MANAGER_PORT'])


if __name__ == "__main__":
    import wcloud.config.wcloud_settings as wcloud_settings
    import wcloud.config.wcloud_settings_default as wcloud_settings_default

    app.config.from_object(wcloud_settings_default)
    app.config.from_object(wcloud_settings)
    app.config.from_envvar('WCLOUD_SETTINGS', silent=True)

    main()
    try:
        app.run(port=app.config['TASK_MANAGER_PORT'])
    except:
        task_manager.shutdown()
        raise
    else:
        print "Flask finished"
        task_manager.shutdown()

