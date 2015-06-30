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
# Author: Jaime Irurzun <jaime.irurzun@gmail.com>
#
from __future__ import print_function, unicode_literals

import urllib2

import weblab.experiment.devices.exc as DeviceErrors

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
            raise WlHttpDeviceHTTPErrorError(e)
        except urllib2.URLError as e:
            raise WlHttpDeviceURLErrorError(e)
        except Exception as e:
            raise WlHttpDeviceError(e)

class WlHttpDeviceError(DeviceErrors.DeviceError):
    def __init__(self, msg):
        DeviceErrors.DeviceError.__init__(self, "Exception related to Weblab's Http device: %s" % msg)

class WlHttpDeviceURLErrorError(WlHttpDeviceError):
    def __init__(self, e = None):
        text = "Failed reaching the server"
        if hasattr(e, "reason"):
            text += ": %(r)s" % {'r':e.reason}
        WlHttpDeviceError.__init__(self, text)

class WlHttpDeviceHTTPErrorError(WlHttpDeviceError):
    def __init__(self, e = None):
        text = "The server couldn't fulfill the request"
        if hasattr(e, "code"):
            text += ": %(c)i" % {'c':e.code}
        else:
            text += ": %s" % e
        WlHttpDeviceError.__init__(self, text)
