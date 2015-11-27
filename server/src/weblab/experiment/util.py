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

import base64

# This class doesn't inherit from WebLabError since it is used in fileUpload.py
# Inheriting from WebLabError would mean that we would need to load weblab.exceptions
# in fileUpload.py
class UnableToDeserializeError(Exception):
    def __init__(self,*args,**kargs):
        Exception.__init__(self,*args,**kargs)

def serialize(file_content):
    """
    Serializes into base64.
    :param file_content: The string to serialize. If it was an unicode string, errors could occur.
    :type file_content: str
    :return:
    """
    result = base64.encodestring(file_content)
    return result

def deserialize(serialized_content):
    try:
        deserialized_content = base64.decodestring(serialized_content)
    except Exception as e:
        raise UnableToDeserializeError("Couldn't deserialize base64 content: %s" % serialized_content, e)
    return deserialized_content

