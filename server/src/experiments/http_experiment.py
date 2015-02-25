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

import sys
import traceback
import base64
import urllib2
import json

import weblab.configuration_doc as configuration_doc
from weblab.experiment.experiment import Experiment
import weblab.experiment.level as ExperimentApiLevel
import weblab.core.coordinator.coordinator as Coordinator

class HttpExperiment(Experiment):

    def __init__(self, coord_address, locator, cfg_manager, *args, **kwargs):
        super(Experiment, self).__init__(*args, **kwargs)

        self.base_url = cfg_manager.get_doc_value(configuration_doc.HTTP_EXPERIMENT_URL)
        if self.base_url.endswith('/'):
            print "Warning: HTTP experiment address ends in /" 
        self.username = cfg_manager.get_doc_value(configuration_doc.HTTP_EXPERIMENT_USERNAME)
        self.password = cfg_manager.get_doc_value(configuration_doc.HTTP_EXPERIMENT_PASSWORD)
        self.batch    = cfg_manager.get_doc_value(configuration_doc.HTTP_EXPERIMENT_BATCH)

        if self.username and self.password:
            self.encoded = base64.encodestring('%s:%s' % (self.username, self.password)).replace('\n', '')
        
        self.session_id = ''

    def _request(self, path, data = None):
        request = urllib2.Request("%s/weblab/sessions/%s" % (self.base_url, path))

        if self.username and self.password:
            request.add_header("Authorization", "Basic %s" % self.encoded)
            if data is not None:
                request.add_header('Content-Type', 'application/json')

        if data is None:
            return urllib2.urlopen(request).read()
        else:
            return urllib2.urlopen(request, json.dumps(data)).read()

    def do_start_experiment(self, serialized_client_initial_data, serialized_server_initial_data):
        """
        Invoked by WebLab on the start experiment event.
        :param serialized_client_initial_data: Initial client configuration. As a JSON-parseable string.
        :type serialized_client_initial_data: str
        :param serialized_server_initial_data: Initial data provided by the server. As a JSON-parseable string.
        :type serialized_server_initial_data: str
        :return: JSON parseable string containing the initial_configuration dictionary, which includes an "url" and a "back" url.
        :rtype: str
        """
        try:
            back_url = json.loads(serialized_client_initial_data).get('back','')

            response_str = self._request('', {
                'client_initial_data' : serialized_client_initial_data,
                'server_initial_data' : serialized_server_initial_data,
                'back' : back_url,
            })
            try:
                response = json.loads(response_str)
            except:
                print 
                print "Got invalid JSON response from the HTTP server:"
                print "*" * 20
                print response_str
                print "*" * 20
                sys.stdout.flush()
                raise
            url = response.get('url','http://server.sent.invalid.address')

            config = {
                'url'  : url,
            }
            self.session_id = response.get('session_id','invalid_session_id')

            return json.dumps({ "initial_configuration" : json.dumps(config), "batch" : self.batch })
        except:
            traceback.print_exc()
            raise

    def do_get_api(self):
        return ExperimentApiLevel.level_2

    def do_should_finish(self):
        """
        Should the experiment finish? If the experiment server should be able to
        say "I've finished", it will be asked every few time; if the experiment
        is completely interactive (so it's up to the user and the permissions of
        the user to say when the session should finish), it will never be asked.

        Therefore, this method will return a numeric result, being:
          - result > 0: it hasn't finished but ask within result seconds.
          - result == 0: completely interactive, don't ask again
          - result < 0: it has finished.
        """
        try:
            response_str = self._request('%s/status' % self.session_id)
            response = json.loads(response_str)
            return response['should_finish']
        except:
            traceback.print_exc()
            raise

    def do_dispose(self):
        try:
            response_str = self._request('%s' % self.session_id, {
                'action' : 'delete',
            })

            return json.dumps({ Coordinator.FINISH_FINISHED_MESSAGE : True, Coordinator.FINISH_DATA_MESSAGE : ""})
        except:
            traceback.print_exc()
            raise


# TODO: support the concurrent version



