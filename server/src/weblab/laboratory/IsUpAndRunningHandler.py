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
# Author: Jaime Irurzun <jaime.irurzun@gmail.com>
#

"""
IsUpAndRunningHandler allow the LaboratoryServer to check if a certain
resource or connectivity aspect related to a experiment is working properly. This
is intended to be used for checking common issues to most of the
experiments. Examples:
   -> Is that webcam (url) returning a JPG image?
   -> Is that host (ip, port) listening?
"""

import urllib2
import socket

from voodoo.override import Override
from weblab.exceptions.laboratory import LaboratoryExceptions as Laboratory


VALID_IMAGE_FORMATS = ('image/jpg',)


class AbstractIsUpAndRunningHandler(object):
    
    def run(self):
        raise NotImplementedError()

HANDLERS = ()


class HostIsUpAndRunningHandler(AbstractIsUpAndRunningHandler):
    
    _socket = socket
    
    def __init__(self, hostname, port):
        super(HostIsUpAndRunningHandler, self).__init__()
        self.hostname = hostname
        self.port = port
        
    @Override(AbstractIsUpAndRunningHandler)
    def run(self):
        s = self._socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((self.hostname, self.port))
        except socket.error, e:
            raise Laboratory.UnableToConnectHostnameInPortException(self.hostname, self.port, e)
        finally:
            s.close()

HANDLERS += ('HostIsUpAndRunningHandler',)
        

class WebcamIsUpAndRunningHandler(AbstractIsUpAndRunningHandler):
    
    _urllib2 = urllib2
    
    def __init__(self, img_url):
        super(WebcamIsUpAndRunningHandler, self).__init__()
        self.img_url = img_url
        
    @Override(AbstractIsUpAndRunningHandler)
    def run(self):
        try:
            response = self._urllib2.urlopen(self.img_url)
        except urllib2.URLError, e:
            raise Laboratory.ImageURLDidNotRetrieveAResponseException(self.img_url, e)
        if response.headers['content-type'] not in VALID_IMAGE_FORMATS:
            raise Laboratory.InvalidContentTypeRetrievedFromImageURLException(self.img_url)

HANDLERS += ('WebcamIsUpAndRunningHandler',)