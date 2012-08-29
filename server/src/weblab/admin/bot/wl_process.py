#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2005 onwards University of Deusto
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#
# This software consists of contributions made by many individuals,
# listed below:
#
# Authors: Jaime Irurzun <jaime.irurzun@gmail.com>
#          Pablo Orduña <pablo@ordunya.com>
#

import StringIO
import os
import traceback
import glob
import subprocess
import time
import urllib2
import voodoo.killer as killer

class WebLabProcess(object):

    def __init__(self, launch_file, host, options, base_location = '', verbose = False):
        super(WebLabProcess, self).__init__()

        self.out = 'Not started'
        self.err = 'Not started'

        if os.sep != '/' and '/' in launch_file and os.sep in launch_file:
            raise Exception("Both %s and / found in launch_file (%s), only one expected" % (os.sep, launch_file))

        self.host        = host
        self.verbose       = verbose

        normalized_launch_file = launch_file.replace('/', os.sep) 
        
        self.launch_file = os.path.basename(normalized_launch_file)
        self.launch_path = os.path.abspath(os.path.dirname(normalized_launch_file))

        if not os.path.exists(self.launch_path):
            raise Exception("Expected launch path %s not found" % self.launch_path)

        debugging_file = os.path.join(self.launch_path, 'debugging.py')

        if not os.path.exists(debugging_file):
            raise Exception("Expected debugging file %s not found" % debugging_file)

        variables = {}
        execfile(debugging_file, variables, variables)
        self.ports = variables['PORTS']
        # self.base_location = variables.get('BASE_URL', base_location)
        self.base_location = ''

        # 
        # After running the bot several times, the amount of files stored and logs
        # increase a lot. We remove them in the beginning. We should do the same
        # with the database.
        # 
        if options['delete_files_stored']:
            files_stored_dir = os.path.join(self.launch_path, 'files_stored')
            if os.path.exists(files_stored_dir):
                for file_stored in glob.glob('%s/*' % files_stored_dir):
                    os.remove(file_stored)

        if options['delete_logs']:
            logs_dir = os.path.join(self.launch_path, 'logs')
            if os.path.exists(logs_dir):
                for log_file in glob.glob('%s/*txt*' % logs_dir):
                    os.remove(log_file)


    def _has_started(self):
        running  = []
        failures = []
        try:
            matches = True

            for port in self.ports['soap']:
                soap_url = 'http://%s:%s%s/weblab/soap/?WSDL' % (self.host, port, self.base_location)
                if self.verbose:
                    print soap_url
                current_content = urllib2.urlopen(soap_url).read()
                matches &= current_content.find("definitions targetNamespace") > 0
                running.append('soap')

            for port in self.ports['xmlrpc']:
                xmlrpc_url = 'http://%s:%s%s/weblab/xmlrpc/' % (self.host, port, self.base_location)
                if self.verbose:
                    print xmlrpc_url
                current_content = urllib2.urlopen(xmlrpc_url).read()
                matches &= current_content.find("XML-RPC service") > 0
                running.append('xmlrpc')

            for port in self.ports['json']:
                json_url = 'http://%s:%s%s/weblab/json/' % (self.host, port, self.base_location)
                if self.verbose:
                    print json_url
                current_content = urllib2.urlopen(json_url).read()
                matches &= current_content.find("JSON service") > 0
                running.append('json')

            for port in self.ports['soap_login']:
                soap_login_url = 'http://%s:%s%s/weblab/login/soap/?WSDL' % (self.host, port, self.base_location)
                if self.verbose:
                    print soap_login_url
                current_content = urllib2.urlopen(soap_login_url).read()
                matches &= current_content.find("definitions targetNamespace") > 0
                running.append('soap_login')

            for port in self.ports['xmlrpc_login']:
                xmlrpc_login_url = 'http://%s:%s%s/weblab/login/xmlrpc/' % (self.host, port, self.base_location)
                if self.verbose:
                    print xmlrpc_login_url
                current_content = urllib2.urlopen(xmlrpc_login_url).read()
                matches &= current_content.find("XML-RPC service") > 0
                running.append('xmlrpc_login')

            for port in self.ports['json_login']:
                json_login_url = 'http://%s:%s%s/weblab/login/json/' % (self.host, port, self.base_location)
                if self.verbose:
                    print json_login_url
                current_content = urllib2.urlopen(json_login_url).read()
                matches &= current_content.find("JSON service") > 0
                running.append('json_login')

            return matches, 'not matches'
        except Exception:
            sio = StringIO.StringIO()
            traceback.print_exc(file=sio)
            if self.verbose:
                print sio.getvalue()
            return False, sio.getvalue()

    def _has_finished(self):
        return self.popen.poll() is not None

    def start(self):
        self.popen = subprocess.Popen(["python", "-OO", self.launch_file],
                                      cwd=self.launch_path,
                                      stdin=subprocess.PIPE,
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE)

        time.sleep(2)
        if self.popen.poll() is not None:
            print self.popen.stdout.read()
            print self.popen.stderr.read()
            raise Exception("Server couldn't start!")

    def step_wait(self):
        time.sleep(8)

    def wait_for_process_started(self):
        max_iterations = 10
        while max_iterations > 0:
            started, failure = self._has_started()
            if started:
                break
            max_iterations -= 1
            time.sleep(4)
        if max_iterations == 0:
            if self.popen.poll() is not None:
                print self.popen.stdout.read()
                print self.popen.stderr.read()
            raise Exception("Server couldn't start! Failure: %s" % failure)
        self._wait_file_notifier(os.path.join(self.launch_path, "_file_notifier"))

    def step_started_wait(self):
        time.sleep(4)

    def _wait_file_notifier(self, filepath):
        while True:
            try:
                open(filepath)
            except IOError:
                time.sleep(0.1)
            else:
                break
        #time.sleep(1)

    def shutdown(self):
        if not self._has_finished():
            (self.out, self.err) = self.popen.communicate(input="\n")
            maxtime = 5 # seconds
            time_expired = False
            initialtime = time.time()
            while not self._has_finished() and not time_expired:
                time.sleep(0.1)
                time_expired = time.time() > initialtime + maxtime
            if time_expired:
                killer.term(self.popen)
                initialtime = time.time()
                while not self._has_finished() and not time_expired:
                    time.sleep(0.1)
                    time_expired = time.time() > initialtime + maxtime
                if time_expired:
                    killer.kill(self.popen)
        else:
            try:
                self.out = self.popen.stdout.read()
                self.err = self.popen.stderr.read()
            except Exception as e:
                self.out = "Couldn't read process output: %s" % e
                self.err = "Couldn't read process output: %s" % e

        self.result = self.popen.wait()
        return self.result
