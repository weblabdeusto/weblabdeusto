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
import Queue
import threading
import time
import traceback
import subprocess
import urllib2
import BaseHTTPServer
import re
import json
import uuid
import mmap
from cStringIO import StringIO

from weblab.admin.script import weblab_create, Creation
from wlcloud import deploymentsettings, db
from wlcloud.models import User, Entity


PORT = 1661

class TaskManagerServer(BaseHTTPServer.BaseHTTPRequestHandler):
    """ Simple server for calling the task manager process.
    API:
        - GET /task/{identifier} - Gets task with identifier 
        - POST /task - creates new task and responds with the identifier
        - GET /task/{identifier}/stdout - gets the stdout from a concrete task
        - GET /task/{identifier}/stderror - get the stdout from a concrete task
    """
    
    tasks = {}

    def do_GET(self):
        
        self.send_response(200)
        self.end_headers()
        
        try:
            # /task/{identifier}
            match = re.match(r"/task/([\w-]+)/?$", self.path)
            if match is not None:
                results = dict(TaskManagerServer.tasks[match.group(1)])
                del results['stdout']
                del results['stderr']
                del results['exit_func']
                self.wfile.write(json.dumps(results))
                return
                
            # /task/{identifier}/stdout
            match = re.match(r"/task/([\w-]+)/stdout/?$", self.path)
            if match is not None:
                stringio = TaskManagerServer.tasks[match.group(1)]['stdout']
                self.wfile.write(stringio.getvalue())
                return 
                
            # /task/{identifier}/stderror
            match = re.match(r"/task/([\w-]+)/stderror/?$", self.path)
            if match is not None:
                stringio = TaskManagerServer.tasks[match.group(1)]['stderr']
                self.wfile.write(stringio.getvalue())
                return
        except:
            pass
        self.send_response(400)
        self.end_headers()
        self.wfile.write('ERROR')        
    
    def do_POST(self):
        # /task
        match = re.match(r"/task/?$", self.path)
        if match is not None:
            
            #Decode json
            post_vars = self.rfile.read(int(self.headers['Content-Length']))
            settings = json.loads(post_vars)
            
            #create needed resources
            task_id = (str(uuid.uuid4()))
            stdout = StringIO()
            stderr = StringIO()
            
            def exit_func(code):
                raise Exception("Error creating weblab: %s" % code)
            
            #create task settings and submit to the task manager
            settings_update = {'stdout': stdout,
                                'stderr': stderr,
                                'exit_func': exit_func,
                                'task_id': task_id}
        
            settings.update(settings_update)

            #Submit task
            task_manager.submit_task(settings)
        
            #send response to client with the client id
            self.send_response(200)
            self.end_headers()        
            self.wfile.write(task_id)
            return
        
        self.send_response(400)
        self.end_headers()
        self.wfile.write('ERROR')

class TaskManager(threading.Thread):
    

    STATUS_WAITING = 'waiting'
    STATUS_STARTED = 'started'
    STATUS_FINISHED = 'finished'
    STATUS_ERROR = 'error'
    
    def __init__(self):
        """Task manager constructor"""
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.queue = Queue.Queue() # Queue
        self.shutdown = False # While not shutdown run task manager
        self.task_output = {} # Task execution results
        self.task_status = {} # Task status ('waiting', 'started', 'finished')
        self.task_counter = 0 # Counter of the tasks
        self.lock = threading.Lock()
    
    def submit_task(self, task):
        """Adds a task to the queue of jobs and initializes all the neccessary
        data of the task status
        
        :param task: A dict with all the neccessary data to run the job
        """
        
        with self.lock:
            self.task_counter += 1
            self.task_status[self.task_counter] = TaskManager.STATUS_WAITING
            self.queue.put(task)
            
            return self.task_counter
        
    
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
            self.task_status[task['task_id']] = TaskManager.STATUS_STARTED
            try:
                user = User.query.filter_by(email=task[u'email']).first()
                
                #Create the entity
                settings =  deploymentsettings.DEFAULT_DEPLOYMENT_SETTINGS
                
                settings[Creation.BASE_URL] = user.entity.base_url
                settings[Creation.DB_NAME] = 'wlcloud' + \
                                        str(User.total_users() + 1)
                settings[Creation.ADMIN_USER] = task['admin_user']
                settings[Creation.ADMIN_NAME] = task['admin_name']
                settings[Creation.ADMIN_PASSWORD] = task['admin_password']
                settings[Creation.ADMIN_MAIL] = task['admin_email']
                last_port = Entity.last_port()
                if last_port is None: last_port = deploymentsettings.MIN_PORT
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
                TaskManagerServer.tasks[task['task_id']] = settings
                
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

if __name__ == "__main__":
    task_manager = TaskManager()
    task_manager.start()
    print("Task manager started in  127.0.0.1:%d" % PORT)
    x = BaseHTTPServer.HTTPServer(('127.0.0.1', PORT), TaskManagerServer)    
    x.serve_forever()
