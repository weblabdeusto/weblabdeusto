#!/usr/bin/env python
#-*-*- encoding: utf-8 -*-*-
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
import weblab.comm.web_server as WebFacadeServer

class ConfigurationMethod(WebFacadeServer.Method):
    path = '/experiments.js'

    def avoid_weblab_cookies(self):
        return True

    def run(self):
        clients = self.server.list_clients()
        formatted = {
            # 'client_id' : [
            #          {
            #              'experiment.name' : 'foo',
            #              'experiment.category' : 'bar',
            #              'other.property' : 'foobar',
            #          },
            #          {
            #              'experiment.name' : 'other',
            #              'experiment.category' : 'bar',
            #              'other.property' : 'foobar',
            #          },
            # ]
        }
        for (exp_name, exp_category), client in clients.iteritems():
            client_config = {
                'experiment.name'     : exp_name,
                'experiment.category' : exp_category,
            }
            for key in client.configuration:
                client_config[key] = client.configuration[key]

            if client.client_id in formatted:
                formatted[client.client_id].append(client_config)
            else:
                formatted[client.client_id] = [ client_config ]
            
        return json.dumps(formatted, indent = 4)

