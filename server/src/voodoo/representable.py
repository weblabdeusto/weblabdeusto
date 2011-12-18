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

def _repr_impl(self):
    """__repr__: it takes all the arguments of the constructor and
    checks for their value in the object"""
    my_class = type(self)
    repr_str = "%s(" % my_class.__name__
    repr_str += ', '.join([ '%s = %r' % (v, getattr(self, v)) for v in my_class.__init__.func_code.co_varnames[1:] ])
    repr_str += ")"
    return repr_str

def _eq_impl(self, other):
    """__eq__: checks all the fields that appear as variables in the constructor"""
    if type(self) != type(other):
        return False

    for var_name in ( var_name for var_name in type(self).__init__.func_code.co_varnames[1:] ):

        if not hasattr(other, var_name):
            return False

        if getattr(self, var_name) != getattr(other, var_name):
            return False

    return True

class Representable(type):
    """Metaclass that defines the __repr__ and __eq__ methods of a class. When creating an instance
    of the class, it checks that all the arguments of the __init__ method exist in the resulting 
    object. For instance:
    
    >>> class A(object):
    ...     __metaclass__ = Representable
    ...     def __init__(self, field1, field2):
    ...         self.field1 = field1
    ...         self.field2 = field2
    ... 
    >>> 
    
    In this case, the metaclass will check that field1 and field2 are set in __init__. Failing to
    do so will complain with a TypeError. Once thisis validated, any instance will have a standard
    repr method implementation:
    
    >>> a = A('one', 2)
    >>> a 
    A(field1 = 'one', field2 = 2)
    >>> 
    """
    def __new__(mcs, name, bases, dict):
        if not '__repr__' in dict:
            dict['__repr__'] = _repr_impl
        if not '__eq__' in dict:
            dict['__eq__']   = _eq_impl
        return type.__new__(mcs, name, bases, dict)

    def __call__(*args, **kwargs):
        obj = type.__call__(*args, **kwargs)
        my_class = type(obj)
        for field in [ v for v in my_class.__init__.func_code.co_varnames[1:] ]:
            if not hasattr(obj, field):
                raise TypeError("%s type %s has no field %s, provided in the constructor" % (Representable.__name__, my_class.__name__, field))

        return obj

