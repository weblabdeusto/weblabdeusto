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

from urllib import addinfourl
from cStringIO import StringIO


class fakeaddinfourl(addinfourl):

    def __init__(self, response='', headers={}, url=''):
        if isinstance(response, basestring):
            response = StringIO(response)
        addinfourl.__init__(self, response, headers, url)


class return_values(object):

    def __init__(self, values):
        self.values = values
        self.values.reverse()

    def __call__(self, *args, **kwargs):
        return self.values.pop()
