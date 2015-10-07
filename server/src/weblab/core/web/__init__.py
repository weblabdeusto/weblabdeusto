#!/usr/bin/env python
#-*-*- encoding: utf-8 -*-*-
#
# Copyright (C) 2014 onwards University of Deusto
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#
# This software consists of contributions made by many individuals,
# listed below:
#
# Author: Pablo Orduña <pablo@ordunya.com>
#
from __future__ import print_function, unicode_literals

from weblab.core.wl import weblab_api
assert weblab_api is not None # avoid warnings
from flask import request

def get_argument(name, default = None):
    value = request.args.get(name)
    if value is None: 
        if request.method == 'POST':
            return request.form.get(name, default)
        return default
    return value

import language
assert language is not None # avoid warnings

import client
assert client is not None # avoid warnings

import direct2experiment
assert direct2experiment is not None # avoid warnings

import ilab
assert ilab is not None # avoid warnings

import labview
assert labview is not None # avoid warnings

import upload
assert upload is not None # avoid warnings

import visir
assert visir is not None # avoid warnings

import configuration
assert configuration is not None # avoid warnings

import i18n
assert i18n is not None # avoid warnings

import quickadmin
assert quickadmin is not None # avoid warnings

import version
assert version is not None # avoid warnings

import client_config
assert client_config is not None # avoid warnings

import logo
assert logo is not None # avoid warnings

import avatar
assert avatar is not None # avoid warnings

import pub
assert pub is not None # avoid warnings

