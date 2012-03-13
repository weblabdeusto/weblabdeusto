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
# Author: Luis Rodríguez <luis.rodriguez@opendeusto.es>
#         Pablo Orduña <pablo@ordunya.com>
# 

import weblab.experiment.concurrent_experiment as ConcurrentExperiment

import httplib
import urllib2
import urllib
import threading
import time
import xml.dom.minidom as xml

import json

from voodoo.log import logged
from voodoo.override import Override
from voodoo.lock import locked


from voodoo.typechecker import typecheck, ANY


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
CFG_HEARTBEAT_PERIOD = "vt_heartbeat_period"
CFG_DEBUG_PRINTS = "vt_debug_prints"

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
DEFAULT_HEARTBEAT_PERIOD = 30
DEFAULT_DEBUG_PRINTS = False

HEARTBEAT_REQUEST = """<protocol version="1.3"><request sessionkey="%s"/></protocol>"""
HEARTBEAT_MAX_SLEEP = 5


# Actually defined through the configuration.
DEBUG = None


class Heartbeater(threading.Thread):
    """
    The Heartbeater is a different thread, which will periodically send a heartbeat
    request if no other requests have been sent recently.
    """
    
    @typecheck(ANY, basestring, int, basestring)
    def __init__(self, experiment, heartbeat_period):
        """
        Creates the Heartbeater object. The Heartbeater is a thread which will periodically
        send requests as heartbeats (because actual heartbeat or even login requests do not work).
        
        There should be a single Heartbeater, which will send the periodical requests to every
        user that needs so. New sessions to handle should be registered through register_session and removed through
        remove_session.
        
        The heartbeat may be inhibited through periodical tick() calls.
    
        For the Heartbeater to start working, it needs to be started through start(). To stop it,
        stop() must be called. It is noteworthy that stop is not immediate. 
        
        @param experiment Reference to the VisirTestExperiment. Will make use of the user map within it.
        @param heartbeat_period Number of seconds between heartbeats.
        
        @see start
        @see stop
        @see tick
        @see register_session
        @see remove_session
        """
        threading.Thread.__init__(self)
        self.is_stopped = False
        self.experiment = experiment
        self.heartbeat_period = heartbeat_period
        self.sessions = {}
        
        
    def register_session(self, lab_session_id, sessionkey):
        """
        Register the specified session. The session will start receiving
        heartbeats.
        @param lab_session_id Laboratory session id of the user to register.
        @param visir session key to send requests with. It is actually linked
        to the laboratory session.
        """
        self.sessions[lab_session_id] = {}
        self.sessions[lab_session_id]['sessionkey'] = sessionkey
        
    def remove_session(self, lab_session_id):
        """
        Remove the specified session. The session will no longer receive
        heartbeats. If the session does not exist, this will have no effect.
        @param lab_session_id Laboratory session of the user to remove.
        """
        if lab_session_id in self.sessions:
            del self.sessions[lab_session_id]
         
        
    def stop(self):
        """
        Stops the thread. The thread is not stopped immediately. Instead, a flag is
        internally set and the actual thread will finish when possible.
        Once called, stopped() will return true (without waiting for the thread to
        actually finish).
        
        @see stopped
        """
        self.is_stopped = True
        
    def stopped(self):
        """
        Returns true if the thread has been explicitly stopped. False otherwise.
        Note that before the thread has been started, stopped will still be false.
        That is, it will start returning true just as soon as stop is called.
        
        @see stop
        @see is_alive
        """
        return self.is_stopped
    
        
    def tick(self, lab_session_id):
        """
        tick()
        Ticks to update the time for a given session. If the session has not been registered
        the tick operation does nothing.
        
        @param lab_session_id Session id of the user counter to tick
        Should be called, both internally or externally, whenever a heartbeat or any
        other packet is sent to reset OR INITIALIZE the heartbeat timer.
        """
        
        # If the session id is not registered within the sessions map, we will simply
        # return without doing anything. This can happen for the initial login request.
        if lab_session_id not in self.sessions:
            return
        
        sessiondata = self.sessions[lab_session_id]
        sessiondata['last_heartbeat_sent'] = time.time()
        if DEBUG: print "[DBG] HB TICK"
    
    
    def run(self):
        """
        run()
        
        Thread process. Thread starts running here when start() is called.
        @see start
        """
        
        if DEBUG: print "[DBG] HB INIT"
        
        while(True):
            
            # Sleep at most HEARTBEAT_MAX_SLEEP. We will most likely overwrite this
            # with a lower value, depending on the pending requests.
            time_to_sleep = HEARTBEAT_MAX_SLEEP 
            
            # Loop through every user that is using the experiment concurrently, and consider 
            # whether we should update it or not.
            for sid, sessiondata in self.sessions.items():
                
                # Evaluate the time left for the next potential heartbeat.
                if 'last_heartbeat_sent' not in sessiondata:
                    # If we actually don't have a last_heartbeat_sent yet,
                    # initialize it.
                    sessiondata['last_heartbeat_sent'] = time.time()
                last_sent = sessiondata['last_heartbeat_sent']
                session_key = sessiondata['sessionkey']
                time_left = (last_sent + self.heartbeat_period) - time.time()
                
                # If time_left is zero or negative, a heartbeat IS due.
                if(time_left <= 0):
                    if DEBUG: print "[DBG] HB FORWARDING"             
                    ret = self.experiment.forward_request(sid, HEARTBEAT_REQUEST % (session_key))
                    if DEBUG_MESSAGES: print "[DBG] Heartbeat response: ", ret
                    
                else:
                    # Otherwise, we will just sleep. 
                    if DEBUG: print "[DBG] HB SLEEPING FOR %d" % (time_left)
                    
                    # We wish to sleep the maximum only if there are no pending
                    # requests (and if it doesn't go over the MAX).
                    time_to_sleep = min(time_left, time_to_sleep)
            
                # We will actually not sleep the whole time_to_sleep at once, so that
                # we can check whether the thread has finished more often.
                # TODO: Consider doing this through semaphores so that we do not need 
                # this work-around.
                step_time = 0.1
                steps = time_to_sleep / step_time
                while not self.stopped() and steps > 0:
                    time.sleep(step_time)
                    steps -= 1
                if DEBUG: print "[DBG] Not sleeping anymore"
                
            if self.stopped():
                return

DEBUG_MESSAGES = DEBUG and False


class VisirTestExperiment(ConcurrentExperiment.ConcurrentExperiment):
    
    def __init__(self, coord_address, locator, cfg_manager, *args, **kwargs):
        super(VisirTestExperiment, self).__init__(*args, **kwargs)
        self._cfg_manager = cfg_manager
        self.read_config()
        self._requesting_lock = threading.Lock()
        
        # There will be a single heartbeater and a single thread, which will update
        # every concurrent user using this experiment.
        self.heartbeater = Heartbeater(self, self.heartbeat_period)
        
        # We start the heartbeater thread straightaway. The thread will actually do nothing
        # until there are sessions logged in which are awaiting heartbeats.
        self.heartbeater.start()
        
        self.users_map = {} # To store the list of users and their data
        
    @Override(ConcurrentExperiment.ConcurrentExperiment)
    def do_get_api(self):
        return "2_concurrent"
        
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
        self.heartbeat_period = self._cfg_manager.get_value(CFG_HEARTBEAT_PERIOD, DEFAULT_HEARTBEAT_PERIOD)
        
        global DEBUG
        DEBUG = self._cfg_manager.get_value(CFG_DEBUG_PRINTS, DEFAULT_DEBUG_PRINTS)

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
            

    @Override(ConcurrentExperiment.ConcurrentExperiment)
    @logged()
    def do_start_experiment(self, lab_session_id, *args, **kwargs):
        """
        Callback run when the experiment is started
        """
        
        # New user entered the experiment
        self.users_map[lab_session_id] = {}
        
        if DEBUG: print "[DBG] Current number of users: ", len(self.users_map)
        if DEBUG: print "[DBG] Lab Session Id: ", lab_session_id
        if DEBUG: print "[DBG] Measure server address: ", self.measure_server_addr
        if DEBUG: print "[DBG] Measure server target: ", self.measure_server_target

        return "Ok"

    @Override(ConcurrentExperiment.ConcurrentExperiment)
    def do_send_command_to_device(self, lab_session_id, command):
        """
        Callback run when the client sends a command to the experiment
        @param command Command sent by the client, as a string.
        """
        
        if DEBUG: print "[DBG] Lab Session Id: ", lab_session_id
        
        # Check whether it's a GIVEMECOOKIE command, which will carry out
        # a login to obtain the cookie the client should use
        if command == 'GIVE_ME_SETUP_DATA':
            if not self.use_visir_php:
                return self.build_setup_data("", self.client_url)

            if(DEBUG): print "[VisirTestExperiment] Performing login with %s / %s"  % (self.login_email, self.login_password)
            
            cookie = self.perform_visir_web_login(self.loginurl, self.login_email, self.login_password)
            
            return self.build_setup_data(cookie, self.client_url)
        
        # Otherwise, it's a VISIR XML command, and should just be forwarded
        # to the VISIR measurement server
        data = self.forward_request(lab_session_id, command) 
        
        # Find out the request type
        request_type = self.parse_request_type(command)
        
        if DEBUG: print "[DBG] REQUEST TYPE: " + request_type
        
        
        user = self.users_map[lab_session_id]
        
        # If it was a login request, we will extract the session key from the response.
        # Once the session is in a logged in state, it will need to start receiving
        # heartbeats.
        if request_type == "login":
            # Store the session for the user
            user['sessionkey'] = self.extract_sessionkey(data)
            if DEBUG: print "[DBG] Extracted sessionkey: " + user['sessionkey']
            
            # Register the new logged in user with the heartbeater, so that its session 
            # starts receiving updates.
            self.heartbeater.register_session(lab_session_id, user['sessionkey'])
            if DEBUG: print "[DBG] Registered with the heartbeater the lab session ", lab_session_id 
            
        return data


    def extract_sessionkey(self, command):
        """
        Extracts the sessionkey from the response to a <login> request.
        @param command The request, in a string containing the raw XML of the response.
        """
        dom = xml.parseString(command)
        protocol_node = dom.firstChild
        
        # Find the next non-text node.
        for n in protocol_node.childNodes:
            if n.nodeName != "#text":
                login_node = n
                
        sessionkey = login_node.getAttribute("sessionkey")
        
        return sessionkey
    
    
    def parse_request_type(self, command):
        """
        Will obtain the request type. That is, the name of the node beneath the root <protocol> node.
        @param command (String) The raw XML request or response.
        """
        dom = xml.parseString(command)
        protocol_node = dom.firstChild
        
        # Find the next non-text node.
        for n in protocol_node.childNodes:
            if n.nodeName != "#text":
                return n.nodeName
    
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
    
 
    @locked('_requesting_lock')
    def forward_request(self, lab_session_id, request):
        """
        Forwards a request to the VISIR Measurement Server through an
        HTTP POST.
        @param request String containing the request to be forwarded
        """
        if DEBUG_MESSAGES:
            print "[VisirTestExperiment] Forwarding request: ", request

            
        conn = httplib.HTTPConnection(self.measure_server_addr)
        conn.request("POST", self.measure_server_target, request)
        response = conn.getresponse()
        data = response.read()
        response.close()
        conn.close()
        
                    
        # We just sent a request. Tick the heartbeater.
        self.heartbeater.tick(lab_session_id)
        
        if DEBUG_MESSAGES:
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
            if DEBUG: print "Cookie found: ", c
            o.open("%s/electronics/experiment.php?cookie=%s" % (self.baseurl, c.value))
            #experiments_content = experiments_page.read()
            #"<a href=/electronics/experiment.php?[a-zA-Z0-9;&=]+\">(.*)"
            
            # Note: Normally we would want to start the heartbeater here, but because the 
            # standard <heartbeat> request does not work, we need to send standard requests
            # instead. These require a sessionkey, and we do not have one available until 
            # the user first sends a request.
            
            return c.value
        
        # No cookies retrieved, login must have failed.
        return None
    

    @Override(ConcurrentExperiment.ConcurrentExperiment)
    @logged()
    def do_send_file_to_device(self, lab_session_id, content, file_info):
        """ 
        Callback for when the client sends a file to the experiment
        server. Currently unused for this experiment, should never get 
        called.
        """
        if DEBUG: print "[DBG] Lab Session Id: ", lab_session_id
        if(DEBUG):
            print "[VisirTestExperiment] do_send_file_to_device called"
        return "Ok"
 

    @Override(ConcurrentExperiment.ConcurrentExperiment)
    @logged()
    def do_dispose(self, lab_session_id):
        """
        Callback to perform cleaning after the experiment ends.
        """
        
        if DEBUG: print "[DBG] Lab Session Id: ", lab_session_id        
        if(DEBUG):
            print "[VisirTestExperiment] do_dispose called"
            
        
        # TODO: For now, we will never stop the heartbeater thread. Eventually,
        # we maight wanna consider stoping it when there are 0 users, though in that
        # case it would probably have to be re-created before being started again.
        #user['heartbeater'].stop()
            
        #if user['heartbeater'].is_alive():
        #    raise Exception("[ERROR/Visir] The heartbeater thread could not be stopped in time")
        
        # User leaving the experiment. Remove it from the heartbeater, and remove it
        # from the internal users map.
        self.heartbeater.remove_session(lab_session_id)
        
        if DEBUG: print "[DBG] Finished successfully: ", lab_session_id 
        
        return "Ok"

