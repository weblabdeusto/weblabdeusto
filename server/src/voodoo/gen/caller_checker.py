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

ALL = 'All servers'

def caller_check(servers = ALL):
    def func_wrapper(func):
        def wrapped_func(*args, **kargs):
            # TODO
            try:
                a = servers[0]
            except TypeError,e:
                all_servers = (servers,)
            else:
                all_servers = servers
            #TODO: work with all_servers
            return func(*args,**kargs)
        wrapped_func.__name__ = func.__name__
        wrapped_func.__doc__ = func.__doc__
        return wrapped_func
    return func_wrapper

