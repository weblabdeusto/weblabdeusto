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

"""
IsUpAndRunningHandler allow the LaboratoryServer to check if a certain
resource or connectivity aspect related to a experiment is working properly. This
is intended to be used for checking common issues to most of the
experiments. Examples:
   -> Is that webcam (url) returning a JPG image?
   -> Is that host (ip, port) listening?
All these requests will not require a slot in the scheduling system, so they can
be requested at any moment, even if there is a user using the experiment.
"""

import json
import urllib2
import socket
from abc import ABCMeta, abstractmethod

from voodoo.override import Override
import weblab.lab.exc as labExc


VALID_IMAGE_FORMATS = ('image/jpg','image/png','image/jpeg')


class AbstractLightweightIsUpAndRunningHandler(object):

    DEFAULT_TIMES = 1

    __metaclass__ = ABCMeta

    def __init__(self, times = None, *args, **kwargs):
        if times is not None:
            self.times = times
        else:
            self.times = self.DEFAULT_TIMES

    def run_times(self):
        messages = []
        for _ in xrange(self.times):
            try:
                self.run()
            except Exception as e:
                messages.append("%s: %s" % (type(e).__name__,str(e)))
            else:
                return []
        return messages

    @abstractmethod
    def run(self):
        pass

HANDLERS = ()


class HostIsUpAndRunningHandler(AbstractLightweightIsUpAndRunningHandler):

    _socket = socket
    DEFAULT_TIMES = 2

    def __init__(self, hostname, port, *args, **kwargs):
        super(HostIsUpAndRunningHandler, self).__init__(*args, **kwargs)
        self.hostname = hostname
        self.port = port

    @Override(AbstractLightweightIsUpAndRunningHandler)
    def run(self):
        s = self._socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((self.hostname, self.port))
        except Exception as e:
            raise labExc.UnableToConnectHostnameInPortError(self.hostname, self.port, e)
        finally:
            s.close()

    def __repr__(self):
        return "HostIsUpAndRunningHandler(hostname=%r, port=%r)" % (self.hostname, self.port)

HANDLERS += (HostIsUpAndRunningHandler.__name__,)


class WebcamIsUpAndRunningHandler(AbstractLightweightIsUpAndRunningHandler):

    _urllib2 = urllib2
    DEFAULT_TIMES = 3

    def __init__(self, img_url, *args, **kwargs):
        self.timeout = kwargs.pop('timeout', 10)
        super(WebcamIsUpAndRunningHandler, self).__init__(*args, **kwargs)
        self.img_url = img_url

    @Override(AbstractLightweightIsUpAndRunningHandler)
    def run(self):
        try:
            response = self._urllib2.urlopen(self.img_url, timeout = self.timeout)
        except Exception as e:
            raise labExc.ImageURLDidNotRetrieveAResponseError(self.img_url, e)

        if response.headers['content-type'] not in VALID_IMAGE_FORMATS:
            raise labExc.InvalidContentTypeRetrievedFromImageURLError(self.img_url)

    def __repr__(self):
        return "WebcamIsUpAndRunningHandler(img_url=%r)" % self.img_url

HANDLERS += (WebcamIsUpAndRunningHandler.__name__,)

class WebHandler(AbstractLightweightIsUpAndRunningHandler):

    _urllib2 = urllib2
    DEFAULT_TIMES = 3

    def __init__(self, url, *args, **kwargs):
        self.timeout = kwargs.pop('timeout', 10)
        super(WebHandler, self).__init__(*args, **kwargs)
        self.url = url

    @Override(AbstractLightweightIsUpAndRunningHandler)
    def run(self):
        try:
            response = self._urllib2.urlopen(self.url, timeout = self.timeout)
            str_contents = response.read()
        except Exception as e:
            raise labExc.WebHandlerInvalidResponseHandlerError(self.url, e)

        try:
            contents = json.loads(str_contents)
        except Exception as e:
            raise labExc.WebHandlerInvalidFormatHandlerError(self.url, e)

        if not contents.get('success', False):
            raise labExc.WebHandlerReturnedErrorHandlerError(self.url, contents)


    def __repr__(self):
        return "WebHandler(url=%r)" % self.url

HANDLERS += (WebHandler.__name__,)

