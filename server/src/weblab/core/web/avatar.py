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
from __future__ import print_function, unicode_literals

from weblab.core.wl import weblab_api
from weblab.core.exc import DatabaseError

# TODO: in the future, instead of login, we should use another field such as
# anonymous identifier or so
@weblab_api.route_web('/avatar/<login>/')
def avatar(login):
    try:
        auths = weblab_api.db.retrieve_role_user_auths(login)
    except DatabaseError:
        return "Login not found", 404
    else:
        if auths is None:
            return "Login not found", 404

    # avatars = []
    # [ auth.auth_type for auth in auths ]
    return "avatar not yet implemented"

