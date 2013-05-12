#!/usr/bin/env python
#-*-*- encoding: utf-8 -*-*-
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
# Author: Pablo Orduña <pablo@ordunya.com>
#

#
# The systems presented in this file are those which delegate to
# other system the authentication, so no password is sent to LoginServer
# but external tokens. This can be the case of Facebook or SecondLife
#

from weblab.login.web.openid_web import OpenIDManager
from weblab.login.web.facebook import FacebookManager

WEB_PROTOCOL_AUTHN = {
    'FACEBOOK' : FacebookManager(),
    'OPENID'   : OpenIDManager(),
}

