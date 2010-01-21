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

class AlgorithmNotFoundException(Exception):
    def __init__(self, *args, **kargs):
        Exception.__init__(self, *args, **kargs)

def new(name):
    try:
        import hashlib
    except ImportError, ie:
        if name == 'md5':
            import md5
            return md5.new()
        elif name == 'sha' or name =='sha1':
            import sha
            return sha.new()
        else:
            raise AlgorithmNotFoundException("Algorithm not found: %s" % name)
    else:
        try:
            return hashlib.new(name)
        except ValueError, ve:
            raise AlgorithmNotFoundException("Algorithm not found: %s" % name)

    
