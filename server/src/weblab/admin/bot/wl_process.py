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

import os
import subprocess
import time
import urllib2
import voodoo.killer as killer

class WebLabProcess(object):

    def __init__(self, launch_file, host, base_location = ''):
        super(WebLabProcess, self).__init__()

        if os.sep != '/' and '/' in launch_file and os.sep in launch_file:
            raise Exception("Both %s and / found in launch_file (%s), only one expected" % (os.sep, launch_file))

        self.host        = host
        self.base_location = base_location

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

    def _has_started(self):
        try:
            matches = True

            for port in self.ports['soap']:
                current_content = urllib2.urlopen('http://%s:%s%s/weblab/soap/?WSDL' % (self.host, port, self.base_location)).read()
                matches &= current_content.find("definitions targetNamespace") > 0

            for port in self.ports['xmlrpc']:
                current_content = urllib2.urlopen('http://%s:%s%s/weblab/xmlrpc/' % (self.host, port, self.base_location)).read()
                matches &= current_content.find("XML-RPC service") > 0

            for port in self.ports['json']:
                current_content = urllib2.urlopen('http://%s:%s%s/weblab/json/' % (self.host, port, self.base_location)).read()
                matches &= current_content.find("JSON service") > 0

            for port in self.ports['soap_login']:
                current_content = urllib2.urlopen('http://%s:%s%s/weblab/login/soap/?WSDL' % (self.host, port, self.base_location)).read()
                matches &= current_content.find("definitions targetNamespace") > 0

            for port in self.ports['xmlrpc_login']:
                current_content = urllib2.urlopen('http://%s:%s%s/weblab/login/xmlrpc/' % (self.host, port, self.base_location)).read()
                matches &= current_content.find("XML-RPC service") > 0

            for port in self.ports['json_login']:
                current_content = urllib2.urlopen('http://%s:%s%s/weblab/login/json/' % (self.host, port, self.base_location)).read()
                matches &= current_content.find("JSON service") > 0

            return matches
        except Exception:
            return False

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
        time.sleep(8)

        max_iterations = 10
        while not self._has_started() and max_iterations > 0:
            max_iterations -= 1
            time.sleep(4)
        if max_iterations == 0:
            if self.popen.poll() is not None:
                print self.popen.stdout.read()
                print self.popen.stderr.read()
            raise Exception("Server couldn't start!")
        self._wait_file_notifier(os.path.join(self.launch_path, "_file_notifier"))
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
