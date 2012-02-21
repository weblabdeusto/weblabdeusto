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
# Author: Pablo Orduña <pablo@ordunya.com>
#
import voodoo.sessions.session_type as SessionType
import voodoo.sessions.exc as SessionErrors

def get_gateway_class(session_type):
    if session_type == SessionType.Memory:
        from voodoo.sessions.memory import SessionMemoryGateway
        return SessionMemoryGateway
    elif session_type == SessionType.sqlalchemy:
        from voodoo.sessions.sqlalchemy_gateway import SessionSqlalchemyGateway
        return SessionSqlalchemyGateway
    else:
        raise SessionErrors.SessionTypeNotImplementedError(
                "Session Type %s not implemented" % session_type.name
            )

