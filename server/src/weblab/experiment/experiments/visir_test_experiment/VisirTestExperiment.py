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

from voodoo.override import Override




class VisirTestExperiment(Experiment.Experiment):
    
    MEASURE_SERVER_ADDR = "130.206.138.35:8080"
    MEASURE_SERVER_TARGET = "/measureserver"
    
    def __init__(self, coord_address, locator, cfg_manager, *args, **kwargs):
        super(VisirTestExperiment, self).__init__(*args, **kwargs)

    @Override(Experiment.Experiment)
    def do_start_experiment(self):
        print "do_start_experiment"
        return "Ok"

    @Override(Experiment.Experiment)
    def do_send_command_to_device(self, command):
        return self.do_send_command_to_device_real(command)
    
    
    def do_send_command_to_device_real(self, command):
        command = self.transform_request(command)
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
        print "Sending request: ", request
        conn = httplib.HTTPConnection(VisirTestExperiment.MEASURE_SERVER_ADDR)
        conn.request("POST", VisirTestExperiment.MEASURE_SERVER_TARGET, request)
        response = conn.getresponse()
        print response.status, response.reason
        data = response.read()
        conn.close()
        print "Received response: ", data
        return data

    
    def do_send_command_to_device_hc(self, command):
        print "Command: %s" % command
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


    @Override(Experiment.Experiment)
    def do_send_file_to_device(self, content, file_info):
        print "On send file"
        return "Ok"


    @Override(Experiment.Experiment)
    def do_dispose(self):
        print "On do dispose"
        return "Ok"

