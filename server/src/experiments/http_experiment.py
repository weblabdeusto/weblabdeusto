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
import time
import json
import base64
import urllib
import urllib2
import traceback
import threading
import ssl

import weblab.configuration_doc as configuration_doc
from weblab.experiment.experiment import Experiment
from weblab.experiment.concurrent_experiment import ConcurrentExperiment
import weblab.experiment.level as ExperimentApiLevel
import weblab.core.coordinator.coordinator as Coordinator

class GetInfoThread(threading.Thread):
    def __init__(self, experiment, coord_address, verbose):
        threading.Thread.__init__(self)
        self.setName("HttpExperiment::GetInfoThread::%s" % coord_address)
        self.setDaemon(True)
        self.experiment = experiment
        self.verbose = verbose

    def run(self):
        while True:
            try:
                if self.experiment.get_api_and_test():
                    break
            except:
                if self.verbose:
                    print("Error in %s" % self.name)
                    traceback.print_exc()
            time.sleep(10)

class HttpExperiment(Experiment):

    def __init__(self, coord_address, locator, config, *args, **kwargs):
        super(Experiment, self).__init__(*args, **kwargs)

        self.base_url = config.get_doc_value(configuration_doc.HTTP_EXPERIMENT_URL)
        if self.base_url.endswith('/'):
            print "Warning: HTTP experiment address ends in /" 
        self.username       = config.get_doc_value(configuration_doc.HTTP_EXPERIMENT_USERNAME)
        self.password       = config.get_doc_value(configuration_doc.HTTP_EXPERIMENT_PASSWORD)
        self.batch          = config.get_doc_value(configuration_doc.HTTP_EXPERIMENT_BATCH)
        self.api            = config.get_doc_value(configuration_doc.HTTP_EXPERIMENT_API)
        self.extension      = config.get_doc_value(configuration_doc.HTTP_EXPERIMENT_EXTENSION)
        self.request_format = config.get_doc_value(configuration_doc.HTTP_EXPERIMENT_REQUEST_FORMAT)
        self.verbose        = config.get_doc_value(configuration_doc.HTTP_EXPERIMENT_VERBOSE)

        if self.username and self.password:
            self.encoded = base64.encodestring('%s:%s' % (self.username, self.password)).replace('\n', '')
        
        self.session_id = ''
        self._get_info_thread = GetInfoThread(self, coord_address, self.verbose)

        self._tested = False
        if self.api != '0': # If API is '0', the /api and /test methods don't even exist
            self._get_info_thread.start()

    def _build_url(self, path):
        return "%s/weblab/sessions/%s" % (self.base_url, path)

    def _request(self, path, data = None):
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        request = urllib2.Request(self._build_url(path))

        if self.username and self.password:
            request.add_header("Authorization", "Basic %s" % self.encoded)

        if data is not None:
            if self.request_format == 'json':
                request.add_header('Content-Type', 'application/json')

        if data is None:
            return urllib2.urlopen(request, context=ctx).read()
        elif self.request_format == 'json':
            return urllib2.urlopen(request, json.dumps(data), context=ctx).read()
        elif self.request_format == 'form':
            return urllib2.urlopen(request, urllib.urlencode(data), context=ctx).read()
        else:
            raise Exception("Unsupported format: %r" % fmt)

    def _request_json_dict(self, url, what, data = None):
        try:
            response_str = self._request(url, data)
        except:
            if self.verbose:
                print("Error obtaining %s from %s" % (what, self._build_url(url)))
                traceback.print_exc()
            return False
       
        if response_str == 'ok' or response_str == '' or response_str == 'deleted':
            response_str = "{}"

        try:
            response = json.loads(response_str)
        except:
            if self.verbose:
                print("Error obtaining JSON from %s response:" % what)
                print(response_str)
            return False
        
        if not isinstance(response, dict):
            if self.verbose:
                print("Error obtaining JSON from %s response: it is not an object" % what)
                print(response_str)
            return False

        return response
   
    def get_api(self):
        if self.api:
            return self.api

        if self.extension:
            url = 'api%s' % self.extension
        else:
            url = 'api'
        
        response = self._request_json_dict(url, "API")
        if response == False:
            return False

        api_version = response.get('api_version')
        if not api_version:
            if self.verbose:
                print("Invalid api_version")
                print(api_version)
            return False
        
        self.api = api_version
        return self.api

    def test(self):
        if self._tested:
            # Previously tested
            return True

        if self.api is None:
            if self.verbose:
                print("API not yet defined; couldn't try the test method")
            return False
        
        if self.api == '0':
            # No test required
            self._tested = True
            return True
        
        if self.extension:
            url = 'test%s' % self.extension
        else:
            url = 'test'

        response = self._request_json_dict(url, "Test")
        if response == False:
            return False

        valid = response.get('valid', False)
        if valid:
            self._tested = True
            return True

        raise Exception("Error testing the server: %s" % response.get('error_messages', ["Error accesing server by unknown reason"]))

    def get_api_and_test(self):
        api = self.get_api()
        if api:
            if not self.test():
                return False
        return api
            

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
        api = self.get_api_and_test()
        if api is None:
            raise Exception("Couldn't obtain the API for this experiment, so it can't be started!")

        try:
            back_url = json.loads(serialized_client_initial_data).get('back','')
    
            if self.extension:
                url = 'new%s' % self.extension
            else:
                url = ''

            data = {
                'back' : back_url
            }
            
            if api == "0" or self.request_format == 'form':
                data['client_initial_data'] = serialized_client_initial_data
                data['server_initial_data'] = serialized_server_initial_data
            else:
                data['client_initial_data'] = json.loads(serialized_client_initial_data)
                data['server_initial_data'] = json.loads(serialized_server_initial_data)
            
            response_str = self._request(url, data)
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
        if self.extension:
            url = 'status%s?session_id=%s' % (self.extension, self.session_id)
        else:
            url = '%s/status' % self.session_id
        try:
            response_str = self._request(url)
            response = json.loads(response_str)
            return response['should_finish']
        except:
            traceback.print_exc()
            raise

    def do_dispose(self):
        if self.extension:
            url = 'action%s?session_id=%s' % (self.extension, self.session_id)
        else:
            url = '%s' % self.session_id

        try:
            response = self._request_json_dict(url, "dispose", {
                'action': 'delete',
            })

            wrapped_response = {
                Coordinator.FINISH_FINISHED_MESSAGE: True,
                Coordinator.FINISH_DATA_MESSAGE: ""
            }

            if response:
                finished = response.get(Coordinator.FINISH_FINISHED_MESSAGE)
                if finished is not None:
                    wrapped_response[Coordinator.FINISH_FINISHED_MESSAGE] = finished
                data = response.get(Coordinator.FINISH_DATA_MESSAGE)
                if data is not None:
                    wrapped_response[Coordinator.FINISH_FINISHED_MESSAGE] = data
                ask_again = response.get(Coordinator.FINISH_ASK_AGAIN_MESSAGE)
                if ask_again is not None:
                    wrapped_response[Coordinator.FINISH_ASK_AGAIN_MESSAGE] = ask_again

            return json.dumps(wrapped_response)
        except:
            traceback.print_exc()
            raise


class ConcurrentHttpExperiment(Experiment):

    def __init__(self, coord_address, locator, config, *args, **kwargs):
        super(Experiment, self).__init__(*args, **kwargs)

        self.base_url = config.get_doc_value(configuration_doc.HTTP_EXPERIMENT_URL)
        if self.base_url.endswith('/'):
            print "Warning: HTTP experiment address ends in /" 
        self.username       = config.get_doc_value(configuration_doc.HTTP_EXPERIMENT_USERNAME)
        self.password       = config.get_doc_value(configuration_doc.HTTP_EXPERIMENT_PASSWORD)
        self.batch          = config.get_doc_value(configuration_doc.HTTP_EXPERIMENT_BATCH)
        self.api            = config.get_doc_value(configuration_doc.HTTP_EXPERIMENT_API)
        self.extension      = config.get_doc_value(configuration_doc.HTTP_EXPERIMENT_EXTENSION)
        self.request_format = config.get_doc_value(configuration_doc.HTTP_EXPERIMENT_REQUEST_FORMAT)
        self.verbose        = config.get_doc_value(configuration_doc.HTTP_EXPERIMENT_VERBOSE)

        self.session_ids_lock = threading.Lock()
        self.session_ids = {}


        if self.username and self.password:
            self.encoded = base64.encodestring('%s:%s' % (self.username, self.password)).replace('\n', '')
        
        self._get_info_thread = GetInfoThread(self, coord_address, self.verbose)

        self._tested = False
        if self.api != '0': # If API is '0', the /api and /test methods don't even exist
            self._get_info_thread.start()

    def _build_url(self, path):
        return "%s/weblab/sessions/%s" % (self.base_url, path)

    def _request(self, path, data = None):
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        request = urllib2.Request(self._build_url(path))

        if self.username and self.password:
            request.add_header("Authorization", "Basic %s" % self.encoded)

        if data is not None:
            if self.request_format == 'json':
                request.add_header('Content-Type', 'application/json')

        if data is None:
            return urllib2.urlopen(request, context=ctx).read()
        elif self.request_format == 'json':
            return urllib2.urlopen(request, json.dumps(data), context=ctx).read()
        elif self.request_format == 'form':
            return urllib2.urlopen(request, urllib.urlencode(data), context=ctx).read()
        else:
            raise Exception("Unsupported format: %r" % fmt)

    def _request_json_dict(self, url, what, data = None):
        try:
            response_str = self._request(url, data)
        except:
            if self.verbose:
                print("Error obtaining %s from %s" % (what, self._build_url(url)))
                traceback.print_exc()
            return False
       
        if response_str == 'ok' or response_str == '' or response_str == 'deleted':
            response_str = "{}"

        try:
            response = json.loads(response_str)
        except:
            if self.verbose:
                print("Error obtaining JSON from %s response:" % what)
                print(response_str)
            return False
        
        if not isinstance(response, dict):
            if self.verbose:
                print("Error obtaining JSON from %s response: it is not an object" % what)
                print(response_str)
            return False

        return response
   
    def get_api(self):
        if self.api:
            return self.api

        if self.extension:
            url = 'api%s' % self.extension
        else:
            url = 'api'
        
        response = self._request_json_dict(url, "API")
        if response == False:
            return False

        api_version = response.get('api_version')
        if not api_version:
            if self.verbose:
                print("Invalid api_version")
                print(api_version)
            return False
        
        self.api = api_version
        return self.api

    def test(self):
        if self._tested:
            # Previously tested
            return True

        if self.api is None:
            if self.verbose:
                print("API not yet defined; couldn't try the test method")
            return False
        
        if self.api == '0':
            # No test required
            self._tested = True
            return True
        
        if self.extension:
            url = 'test%s' % self.extension
        else:
            url = 'test'

        response = self._request_json_dict(url, "Test")
        if response == False:
            return False

        valid = response.get('valid', False)
        if valid:
            self._tested = True
            return True

        raise Exception("Error testing the server: %s" % response.get('error_messages', ["Error accesing server by unknown reason"]))

    def get_api_and_test(self):
        api = self.get_api()
        if api:
            if not self.test():
                return False
        return api
            

    def do_start_experiment(self, lab_session_id, serialized_client_initial_data, serialized_server_initial_data):
        """
        Invoked by WebLab on the start experiment event.
        :param serialized_client_initial_data: Initial client configuration. As a JSON-parseable string.
        :type serialized_client_initial_data: str
        :param serialized_server_initial_data: Initial data provided by the server. As a JSON-parseable string.
        :type serialized_server_initial_data: str
        :return: JSON parseable string containing the initial_configuration dictionary, which includes an "url" and a "back" url.
        :rtype: str
        """
        api = self.get_api_and_test()
        if api is None:
            raise Exception("Couldn't obtain the API for this experiment, so it can't be started!")

        try:
            back_url = json.loads(serialized_client_initial_data).get('back','')
    
            if self.extension:
                url = 'new%s' % self.extension
            else:
                url = ''

            data = {
                'back' : back_url,
            }
            
            if api == "0" or self.request_format == 'form':
                data['client_initial_data'] = serialized_client_initial_data
                data['server_initial_data'] = serialized_server_initial_data
            else:
                data['client_initial_data'] = json.loads(serialized_client_initial_data)
                data['server_initial_data'] = json.loads(serialized_server_initial_data)
            
            response_str = self._request(url, data)
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
            with self.session_ids_lock:
                self.session_ids[lab_session_id] = response.get('session_id','invalid_session_id')

            return json.dumps({ "initial_configuration" : json.dumps(config), "batch" : self.batch })
        except:
            traceback.print_exc()
            raise

    def do_get_api(self):
        return ExperimentApiLevel.level_2_concurrent

    def do_should_finish(self, lab_session_id):
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
        with self.session_ids_lock:
            session_id = self.session_ids.get(lab_session_id, 'no-session-id')

        if self.extension:
            url = 'status%s?session_id=%s' % (self.extension, session_id)
        else:
            url = '%s/status' % session_id
        try:
            response_str = self._request(url)
            response = json.loads(response_str)
            return response['should_finish']
        except:
            traceback.print_exc()
            raise

    def do_dispose(self, lab_session_id):
        with self.session_ids_lock:
            session_id = self.session_ids.get(lab_session_id, 'no-session-id')

        if self.extension:
            url = 'action%s?session_id=%s' % (self.extension, session_id)
        else:
            url = '%s' % session_id

        try:
            response = self._request_json_dict(url, "dispose", {
                'action': 'delete',
            })

            wrapped_response = {
                Coordinator.FINISH_FINISHED_MESSAGE: True,
                Coordinator.FINISH_DATA_MESSAGE: ""
            }

            if response:
                finished = response.get(Coordinator.FINISH_FINISHED_MESSAGE)
                if finished is not None:
                    wrapped_response[Coordinator.FINISH_FINISHED_MESSAGE] = finished
                data = response.get(Coordinator.FINISH_DATA_MESSAGE)
                if data is not None:
                    wrapped_response[Coordinator.FINISH_FINISHED_MESSAGE] = data
                ask_again = response.get(Coordinator.FINISH_ASK_AGAIN_MESSAGE)
                if ask_again is not None:
                    wrapped_response[Coordinator.FINISH_ASK_AGAIN_MESSAGE] = ask_again

            return json.dumps(wrapped_response)
        except:
            traceback.print_exc()
            raise

