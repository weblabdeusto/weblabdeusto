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
# Author: Luis Rodriguez <luis.rodriguez@opendeusto.es>
#
from __future__ import print_function, unicode_literals

STATUS_RUNNING  = "running"
STATUS_OK       = "ok"
STATUS_ERROR    = "error"

# TODO: The following class seems to actually be not necessary. Consider removing
# this whole file.
#
#class AsyncRequest(object):
#    """
#    Contains information about the state and result of an asynchronous request.
#    """
#
#    def __init__(self, request_id, threadobj = None):
#        """
#        Creates a new AsyncRequest object, which will be identified
#        through its request_id.
#        """
#        self._request_id = request_id
#        self._status = STATUS_RUNNING
#        self._command = None
#        self._contents = None
#        self._thread = threadobj
#
#    def get_contents(self):
#        """
#        Retrieves the contents field of the async request. If the content has finished
#        successfully, that will be the response text. If it has failed, it will be
#        the error message.
#        """
#        return self._command
#
#    def get_request_id(self):
#        """ Retrieves the request's identifier. """
#        return self._request_id
#
#    def get_status(self):
#        """ Retrieves the request's status. """
#        return self._status
#
#    def get_thread(self):
#        """
#        Retrieves the thread object that is running the request.
#        May return None.
#        """
#        return self._thread