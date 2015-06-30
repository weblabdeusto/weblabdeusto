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

import weakref

from voodoo.resources_manager import is_testing

###########################################
#
# By default, it only checks the data
# types whenever we are unit testing.
# This way, we keep the system documented
# and catch the failures while testing,
# but it has no performance impact in
# production.
#
CHECKING = __debug__ and is_testing()

ANY  = object()
NONE = type(None)

ITERATION_TYPE  = object()
LIST_TYPE       = object()
TUPLE_TYPE      = object()

def LIST(list_type):
    """Check that it is a list of elements of type list_type"""
    return (LIST_TYPE, list_type)

def TUPLE(tuple_type):
    """Check that it is a tuple of elements of type tuple_type"""
    return (TUPLE_TYPE, tuple_type)

def ITERATION(iteration_type):
    """Check that it is any kind of iteration of elements of type iteration_type"""
    return (ITERATION_TYPE, iteration_type)

def _check_types(func, args, kwargs, types):
    default_number = 0 if func.func_defaults is None else len(func.func_defaults)
    if len(args) + len(kwargs) > len(types) or default_number + len(args) + len(kwargs) < len(types):
        raise TypeError("%s: %s types provided but %s arguments passed" % (func.__name__, len(types), (len(args) + len(kwargs))))

    is_class = hasattr(func, 'im_func')
    func_code = func.func_code
    var_names = func_code.co_varnames[:func_code.co_argcount]
    if is_class:
        var_names = var_names[1:]

    kwargs_var_names = var_names[len(args):]

    NOT_FOUND = object()

    kwargs_var_values = map(lambda arg_name : kwargs.get(arg_name, NOT_FOUND), kwargs_var_names)

    if NOT_FOUND in kwargs_var_values:
        default_names = func.func_code.co_varnames[func.func_code.co_argcount - len(func.func_defaults):func.func_code.co_argcount]
        for name, value in zip(kwargs_var_names, kwargs_var_values):
            if not name in default_names:
                raise TypeError("Argument missing: %s" % name)

    complete_ordered_args_list = list(args) + kwargs_var_values

    for pos, (arg, arg_type) in enumerate(zip(complete_ordered_args_list, types)):
        if arg == NOT_FOUND:
            continue

        if arg_type == ANY:
            continue

        if isinstance(arg_type, tuple) and arg_type[0] in (LIST_TYPE, TUPLE_TYPE, ITERATION_TYPE):
            if len(var_names) > pos:
                var_name = var_names[pos]
            else:
                var_name = "Unknown variable name, one of %s" % (var_names,)

            if arg_type[0] == LIST_TYPE and not isinstance(arg, list):
                raise TypeError("Expected argument type for '%s' on method '%s': %s. Got: %s" % (var_name, func.__name__, list, type(arg)))
            elif arg_type[0] == TUPLE_TYPE and not isinstance(arg, tuple):
                raise TypeError("Expected argument type for '%s' on method '%s': %s. Got: %s" % (var_name, func.__name__, tuple, type(arg)))

            for element in arg:
                if not isinstance(element, arg_type[1]):
                    raise TypeError("Expected argument type for '%s' on method '%s': %s. Got: %s" % (var_name, func.__name__, arg_type[1], type(element)))
            continue

        if isinstance(arg_type, basestring):
            arg_type = func.func_globals.get(arg_type)

        if not isinstance(arg, arg_type):
            if len(var_names) > pos:
                var_name = var_names[pos]
            else:
                var_name = "Unknown variable name, one of %s" % (var_names,)
            raise TypeError("Expected argument type for '%s' on method '%s': %s. Got: %s" % (var_name, func.__name__, arg_type, type(arg)))


def dummytypecheck(func):
    return func

def typecheck(*types, **kwargs):
    if not CHECKING:
        return dummytypecheck

    class TypeChecker(object):
        def __init__(self, func):
            self.func = func
            self.obj  = None
            self.__name__      = self.func.__name__
            self.__doc__       = self.func.__doc__
            self.func_varnames = self.func.func_code.co_varnames
            self.func_argcount = self.func.func_code.co_argcount
            self.func_code     = self.func.func_code
            self._original_args = self.func_varnames[0:self.func_argcount]
            if kwargs.get('check_module', False):
                for t in types:
                    if isinstance(t, basestring):
                        if not t in func.func_globals:
                            raise TypeError("Type %s not found in the scope of function %s" % (t, func))

        def __get__(self, obj, type = None):
            if obj is not None:
                self.obj = weakref.ref(obj)
            return self.__class__(self.func.__get__(obj, type))

        def __call__(self, *args, **kwargs):
            if CHECKING:
               _check_types(self.func, args, kwargs, types)

            if self.obj is not None:
                return self.func(self, *args, **kwargs)
            else:
                return self.func(*args, **kwargs)

    return TypeChecker

def typecheckprop(*types):
    return typecheck(ANY, *types)

typecheck.NONE      = NONE
typecheck.ANY       = ANY
typecheck.LIST      = LIST
typecheck.TUPLE     = TUPLE
typecheck.ITERATION = ITERATION
