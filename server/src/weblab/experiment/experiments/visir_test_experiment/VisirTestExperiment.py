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

from voodoo.override import Override


class VisirTestExperiment(Experiment.Experiment):
    
    def __init__(self, coord_address, locator, cfg_manager, *args, **kwargs):
        super(VisirTestExperiment, self).__init__(*args, **kwargs)

    @Override(Experiment.Experiment)
    def do_start_experiment(self):
        print "do_start_experiment"
        return "Ok"

    @Override(Experiment.Experiment)
    def do_send_command_to_device(self, command):
        print "Command: %s" % command
        doc = minidom.parseString(command)
        protocol_tag = doc.getElementsByTagName("protocol")
        for tag in protocol_tag[0].childNodes:
            if tag.nodeType == tag.ELEMENT_NODE and tag.localName == "login":
                return self.handle_login_command(tag)
            elif tag.nodeType == tag.ELEMENT_NODE and tag.localName == "request":
                return self.handle_response_command(tag)
        return """"""
    
    
    def handle_response_command(self, tag):
        return """<protocol version="1.3"><response/></protocol>"""


    def handle_login_command(self, tag):
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

