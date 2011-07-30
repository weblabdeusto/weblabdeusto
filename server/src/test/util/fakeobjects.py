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

from urllib import addinfourl
from cStringIO import StringIO

class fakeaddinfourl(addinfourl):
  def __init__(self, response='', headers={}, url=''):
    if isinstance(response, basestring):
      response = StringIO(response)
    addinfourl.__init__(self, response, headers, url)