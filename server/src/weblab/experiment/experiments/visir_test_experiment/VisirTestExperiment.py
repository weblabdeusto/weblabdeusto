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
# 

import weblab.experiment.Experiment as Experiment

import xml.dom.minidom as minidom
import httplib
import urllib
import urllib2

from voodoo.override import Override



CFG_MEASURE_SERVER_ADDRESS = "vt_measure_server_addr"
CFG_MEASURE_SERVER_TARGET = "vt_measure_server_target"
CFG_LOGIN_URL = "vt_login_url"
CFG_COOKIE = "vt_cookie"
CFG_LOGIN_EMAIL = "vt_login_email"
CFG_LOGIN_PASSWORD = "vt_login_password"



class VisirTestExperiment(Experiment.Experiment):
    
    def __init__(self, coord_address, locator, cfg_manager, *args, **kwargs):
        super(VisirTestExperiment, self).__init__(*args, **kwargs)
        self._cfg_manager = cfg_manager
        self.read_config()
        
    def read_config(self):
        self.measure_server_addr = self._cfg_manager.get_value(CFG_MEASURE_SERVER_ADDRESS)
        self.measure_server_target = self._cfg_manager.get_value(CFG_MEASURE_SERVER_TARGET)
        #self.cookie = self._cfg_manager.get_value(CFG_COOKIE)
        self.loginurl = self._cfg_manager.get_value(CFG_LOGIN_URL)
        self.login_email = self._cfg_manager.get_value(CFG_LOGIN_EMAIL)
        self.login_password = self._cfg_manager.get_value(CFG_LOGIN_PASSWORD)

    @Override(Experiment.Experiment)
    def do_start_experiment(self):
        print "Measure server address: ", self.measure_server_addr
        print "Measure server target: ", self.measure_server_target
        return "Ok"

    @Override(Experiment.Experiment)
    def do_send_command_to_device(self, command):
        return self.do_send_command_to_device_real(command)
    
    
    def do_send_command_to_device_real(self, command):
        #command = self.transform_request(command)
        
        if command == 'GIVEMECOOKIE':
            # Perform a login
            print "COOKIE REQUESTED"
            cookie = self.perform_visir_web_login(self.loginurl, 
                self.login_email, self.login_password)
            print "COOKIE OBTAINED: ", cookie
            return cookie
        
        return self.send_request(command)
    
    def transform_request(self, command):
        print "Transforming request: ", command
        doc = minidom.parseString(command)
        tags = doc.getElementsByTagName("login")
        if len(tags) == 0:
            return command
        tag = tags[0]
        tag.setAttribute("keepalive", "1")
        command = doc.toxml()
        return command
         
        
        
    def send_request(self, request):
        print "Sending req: ", request
        conn = httplib.HTTPConnection(self.measure_server_addr)
        conn.request("POST", self.measure_server_target, request)
        response = conn.getresponse()
        print response.status, response.reason
        data = response.read()
        conn.close()
        print "Received response: ", data
        return data

    
    def do_send_command_to_device_hc(self, command):
  #      print "Command: %s" % command
        
        if command == 'GIVEMECOOKIE':
            # Perform a login
            print "COOKIE REQUESTED"
            cookie = self.perform_visir_web_login(self.loginurl, "guest", "guest")
            print "COOKIE OBTAINED: ", cookie
            return cookie
        
        doc = minidom.parseString(command)
        protocol_tag = doc.getElementsByTagName("protocol")
        for tag in protocol_tag[0].childNodes:
            if tag.nodeType == tag.ELEMENT_NODE and tag.localName == "login":
                return self.handle_login_command(tag)
            elif tag.nodeType == tag.ELEMENT_NODE and tag.localName == "request":
                return self.handle_response_command(tag)
        return """"""
    
    def handle_response_command_hc(self, tag):
        return """<protocol version="1.3"><response/></protocol>"""

    def handle_login_command_hc(self, tag):
        '''
        Handles a login command.
        @param tag The XML "login" tag describing the command.
        @return Response to the command
        '''
        print "Returning LOGIN command"
        return """<protocol version="1.3"><login sessionkey="123"/></protocol>"""


    def perform_visir_web_login(self, url, email, password):
        '''
        Performs a login through the specified visir web url.
        @param url Url to the file through which to login. May contain
        GET parameters if required.
        @param email Email or account name to use
        @param password Password to use
        @return The cookie that was returned upon a successful login, and
        None upon a failed one
        '''
        
        # Create the POST data with the parameters
        postvals = {'email' : email,
                    'password' : password }
        postdata = urllib.urlencode(postvals)

        # We need to use a Cookie processor to be able to retrieve
        # the auth cookie that we seek
        cp = urllib2.HTTPCookieProcessor()
        o = urllib2.build_opener( cp )
        urllib2.install_opener(o)
        
        # Do the request iself. The cookies retrieved (which should
        # actually be a single cookie) will be stored in the 
        # aforementioned cookie processor's CookieJar
        r = o.open(url, postdata)
        r.close()
        
        # If there is a cookie in the jar, assume it's the one we seek,
        # and return its value.
        for c in cp.cookiejar:
            print "Cookie found: ", c
            return c.value
        
        # No cookies retrieved, login must have failed.
        return None
    

    @Override(Experiment.Experiment)
    def do_send_file_to_device(self, content, file_info):
        print "On send file"
        return "Ok"


    @Override(Experiment.Experiment)
    def do_dispose(self):
        print "On do dispose"
        return "Ok"

