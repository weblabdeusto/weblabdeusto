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

from abc import ABCMeta
import voodoo.log as log

def _extract_ctor_args(klass):
    if hasattr(klass.__init__, '_original_args'):
        return klass.__init__._original_args[1:]
    ctor_func_code = klass.__init__.func_code
    return ctor_func_code.co_varnames[1:ctor_func_code.co_argcount]

def _repr_impl(self):
    """__repr__: it takes all the arguments of the constructor and
    checks for their value in the object"""
    try:
        my_class = type(self)
        ctor_arguments = _extract_ctor_args(my_class)
        repr_str = "%s(" % my_class.__name__

        var_names = {}
        for var_name in ctor_arguments:
            if not hasattr(self, var_name) and hasattr(self, '_%s' % var_name):
                var_names[var_name] = '_%s' % var_name
            elif not hasattr(self, var_name) and hasattr(self, '_%s__%s' % (my_class.__name__, var_name)):
                var_names[var_name] = '_%s__%s' % (my_class.__name__, var_name)
            else:
                var_names[var_name] = var_name

        repr_str += ', '.join([ '%s = %r' % (v, getattr(self, var_names[v])) for v in ctor_arguments ])
        repr_str += ")"
    except:
        log.log(Representable, log.level.Error, "Could not generate a representation of object of type %s" % type(self))
        log.log_exc(Representable, log.level.Error)
        repr_str = '"Could not generate a representation. See the logs"'
    return repr_str

def _eq_impl(self, other):
    """__eq__: checks all the fields that appear as variables in the constructor"""
    if type(self) != type(other):
        return False

    my_class = type(self)

    ctor_arguments = _extract_ctor_args(my_class)

    for var_name in ( var_name for var_name in ctor_arguments ):

        if not hasattr(self, var_name) and hasattr(self, '_%s' % var_name):
            real_var_name = '_%s' % var_name
        elif not hasattr(self, var_name) and hasattr(self, '_%s__%s' % (my_class.__name__, var_name)):
            real_var_name = '_%s__%s' % (my_class.__name__, var_name)
        else:
            real_var_name = var_name

        if not hasattr(other, real_var_name):
            return False

        if getattr(self, real_var_name) != getattr(other, real_var_name):
            return False

    return True

def _ne_impl(self, other):
    return not self.__eq__(other)

def _populate_dict(dict):
    if not '__repr__' in dict:
        dict['__repr__'] = _repr_impl
    if not '__eq__' in dict:
        dict['__eq__']   = _eq_impl
    if not '__ne__' in dict:
        dict['__ne__']   = _ne_impl

def _check_obj(obj):
    my_class = type(obj)

    ctor_arguments = _extract_ctor_args(my_class)

    for field in [ v for v in ctor_arguments ]:
        if not hasattr(obj, field) and not hasattr(obj, '_%s' % field) and not hasattr(obj, '_%s__%s' % (my_class.__name__, field)):
            raise TypeError("%s type %s has no field %s, provided in the constructor" % (Representable.__name__, my_class.__name__, field))

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
        _populate_dict(dict)
        return type.__new__(mcs, name, bases, dict)

    def __call__(*args, **kwargs):
        obj = type.__call__(*args, **kwargs)
        _check_obj(obj)
        return obj

class AbstractRepresentable(ABCMeta):

    """Same as Representable, but inheriting from ABCMeta"""

    def __new__(mcs, name, bases, dict):
        _populate_dict(dict)
        return ABCMeta.__new__(mcs, name, bases, dict)

    def __call__(*args, **kwargs):
        obj = ABCMeta.__call__(*args, **kwargs)
        _check_obj(obj)
        return obj

