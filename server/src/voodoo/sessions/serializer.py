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
from __future__ import print_function, unicode_literals
import cPickle as pickle

import voodoo.sessions.exc as SessionErrors

class SessionSerializer(object):
    def serialize(self,sess_obj):
        try:
            sess_obj_serialized = pickle.dumps(sess_obj)
        except (pickle.PickleError, TypeError) as pe:
            raise SessionErrors.SessionNotSerializableError(
                    "Session object not serializable with pickle: %s" % pe,
                    pe
            )
        return "{pickle}".encode() + sess_obj_serialized

    def deserialize(self,sess_obj_serialized):
        if sess_obj_serialized.startswith("{pickle}".encode()):
            sos = sess_obj_serialized[len("{pickle}".encode()):]
            try:
                deserialized = pickle.loads(sos)
            except (pickle.PickleError, TypeError) as pe:
                raise SessionErrors.SessionNotDeserializableError(
                    "Session object not deserializable with pickle: %s" % pe,
                    pe
            )

            return deserialized
        else:
            raise SessionErrors.SessionSerializationNotImplementedError(
                    "Session serialization not implemented"
                )

