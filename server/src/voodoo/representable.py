#!/usr/bin/env python
#-*-*- encoding: utf-8 -*-*-
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

class Representable(object):
    def __repr__(self):
        my_class = type(self)
        repr_str = "%s(" % my_class.__name__
        repr_str += ', '.join([ '%s = %r' % (v, getattr(self, v)) for v in my_class.__init__.func_code.co_varnames[1:] ])
        repr_str += ")"
        return repr_str

    def __eq__(self, other):
        if type(self) != type(other):
            return False

        for var_name in ( var_name for var_name in type(self).__init__.func_code.co_varnames[1:] ):

            if not hasattr(other, var_name):
                return False

            if getattr(self, var_name) != getattr(other, var_name):
                return False

        return True

