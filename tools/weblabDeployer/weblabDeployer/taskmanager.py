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
import Queue
import threading
import StringIO
import time
import traceback
import subprocess
import urllib2

from weblab.admin.script import weblab_create

from weblabDeployer import deploymentsettings

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
            self.task_output[self.task_counter] = StringIO.StringIO()
            task['task_id'] = self.task_counter
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
                #Create the entity
                weblab_create(task['directory'] , task['options'],
                    task['stdout'], task['stderr'], task['exit_func'])
                time.sleep(0.5)
                
                # Create Apache configuration
                with open(os.path.join(deploymentsettings.DIR_BASE,
                            deploymentsettings.APACHE_CONF_NAME), 'a') as f:
                    conf_dir = task['directory'] + \
                                '/httpd/apache_weblab_generic.conf'
                    f.write('Include "%s"\n' % conf_dir) # TODO: apache_weblab_generic should be a constant
                
                # Reload apache
                print(urllib2.urlopen('http://127.0.0.1:22110').read())
                
                # Add instance to weblab instance runner daemon
                f = open(os.path.join(deploymentsettings.DIR_BASE,
                                      'instances.txt'), 'a')
                f.write('%s\n' % task['directory'])
                
                # Start now the new weblab instance
                process = subprocess.Popen(['nohup','weblab-admin','start',
                            task['directory']],
                    stdout = open(os.path.join(task['directory'], \
                                               'stdout.txt'), 'w'),
                    stderr = open(os.path.join(task['directory'], \
                                               'stderr.txt'), 'w'),
                    stdin = subprocess.PIPE)
                
                self.task_status[task['task_id']] = TaskManager.STATUS_FINISHED
            
                #Copy image
            except:
                import traceback
                print(traceback.format_exc())
                self.task_status[task['task_id']] = TaskManager.STATUS_ERROR