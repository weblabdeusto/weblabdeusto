#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 onwards University of Deusto
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#
# This software consists of contributions made by many individuals,
# listed below:
#
# Author: Pablo Orduña <pablo@ordunya.com>
#
from __future__ import print_function, unicode_literals

from __future__ import unicode_literals

import os
import sys
import shlex
import shutil
import socket
import signal
import time
import tempfile
import threading

import requests

from voodoo.process_starter import clean_created
import weblab.comm.proxy_server as proxy_server
from weblab.core.coordinator.clients.weblabdeusto import WebLabDeustoClient
from weblab.admin.script import weblab as weblab_admin
from test.util.ports import new as new_port



def connect(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('localhost', port))
    s.send('\n')
    s.close()

class ServerCreator(threading.Thread):
    def __init__(self, command = "", port_space = 10, startup_wait = 0.8):
        super(ServerCreator, self).__init__()
        proxy_server.QUIET = True
        self.address = ''
        self.startup_wait = startup_wait
        self.temporary_folder = tempfile.mkdtemp(prefix = 'remove_me_', suffix = '_testcase_script')
        self.weblab_dir = os.path.join(self.temporary_folder, 'weblab')
        self.argv = list(sys.argv)
        self.exc_info = None
        try:
            start_port = new_port()
            # Make a port space
            for _ in xrange(port_space):
                new_port()
            self.shutdown_port = new_port()
            self.public_port = new_port()
            self.address = 'http://localhost:%s/weblab/' % self.public_port
            sys.argv = shlex.split("weblab-admin create %s --ignore-locations --quiet --not-interactive --socket-wait=%s --start-port=%s %s --http-server-port=%s" % (self.weblab_dir, self.shutdown_port, start_port, command, self.public_port))

            weblab_admin()

            variables = {}
            execfile(os.path.join(self.temporary_folder, 'weblab', 'debugging.py'), variables, variables)
            self.ports = variables['PORTS']
            self.temporal_addresses = []
            for port in self.ports:
                self.temporal_addresses.append('http://localhost:%s/weblab/' % port)
        except:
            shutil.rmtree(self.temporary_folder)
            raise
        finally:
            sys.argv = self.argv

    def create_client(self):
        return WebLabDeustoClient(self.address)

    def __enter__(self):
        self.start()
        time.sleep(self.startup_wait)
        max_waiting_time = 8 # seconds
        original_time = time.time()

        while time.time() <= (original_time + max_waiting_time):
            time.sleep(0.2)
            finished = True

            try:
                for address in (self.temporal_addresses + [self.address]):
                    r = requests.get('%sjson/' % self.address, allow_redirects=False)
                    if r.status_code != 200:
                        finished = False
            except:
                finished = False

            if finished:
                break
        return self

    def run(self):
        try:
            if 'PYTHONPATH' in os.environ:
                os.environ['PYTHONPATH'] = os.pathsep.join((os.environ['PYTHONPATH'], os.path.abspath('.')))
            else:
                os.environ['PYTHONPATH'] = os.path.abspath('.')
            sys.argv = shlex.split("weblab-admin start %s" % self.weblab_dir)
            weblab_admin()
        except:
            self.exc_info = sys.exc_info()
            print(self.exc_info)

    def __exit__(self, *args, **kwargs):
        connect(self.shutdown_port)
        self.join(5) # seconds
        clean_created()
        sys.argv = self.argv
        shutil.rmtree(self.temporary_folder)
        if self.isAlive():
            raise AssertionError("Process should be dead by now")
        if self.exc_info is not None:
            raise AssertionError("Process failed: %s" % self.exc_info)
        proxy_server.QUIET = False

