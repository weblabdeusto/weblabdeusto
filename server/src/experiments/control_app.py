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
# Author: Pablo Orduña <pablo@ordunya.com>
#

import json
import base64
import uuid
import urllib
import urllib2
import threading
import time

import weblab.experiment.experiment as Experiment
import weblab.experiment.level as ExperimentApiLevel

from voodoo.override import Override

ROUTER_URL     = 'http://147.175.79.44/rcgi.bin/EditUserForm'
ROUTER_WEB     = 'http://147.175.79.44/usr/controlapp/ControlApp.html?user=%(login)s&pass=%(password)s&remaining=TIME_REMAINING&back=%(back)s'
POLLING_URL    = 'http://147.175.79.44/usr/controlapp/config/pollingInfo.shtm'
POLLING_PERIOD = 15
ROUTER_REALM   = 'eWON IAM 2'

class ControlAppExperiment(Experiment.Experiment):

    def __init__(self, coord_address, locator, cfg_manager, *args, **kwargs):
        super(ControlAppExperiment, self).__init__(*args, **kwargs)
        self.cfg_manager  = cfg_manager
        self.debug        = self.cfg_manager.get_value('debug', False)
        self.admin_user   = self.cfg_manager.get_value('admin_user')
        self.admin_pass   = self.cfg_manager.get_value('admin_pass')
        self.router_url   = self.cfg_manager.get_value('router_url', ROUTER_URL)
        self.router_web   = self.cfg_manager.get_value('router_web', ROUTER_WEB)
        self.router_realm = self.cfg_manager.get_value('router_realm', ROUTER_REALM)
        self.router_poll  = self.cfg_manager.get_value('router_polling_url', POLLING_URL)
        self.poll_period  = self.cfg_manager.get_value('router_polling_period', POLLING_PERIOD)
        if self.poll_period <= 0:
            raise Exception("Router polling period must be over 0")
        self.timer        = None
        self._username    = 'sample'
        self.start_time   = 0

    @Override(Experiment.Experiment)
    def do_get_api(self):
        return ExperimentApiLevel.level_2

    def _reset_password(self):
        auth = urllib2.HTTPBasicAuthHandler()
        auth.add_password(
                    realm  = self.router_realm,
                    uri    = self.router_url,
                    user   = self.admin_user,
                    passwd = self.admin_pass,
                )
        opener = urllib2.build_opener(auth)

        random_uuid = uuid.uuid4()
        password = base64.encodestring(random_uuid.bytes)[:8]

        content = dict(
            edLogin=self._username,
            edPassword=password,
            edConfirmPassword=password,
            cbPageList=0,
            cbDirList=0,
            cbCBMode=0,
            B1='Add/Update',
            AST_EditUserId=4
        )

        opener.open('%s?%s' % (self.router_url, urllib.urlencode(content))).read()
        return password


    @Override(Experiment.Experiment)
    def do_start_experiment(self, serialized_client_initial_data, serialized_server_initial_data):

        raw_back_url = json.loads(serialized_client_initial_data).get('back','')
        back_url = urllib2.quote(raw_back_url,'')

        self.start_time = time.time()
        server_data = json.loads(serialized_server_initial_data)
        time_slot = float(server_data['priority.queue.slot.length'])
        self._username = server_data['request.username']
        self.timer = threading.Timer(time_slot, function = self._reset_password)
        self.timer.start()

        password = self._reset_password()
        url = {'url' : self.router_web % dict(login=self._username, password=password, back=back_url) }
        return json.dumps({ "initial_configuration" : json.dumps(url), 'batch' : False })

    @Override(Experiment.Experiment)
    def do_should_finish(self):

        # During the first 30 seconds, poll often but do not check the final server,
        # since it might take few seconds to load the final system.

        if (time.time() - 30) < self.start_time:
            if self.debug:
                print "Still initializing. Ask again in 10 seconds"
            return 10

        content    = urllib2.urlopen(self.router_poll).read()
        user_alive = json.loads(content).get('user', 0)
        if self.debug:
            print "User alive? ", user_alive != 0

        if user_alive == 0:
            return -1
        else:
            return self.poll_period # Ask again in this amount of time

    @Override(Experiment.Experiment)
    def do_dispose(self):
        if self.timer is not None:
           self.timer.cancel()
        self._reset_password()
        return 'ok'

