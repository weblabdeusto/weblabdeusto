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

import base64

# This class doesn't inherit from WebLabException since it is used in fileUpload.py
# Inheriting from WebLabException would mean that we would need to load weblab.exceptions
# in fileUpload.py
class UnableToDeserializeException(Exception):
    def __init__(self,*args,**kargs):
        Exception.__init__(self,*args,**kargs)

def serialize(file_content):
    result = base64.encodestring(file_content)
    return result

def deserialize(serialized_content):
    try:
        deserialized_content = base64.decodestring(serialized_content)
    except Exception, e:
        raise UnableToDeserializeException("Couldn't deserialize base64 content: %s" % serialized_content, e)
    return deserialized_content

