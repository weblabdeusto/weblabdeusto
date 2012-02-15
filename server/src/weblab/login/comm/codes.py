#!/usr/bin/env python
#-*-*- encoding: utf-8 -*-*-
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
# Author: Pablo Orduña <pablo@ordunya.com>
#

CLIENT_INVALID_CREDENTIALS_EXCEPTION_CODE = 'Client.InvalidCredentials'
LOGIN_SERVER_EXCEPTION_CODE               = 'Server.Login'

# Imported this way instead of from RFMC import *
# to avoid warnings from pyflakes
import weblab.comm.codes as CommonCodes

WEBLAB_GENERAL_EXCEPTION_CODE = CommonCodes.WEBLAB_GENERAL_EXCEPTION_CODE
VOODOO_GENERAL_EXCEPTION_CODE = CommonCodes.VOODOO_GENERAL_EXCEPTION_CODE
PYTHON_GENERAL_EXCEPTION_CODE = CommonCodes.PYTHON_GENERAL_EXCEPTION_CODE
