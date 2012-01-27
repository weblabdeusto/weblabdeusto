#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2005-2009 University of Deusto
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#
# This software consists of contributions made by many individuals, 
# listed below:
#
# Author: Luis Rodríguez <luis.rodriguez@opendeusto.es>
#         Pablo Orduña <pablo@ordunya.com>
# 

import weblab.experiment.experiment as Experiment

import httplib
import urllib2
import urllib
import threading
import time

import json

from voodoo.override import Override
from voodoo.lock import locked

CFG_USE_VISIR_PHP = "vt_use_visir_php"

CFG_MEASURE_SERVER_ADDRESS = "vt_measure_server_addr"
CFG_MEASURE_SERVER_TARGET = "vt_measure_server_target"
CFG_LOGIN_URL = "vt_login_url"
CFG_BASE_URL = "vt_base_url"
CFG_LOGIN_EMAIL = "vt_login_email"
CFG_LOGIN_PASSWORD = "vt_login_password"
CFG_SAVEDATA = "vt_savedata"
CFG_TEACHER  = "vt_teacher"
CFG_CLIENT_URL = "vt_client_url"

DEFAULT_USE_VISIR_PHP = True
DEFAULT_MEASURE_SERVER_ADDRESS = "130.206.138.35:8080"
DEFAULT_MEASURE_SERVER_TARGET = "/measureserver"
DEFAULT_LOGIN_URL = """https://weblab-visir.deusto.es/electronics/student.php"""
DEFAULT_BASE_URL = """https://weblab-visir.deusto.es/"""
DEFAULT_LOGIN_EMAIL = "guest"
DEFAULT_LOGIN_PASSWORD = "guest"
DEFAULT_SAVEDATA = ""
DEFAULT_TEACHER  = True
DEFAULT_CLIENT_URL = "visir/loader.swf"

DEBUG = True

HEARTBEAT_REQUEST = """<protocol version="1.3"><heartbeat/></protocol>"""
HEARTBEAT_PERIOD  = 20 


class Heartbeater(threading.Thread):
    """
    The Heartbeater is a different thread, which will periodically send a heartbeat
    request if no other requests have been sent recently.
    """
    
    def __init__(self):
        self.last_sent = time.time()
        
    def tick(self):
        """
        tick()
        Should be called, both internally or externally, whenever a heartbeat or any
        other packet is sent to reset the heartbeat timer.
        """
        self.last_sent = time.time()
        print "[DBG] HB TICK"
    
    def run(self, experiment):
        
        # Initialize the timer. We assume the thread is started just after login.
        self.last_sent = time.time()
        
        print "[DBG] HB INIT"
        
        while(True):
            # Evaluate the time left for the next potential heartbeat.
            time_left = time.time() - self.last_sent + HEARTBEAT_PERIOD
            
            # If time_left is zero or negative, a heartbeat IS due.
            if(time_left <= 0):
                print "[DBG] HB FORWARDING"             
                experiment.forward_request(HEARTBEAT_REQUEST)
            
            # Otherwise, we will just sleep. 
            print "[DBG] HB SLEEPING FOR %d" % (time_left)
            time.sleep(time_left)
            


class VisirTestExperiment(Experiment.Experiment):
    
    def __init__(self, coord_address, locator, cfg_manager, *args, **kwargs):
        super(VisirTestExperiment, self).__init__(*args, **kwargs)
        self._cfg_manager = cfg_manager
        self.read_config()
        self.heartbeater = Heartbeater()
        
    @Override(Experiment.Experiment)
    def do_get_api(self):
        return "1"
        
    def read_config(self):
        """
        Reads the config parameters from the config file (such as the
        measurement server address)
        """

        # Common configuration values
        self.savedata   = self._cfg_manager.get_value(CFG_SAVEDATA, DEFAULT_SAVEDATA)
        self.teacher    = self._cfg_manager.get_value(CFG_TEACHER, DEFAULT_TEACHER)
        self.client_url = self._cfg_manager.get_value(CFG_CLIENT_URL, DEFAULT_CLIENT_URL)
        self.measure_server_addr = self._cfg_manager.get_value(CFG_MEASURE_SERVER_ADDRESS, DEFAULT_MEASURE_SERVER_ADDRESS)
        self.measure_server_target = self._cfg_manager.get_value(CFG_MEASURE_SERVER_TARGET, DEFAULT_MEASURE_SERVER_TARGET)

        # 
        # There are two ways of deploying VISIR:
        # - with all the OpenLabs Web code
        # - directly without authentication against the measurement server
        # 
        # We support both, depending on this variable.
        # 
        self.use_visir_php = self._cfg_manager.get_value(CFG_USE_VISIR_PHP, DEFAULT_USE_VISIR_PHP)

        if self.use_visir_php:
            self.loginurl = self._cfg_manager.get_value(CFG_LOGIN_URL, DEFAULT_LOGIN_URL)
            self.baseurl = self._cfg_manager.get_value(CFG_BASE_URL, DEFAULT_BASE_URL)
            self.login_email = self._cfg_manager.get_value(CFG_LOGIN_EMAIL, DEFAULT_LOGIN_EMAIL)
            self.login_password = self._cfg_manager.get_value(CFG_LOGIN_PASSWORD, DEFAULT_LOGIN_PASSWORD)

    @Override(Experiment.Experiment)
    def do_start_experiment(self, *args, **kwargs):
        """
        Callback run when the experiment is started
        """
        print "Measure server address: ", self.measure_server_addr
        print "Measure server target: ", self.measure_server_target
        return "Ok"

    @Override(Experiment.Experiment)
    def do_send_command_to_device(self, command):
        """
        Callback run when the client sends a command to the experiment
        @param command Command sent by the client, as a string.
        """
        
        # Check whether it's a GIVEMECOOKIE command, which will carry out
        # a login to obtain the cookie the client should use
        if command == 'GIVE_ME_SETUP_DATA':
            if not self.use_visir_php:
                return self.build_setup_data("", self.client_url)

            if(DEBUG):
                print "[VisirTestExperiment] Performing login with %s / %s"  % (self.login_email, self.login_password)
            
            cookie = self.perform_visir_web_login(self.loginurl, self.login_email, self.login_password)
            
            return self.build_setup_data(cookie, self.client_url)
        
        # Otherwise, it's a VISIR XML command, and should just be forwarded
        # to the VISIR measurement server
        return self.forward_request(command) 

        
    def build_setup_data(self, cookie, url):
        """
        Helper function that will build and return a JSON-encoded reply to the 
        SETUP_DATA request.
        """
        data = {
                "cookie"   : cookie,
                "savedata" : urllib.quote(self.savedata, ''),
                "url"      : url,
                "teacher"  : self.teacher
                }
        resp = json.dumps(data)
        return str(resp)
    
        
    @locked()
    def forward_request(self, request):
        """
        Forwards a request to the VISIR Measurement Server through an
        HTTP POST.
        @param request String containing the request to be forwarded
        """
        if(DEBUG):
            print "[VisirTestExperiment] Forwarding request: ", request
            
        conn = httplib.HTTPConnection(self.measure_server_addr)
        conn.request("POST", self.measure_server_target, request)
        response = conn.getresponse()
        data = response.read()
        conn.close()
        
        # We just sent a request. Tick the heartbeater.
        self.heartbeater.tick()
        
        if(DEBUG):
            print "[VisirTestExperiment] Received response: ", data
            
        return data



    def perform_visir_web_login(self, url, email, password):
        """
        Performs a login through the specified visir web url.
        @param url Url to the file through which to login. May contain
        GET parameters if required.
        @param email Email or account name to use
        @param password Password to use
        @return The cookie that was returned upon a successful login, and
        None upon a failed one
        """
        
        # Create the POST data with the parameters
        postvals = {"email" : email,
                    "password" : password }
        postdata = urllib.urlencode(postvals)

        # We need to use a Cookie processor to be able to retrieve
        # the auth cookie that we seek
        cp = urllib2.HTTPCookieProcessor()
        o = urllib2.build_opener( cp )
        #urllib2.install_opener(o)
        
        # Do the request iself. The cookies retrieved (which should
        # actually be a single cookie) will be stored in the 
        # aforementioned cookie processor's CookieJar
        r = o.open(url, postdata)
        r.close()
        
        # If there is a cookie in the jar, assume it's the one we seek,
        # and return its value.
        for c in cp.cookiejar:
            print "Cookie found: ", c
            o.open("%s/electronics/experiment.php?cookie=%s" % (self.baseurl, c.value))
            #experiments_content = experiments_page.read()
            #"<a href=/electronics/experiment.php?[a-zA-Z0-9;&=]+\">(.*)"
            
            # We are now logged in. Start the heartbeater so that VISIR does not kick us
            # out due to inactivity.
            self.heartbeater.start()
            
            return c.value
        
        # No cookies retrieved, login must have failed.
        return None
    

    @Override(Experiment.Experiment)
    def do_send_file_to_device(self, content, file_info):
        """ 
        Callback for when the client sends a file to the experiment
        server. Currently unused for this experiment, should never get 
        called.
        """
        if(DEBUG):
            print "[VisirTestExperiment] do_send_file_to_device called"
        return "Ok"


    @Override(Experiment.Experiment)
    def do_dispose(self):
        """
        Callback to perform cleaning after the experiment ends.
        """
        if(DEBUG):
            print "[VisirTestExperiment] do_dispose called"
            
        # Stop the heartbeater
        self.heartbeater.stop()
        
        return "Ok"

