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

import urllib2

import weblab.experiment.devices.exc as DeviceExceptions

class HttpDevice(object):

    def __init__(self, hostname, port, app=""):
        self.hostname = hostname
        self.port = port
        self.app = app

    def send_message(self, text):
        try:
            full_url = "http://%(host)s:%(port)s/%(app)s" % {
                        'host':self.hostname,
                        'port':self.port,
                        'app':self.app
                    }
            url = urllib2.urlopen( full_url, text )
            return url.read()
        except urllib2.HTTPError as e:
            raise WlHttpDeviceHTTPErrorException(e)
        except urllib2.URLError as e:
            raise WlHttpDeviceURLErrorException(e)
        except Exception as e:
            raise WlHttpDeviceException(e)

class WlHttpDeviceException(DeviceExceptions.DeviceException):
    def __init__(self, msg):
        DeviceExceptions.DeviceException.__init__(self, "Exception related to Weblab's Http device: %s" % msg)
 
class WlHttpDeviceURLErrorException(WlHttpDeviceException):
    def __init__(self, e = None):
        text = "Failed reaching the server"
        if hasattr(e, "reason"):
            text += ": %(r)s" % {'r':e.reason}
        WlHttpDeviceException.__init__(self, text)

class WlHttpDeviceHTTPErrorException(WlHttpDeviceException):
    def __init__(self, e = None):
        text = "The server couldn't fulfill the request"
        if hasattr(e, "code"):
            text += ": %(c)i" % {'c':e.code}        
        else:
            text += ": %s" % e
        WlHttpDeviceException.__init__(self, text)
