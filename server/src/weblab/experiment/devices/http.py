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
import weblab.exceptions.experiment.devices.http_device.WlHttpDeviceExceptions as WlHttpDeviceExceptions

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
        except urllib2.HTTPError, e:
            raise WlHttpDeviceExceptions.WlHttpDeviceHTTPErrorException(e)
        except urllib2.URLError, e:
            raise WlHttpDeviceExceptions.WlHttpDeviceURLErrorException(e)
        except Exception, e:
            raise WlHttpDeviceExceptions.WlHttpDeviceException(e)


