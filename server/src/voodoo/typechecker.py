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

import weakref
from functools import wraps

CHECKING = True

ANY  = object()
NONE = type(None)

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

        if not isinstance(arg, arg_type):
            raise TypeError("Expected argument type for '%s' on method '%s': %s. Got: %s" % (var_names[pos], func.__name__, arg_type, type(arg)))
        

def dummytypecheck(func):
    return func

def typecheck(*types):
    if not CHECKING:
        return dummytypecheck

    class TypeChecker(object):
        def __init__(self, func):
            self.func = func
            self.obj  = None
            self.func_varnames = self.func.func_code.co_varnames
            self.func_argcount = self.func.func_code.co_argcount
            self._original_args = self.func_varnames[0:self.func_argcount]

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

typecheck.NONE = NONE
typecheck.ANY  = ANY
