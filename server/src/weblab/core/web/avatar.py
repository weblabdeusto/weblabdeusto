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

import hashlib

from flask import redirect, request
from weblab.core.wl import weblab_api
from weblab.core.exc import DatabaseError

# TODO: in the future, instead of login, we should use another field such as
# anonymous identifier or so
@weblab_api.route_web('/avatar/<login>/')
def avatar(login):
    try:
        response = weblab_api.db.retrieve_avatar_user_auths(login)
    except DatabaseError:
        return "Login not found", 404
    else:
        if response is None:
            return "Login not found", 404

    email, auths = response

    size = request.args.get('size', '50')

    for auth_type_name, auth_name, auth_config, user_auth_config in auths:
        if auth_type_name == 'FACEBOOK':
            return redirect("http://graph.facebook.com/{user_id}/picture?type=square&height={size}".format(user_id = user_auth_config, size=size))
        # Other cases here...

    return redirect('http://www.gravatar.com/avatar/{md5}?d=identicon&s={size}'.format(md5=hashlib.md5(email).hexdigest(), size=size))

