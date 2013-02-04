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
import signal
path_aux = sys.path[0].split('/')
path_aux = os.path.join('/', *path_aux[0:len(path_aux)-1])
sys.path.append(path_aux)
import shutil
import Queue
import threading
import time
import traceback
import subprocess
import urllib2
import json
import uuid
import tempfile
from cStringIO import StringIO

from flask import Flask, request

from weblab.admin.script import weblab_create, Creation
from wcloud import deploymentsettings, db
from wcloud.models import User, Entity

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
        self.task_data   = {}        # Task data ( {'stdout' : ..., 'stderr' : ... } )
        self.lock = threading.Lock()
        self.task_ids = {}
    
    def submit_task(self, task):
        """Adds a task to the queue of jobs and initializes all the neccessary
        data of the task status
        
        :param task: A dict with all the neccessary data to run the job
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
                user = User.query.filter_by(email=task[u'email']).first()
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
                settings =  deploymentsettings.DEFAULT_DEPLOYMENT_SETTINGS.copy()
                
                settings[Creation.BASE_URL]       = 'w/' + entity.base_url

                settings[Creation.LOGO_PATH]      = tmp_logo.name

                settings[Creation.DB_NAME]        = 'wcloud%s' % entity.id
                settings[Creation.DB_USER]        = app.config['DB_USERNAME']
                settings[Creation.DB_PASSWD]      = app.config['DB_PASSWORD']

                settings[Creation.ADMIN_USER]     = task['admin_user']
                settings[Creation.ADMIN_NAME]     = task['admin_name']
                settings[Creation.ADMIN_PASSWORD] = task['admin_password']
                settings[Creation.ADMIN_MAIL]     = task['admin_email']

                last_port = Entity.last_port()
                if last_port is None: 
                    last_port = deploymentsettings.MIN_PORT

                settings[Creation.START_PORTS] =  last_port + 1
                settings[Creation.SYSTEM_IDENTIFIER] = user.entity.name
                settings[Creation.ENTITY_LINK] = user.entity.link_url

                #########################################################
                # 
                # 2. Create the full WebLab-Deusto environment
                # 
                output.write("[Done]\nCreating deployment directory...")
                results = weblab_create(task['directory'] ,
                                        settings,
                                        task['stdout'],
                                        task['stderr'],
                                        task['exit_func'])
                time.sleep(0.5)
                
                settings.update(task)

                ##########################################################
                # 
                # 3. Configure the web server
                # 
                output.write("[Done]\nConfiguring web server...")
                
                # Create Apache configuration
                with open(os.path.join(app.config['DIR_BASE'],
                            deploymentsettings.APACHE_CONF_NAME), 'a') as f:
                    conf_dir = results['apache_file']
                    f.write('Include "%s"\n' % conf_dir) 
                
                # Reload apache
                opener = urllib2.build_opener(urllib2.ProxyHandler({}))
                print(opener.open('http://127.0.0.1:%s/' % app.config['APACHE_RELOADER_PORT']).read())
                
                ##########################################################
                # 
                # 4. Register and start the new WebLab-Deusto instance
                #
                output.write("[Done]\nRegistering and starting instance...")
                
                global response
                response = None
                is_error = False
                def register():
                    global response
                    import urllib2
                    import traceback
                    try:
                        url = 'http://127.0.0.1:%s/deployments/' % app.config['WEBLAB_STARTER_PORT']
                        req = urllib2.Request(url, json.dumps({'name' : entity.base_url}), {'Content-Type': 'application/json'})
                        response = opener.open(req).read()
                    except:
                        is_error = True
                        response = "There was an error registering or starting the service. Contact the administrator"
                        traceback.print_exc()

                print "Executing 'register' in other thread...",
                t = threading.Thread(target=register)
                t.start()
                while t.isAlive() and response is None:
                    time.sleep(1)
                    output.write(".")
                print "Ended. is_error=%s; response=%s" % (is_error, response)

                if is_error:
                    raise Exception(response)

                ##########################################################
                # 
                # 5. Service deployed. Configure the response
                #
                
                output.write("[Done]\n\nCongratulations, your system is ready!")
                task['url'] = task['url_root'] + entity.base_url
                self.task_status[task['task_id']] = TaskManager.STATUS_FINISHED
                
                # 
                # Save in database data like last port
                # Note: this is thread-safe since the task manager is 
                # monothread
                user.entity.start_port_number = results['start_port']
                user.entity.end_port_number = results['end_port']
                
                # Save
                db.session.add(user)
                db.session.commit()
                
            except:
                import traceback
                print(traceback.format_exc())
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


app = Flask(__name__)

@app.route('/task/', methods = ['GET','POST'])
def create_task():
    if request.method == 'GET':
        return 'POST expected'

    task = request.json

    print "Creating new task: %s" % task

    output = StringIO()
    command_output = StringIO()
    
    def exit_func(code):
        traceback.print_exc()
        print "Output:",output.getvalue() 
        raise Exception("Error creating weblab: %s" % code)
    
    # Create task settings and submit to the task manager
    task.update({ 'stdout'        : command_output,
                        'stderr'        : command_output,
                        'output'        : output,
                        'exit_func'     : exit_func,
                        'url'           : 'not available yet'})

    # Submit task
    task_id = task_manager.submit_task(task)

    # Send response to client with the client id
    print "Task created: ",  task_id
    return task_id

@app.route('/task/<task_id>/')
def get_task(task_id):
    task_status = task_manager.retrieve_task_status(task_id)
    task_data   = task_manager.retrieve_task_data(task_id)
    if task_status:
        response = {
            'status' : task_status,
            'output' : task_data['output'].getvalue(),
            'url'    : task_data['url'],
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
    import wcloud.default_settings as default_settings
    app.config.from_object(default_settings)
    app.config.from_envvar('WCLOUD_SETTINGS', silent=True)

    main()
    try:
        app.run(port = app.config['TASK_MANAGER_PORT'])
    except:
        task_manager.shutdown()
        raise
    else:
        print "Flask finished"
        task_manager.shutdown()

