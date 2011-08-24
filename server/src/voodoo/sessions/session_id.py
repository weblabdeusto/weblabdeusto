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
# Author: Pablo Orduña <pablo@ordunya.com>
# 

class SessionId(object):
    def __init__(self, real_id):
        object.__init__(self)

        if isinstance(real_id,basestring):
            self.id = real_id
        else:
            # This object will be used by the webserver module
            # and this part will not work, but will neither be ever used
            import voodoo.exceptions.sessions.SessionExceptions as SessionExceptions
            raise SessionExceptions.SessionInvalidSessionIdException(
                "Not a string: %s" % real_id
            )
    
    def __cmp__(self, other):
        if isinstance(other,SessionId):
            return cmp(self.id,other.id)
        else:
            try:
                return cmp(hash(self.id),hash(other))
            except TypeError:
                return 1

    def __eq__(self, other):
        return self.__cmp__(other) == 0

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return "<Session ID: '%s'>" % self.id

    def __str__(self):
        return "Session ID: '%s'" % self.id

