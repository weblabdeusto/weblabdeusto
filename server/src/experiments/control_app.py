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
import datetime
import threading

import weblab.experiment.experiment as Experiment
import weblab.core.coordinator.coordinator as Coordinator

from voodoo.override import Override

ROUTER_URL = 'http://147.175.79.44/rcgi.bin/EditUserForm'
ROUTER_WEB = 'http://147.175.79.44/usr/controlapp/ControlApp.html?user=%(login)s&pass=%(password)s&validto=%(tstamp)s'
ROUTER_REALM = 'eWON IAM 2'

class ControlAppExperiment(Experiment.Experiment):

    def __init__(self, coord_address, locator, cfg_manager, *args, **kwargs):
        super(ControlAppExperiment, self).__init__(*args, **kwargs)
        self.cfg_manager  = cfg_manager
        self.admin_user   = self.cfg_manager.get_value('admin_user')
        self.admin_pass   = self.cfg_manager.get_value('admin_pass')
        self.user_login   = self.cfg_manager.get_value('user_login','sample')
        self.router_url   = self.cfg_manager.get_value('router_url', ROUTER_URL)
        self.router_web   = self.cfg_manager.get_value('router_web', ROUTER_WEB)
        self.router_realm = self.cfg_manager.get_value('router_realm', ROUTER_REALM)
        self.timer        = None

    @Override(Experiment.Experiment)
    def do_get_api(self):
        return "2"

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
            edLogin=self.user_login,
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
        server_data = json.loads(serialized_server_initial_data)
        time_slot = float(server_data['priority.queue.slot.length'])

        now = datetime.datetime.utcnow() + datetime.timedelta(seconds=time_slot)
        str_time = now.strftime("%Y%m%d%H%M%S")

        self.timer = threading.Timer(time_slot, function = self._reset_password)
        self.timer.start()

        password = self._reset_password()
        url = {'url' : self.router_web % dict(login=self.user_login, password=password, tstamp=str_time) }
        return json.dumps({ "initial_configuration" : json.dumps(url), 'batch' : False })

    @Override(Experiment.Experiment)
    def do_dispose(self):
        if self.timer is not None:
           self.timer.cancel()
        self._reset_password()
        return 'ok'

