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

import os
import sys
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
        self.setDaemon(True)
        self.queue = Queue.Queue()   # Queue
        self.shutdown = False        # While not shutdown run task manager
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
        
        self.shutdown = True
    
    def run(self):
        """Loop of the task manager. pops a job in each iteration and executes
        the task until no tasks remain in the queue. The task manager will
        remain executing and awaiting for a task/job until shutdown is true
        """
        
        while (not self.shutdown):
            task = self.queue.get()
            print "Processing task: ", task['task_id']
            self.task_status[task['task_id']] = TaskManager.STATUS_STARTED
            try:
                user = User.query.filter_by(email=task[u'email']).first()
                entity = user.entity
                
                #Create the entity
                settings =  deploymentsettings.DEFAULT_DEPLOYMENT_SETTINGS
                
                settings[Creation.BASE_URL]   = entity.base_url

                settings[Creation.DB_NAME]    = 'wcloud%s' % entity.id
                settings[Creation.DB_USER]    = app.config['DB_USERNAME']
                settings[Creation.DB_PASSWD]  = app.config['DB_PASSWORD']

                settings[Creation.ADMIN_USER] = task['admin_user']
                settings[Creation.ADMIN_NAME] = task['admin_name']
                settings[Creation.ADMIN_PASSWORD] = task['admin_password']
                settings[Creation.ADMIN_MAIL] = task['admin_email']

                last_port = Entity.last_port()
                if last_port is None: 
                    last_port = deploymentsettings.MIN_PORT

                settings[Creation.START_PORTS] =  last_port + 1
                settings[Creation.SYSTEM_IDENTIFIER] = user.entity.name
                settings[Creation.ENTITY_LINK] = user.entity.link_url
                results = weblab_create(task['directory'] ,
                                        settings,
                                        task['stdout'],
                                        task['stderr'],
                                        task['exit_func'])
                time.sleep(0.5)
                
                settings.update(task)
                
                # Create Apache configuration
                with open(os.path.join(deploymentsettings.DIR_BASE,
                            deploymentsettings.APACHE_CONF_NAME), 'a') as f:
                    conf_dir = results['apache_file']
                    f.write('Include "%s"\n' % conf_dir) 
                
                # Reload apache
                print(urllib2.urlopen(deploymentsettings.APACHE_RELOAD_SERVICE)\
                      .read())
                
                # Add instance to weblab instance runner daemon
                with open(os.path.join(deploymentsettings.DIR_BASE,
                                      'instances.txt'), 'a+') as f:
                    
                    #If the line already exists then don't add
                    
                    found = False
                    for line in f:
                        if task['directory'] in line:
                            found = True
                            break
                        
                    if not found: f.write('%s\n' % task['directory']) 
                
                # Start now the new weblab instance
                process = subprocess.Popen(['nohup','weblab-admin','start',
                            task['directory']],
                    stdout = open(os.path.join(task['directory'], \
                                               'stdout.txt'), 'w'),
                    stderr = open(os.path.join(task['directory'], \
                                               'stderr.txt'), 'w'),
                    stdin = subprocess.PIPE)
                
                time.sleep(30)
                if process.poll() is not None: raise Exception
                
                self.task_status[task['task_id']] = TaskManager.STATUS_FINISHED
            
                #Copy image
                img_dir = os.path.dirname(results['img_file'])
                os.makedirs(img_dir)
                f = open(results['img_file'], 'w+')
                f.write(user.entity.logo)
                f.close
                
                #Save in database data like last port
                user.entity.start_port_number = results['start_port']
                user.entity.end_port_number = results['end_port']
                # Save
                db.session.add(user)
                db.session.commit()
                
            except:
                import traceback
                print(traceback.format_exc())
                self.task_status[task['task_id']] = TaskManager.STATUS_ERROR

                shutil.rmtree(task['directory'], ignore_errors=True)


app = Flask(__name__)

@app.route('/task/<task_id>/')
def get_task(task_id):
    task_status = task_manager.retrieve_task_status(task_id)
    task_data   = task_manager.retrieve_task_data(task_id)
    if task_status:
        response = {
            'status' : task_status,
            'output' : task_data['output'].getvalue()
        }
    else:
        response = {}
        
    return json.dumps(response)

@app.route('/task/', methods = ['GET','POST'])
def create_task():
    if request.method == 'GET':
        return 'POST expected'

    settings = request.json

    print "Creating new task: %s" % settings

    output = StringIO()
    
    def exit_func(code):
        traceback.print_exc()
        print "Output:",output.getvalue() 
        raise Exception("Error creating weblab: %s" % code)
    
    # Create task settings and submit to the task manager
    settings_update = { 'stdout'        : output,
                        'stderr'        : output,
                        'output'        : output,
                        'exit_func'     : exit_func }

    settings.update(settings_update)

    # Submit task
    task_id = task_manager.submit_task(settings)

    # Send response to client with the client id
    print "Task created: ",  task_id
    return task_id

task_manager = None

def main():
    global task_manager
    task_manager = TaskManager()
    task_manager.start()
    print("Task manager started in  127.0.0.1:%d" % app.config['TASK_MANAGER_PORT'])



if __name__ == "__main__":
    import settings
    app.config.from_object(settings)

    main()
    app.run(debug = True, port = settings.TASK_MANAGER_PORT)

