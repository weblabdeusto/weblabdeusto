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
import six
import sys
import time
import traceback
import math
import random
import logging
import threading
from functools import wraps
from voodoo.cache import fast_cache

class level(object):
    Critical = 'Critical'
    Error    = 'Error'
    Warning  = 'Warning'
    Info     = 'Info'
    Debug    = 'Debug'

def critical(instance_or_module_or_class, message, max_size = 250):
    return log(instance_or_module_or_class, level.Critical, message, max_size)

def error(instance_or_module_or_class, message, max_size = 250):
    return log(instance_or_module_or_class, level.Error, message, max_size)

def warning(instance_or_module_or_class, message, max_size = 250):
    return log(instance_or_module_or_class, level.Warning, message, max_size)

def info(instance_or_module_or_class, message, max_size = 250):
    return log(instance_or_module_or_class, level.Info, message, max_size)

def debug(instance_or_module_or_class, message, max_size = 250):
    return log(instance_or_module_or_class, level.Debug, message, max_size)

def log(instance_or_module_or_class, level, message, max_size = 250):
    logging_log_level = getattr(logging,level.upper())
    if isinstance(instance_or_module_or_class,str):
        logger_name = instance_or_module_or_class
    elif isinstance(instance_or_module_or_class, six.class_types):
        logger_name = instance_or_module_or_class.__module__ + '.' + instance_or_module_or_class.__name__
    else:
        logger_name = instance_or_module_or_class.__class__.__module__ + '.' + instance_or_module_or_class.__class__.__name__
    logger = logging.getLogger(logger_name)
    if not logger.isEnabledFor(logging_log_level):
        return

    message_repr = repr(message)
    if len(message_repr) > max_size:
        message_repr = message_repr[:max_size-3] + '...'

    logger.log(logging_log_level,message_repr)

def critical_exc(instance_or_module_or_class):
    return log_exc(instance_or_module_or_class, level.Critical)

def error_exc(instance_or_module_or_class):
    return log_exc(instance_or_module_or_class, level.Error)

def warning_exc(instance_or_module_or_class):
    return log_exc(instance_or_module_or_class, level.Warning)

def info_exc(instance_or_module_or_class):
    return log_exc(instance_or_module_or_class, level.Info)

def debug_exc(instance_or_module_or_class):
    return log_exc(instance_or_module_or_class, level.Debug)

def log_exc(instance_or_module_or_class, level):
    f = six.StringIO()
    traceback.print_exc(file=f)
    lines = f.getvalue().split('\n')
    for line in lines:
        log(instance_or_module_or_class, level, line)

_BASE_CALL_ID_STR = time.strftime("%Y_%m_%d-%H:%M:%S-",time.gmtime())
_CALL_ID_ALPHABET = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

@fast_cache
def _get_full_class_name(class_type, func):
    func_name = func.__name__

    def find_class(cur_class, func_name):
        if func_name in cur_class.__dict__:
            return cur_class
        for base_class in cur_class.__bases__:
            found = find_class(base_class, func_name)
            if found is not None:
                return found
        return None

    result = find_class(class_type, func_name)
    return result.__module__ + '.' + result.__name__

@fast_cache
def _get_logger(logger_name):
    """ logging.getLogger scales very bad when using threads. Caching its result is far faster """
    return logging.getLogger(logger_name)

# This code defers the logging requests to a thread pool
# It's experimental code, so by default it's not enabled

def logged(level='debug', except_for=None, max_size = 250, is_class_method = True, ctxt_retriever = None):
    """
    logged([except_for]) -> function

    Logged will return a new function "f", with same __doc__ and __name__, but internally it will
    call logging.getLogger(str(self.__class__)) (so use only with methods!) before and after
    calling the function itself.

    If you don't want all parameters to be showed, use except_for providing a sequence of the parameters
    you want to hide, being each parameter identified by:

     * the name of the parameter.
     * the position of the parameter (an integer).
     * a tuple of (name, position).

    If you only provide the name, it will try to infer the position. For instance:

        @logged(except_for=('password',))
        def login(self, username, password):
            pass

        login("foo","bar")

    will work, since it will infer that "password" is the second parameter. However, if you do something
    like:

        @logged(except_for=('password',))
        @cache
        def login(self, username, password):
            pass

        login("foo",password="bar")
        login("foo","bar")

    Then the first one will work, but for the second call it will be impossible to infer it,
    so a warning will be displayed in stderr. In this case, it would also work:

        @logged(except_for=(2,))
        @cache
        def login(self, username, password):
           pass

        login("foo","bar") # Works

    or:

        @logged(except_for=(('password',2),))
        @cache
        def login(self, username, password):
           pass

        login("foo","bar") # Works
        login("foo",password="bar") # Works

    You can also provide a single parameter by providing only the name or the position.

    Instead of these values, it will say "<hidden>".
    """
    _levelname = level.lower()
    if not hasattr(logging, _levelname):
        raise RuntimeError("level %s does not exist")

    def real_logger(f):
        # parameter_names is a list. Being "f" defined like:
        # def f(name1,name2,name3,*args,**kargs):
        # parameter_names will be ['name1','name2','name3']
        parameter_names = list(f.func_code.co_varnames[:f.func_code.co_argcount])
        func_name       = f.__name__

        levelname       = _levelname
        uplevelname     = _levelname.upper()
        logging_level   = getattr(logging, uplevelname)

        class LogEntry(object):
            def __init__(self):
                self._call_id           = None
                self._current_thread    = None
                self._initial_strtime = None

            @property
            def initial_strtime(self):
                if self._initial_strtime is None:
                    call_time  = time.time()
                    local_time = time.localtime(call_time)
                    millis     = call_time - math.floor(call_time)
                    self._initial_strtime = '<' + time.strftime("%Y-%m-%d %H:%M:%S", local_time) + ',' + ('%0.3f' % millis)[2:] + '>'
                return self._initial_strtime

            @property
            def current_thread(self):
                if self._current_thread is None:
                    self._current_thread = threading.currentThread()
                return self._current_thread

            @property
            def call_id(self):
                if self._call_id is None:
                    call_id_chars = ''.join([ random.choice(_CALL_ID_ALPHABET) for _ in xrange(12) ])
                    self._call_id = _BASE_CALL_ID_STR + call_id_chars
                return self._call_id

        class HeaderLine(object):
            def __init__(self, entry, log_writer):
                self.entry      = entry
                self.log_writer = log_writer

            def log(self, args, kargs):
                # Build it always: the purpose is to alert
                # everytime that a method is incorrectly
                # called
                self._build_fake_args(args, kargs)
                self.log_writer(self)

            def _build_fake_args(self, args, kargs):
                # args doesn't include "self"
                if except_for is not None:
                    self.fake_args = list(args)
                    self.fake_kargs = kargs.copy()

                    if isinstance(except_for,basestring) or isinstance(except_for, int):
                        except_for_parameters = (except_for,)
                    else:
                        except_for_parameters = except_for

                    for parameter in except_for_parameters:
                        replaced = False
                        if isinstance(parameter, int):
                            if len(args) < parameter:
                                self.fake_args[parameter] = '<hidden>'
                                replaced = True
                        else:
                            if isinstance(parameter, basestring):
                                given_position  = -1
                                parameter_name = parameter
                            else:
                                parameter_name, given_position = parameter

                            if parameter_name in kargs:
                                self.fake_kargs[parameter_name] = '<hidden>'
                                replaced = True
                            else:
                                if parameter_name in parameter_names:
                                    position = parameter_names.index(parameter_name)
                                else:
                                    position = given_position

                                if position >= 0 and len(args) > position:
                                    self.fake_args[position] = '<hidden>'
                                    replaced = True

                        if not replaced:
                            print("Warning!!! Function %s didn't receive a parameter %s" % (f, repr(parameter)), file=sys.stderr)
                            self.fake_args  = ('<error: all hidden because the parameter %s was not found>' % repr(parameter),)
                            self.fake_kargs = {}
                else:
                    self.fake_args = args
                    self.fake_kargs = kargs


            def __str__(self):
                strtime = self.entry.initial_strtime

                repr_args = []

                for arg in self.fake_args:
                    try:
                        result_repr = repr(arg)
                    except:
                        try:
                            result_repr = unicode(arg)
                        except:
                            result_repr = "ERROR: COULD NOT SERIALIZE OBJECT OF TYPE %s" % repr(type(arg))
                    if len(result_repr) > max_size:
                        result_repr = result_repr[:max_size-3] + '...'
                    repr_args.append(result_repr)

                repr_kwargs = {}
                for karg in self.fake_kargs:
                    value = self.fake_kargs[karg]
                    result_repr = repr(value)
                    if len(result_repr) > max_size:
                        result_repr = result_repr[:max_size-3] + '...'
                    repr_kwargs[karg] = result_repr

                if ctxt_retriever is not None:
                    ctxt = 'with ctxt %s and' % ctxt_retriever()
                else:
                    ctxt = 'with'

                return '++++{call_id}++++ {thread_id} Calling {func_name} {ctxt} parameters {args} and kargs: {kargs} at {time}'.format(
                            call_id   = self.entry.call_id, thread_id = self.entry.current_thread,
                            func_name = func_name,          args      = repr_args, ctxt = ctxt,
                            kargs     = repr_kwargs,        time      =  strtime )

        class FooterExcLine(object):
            def __init__(self, entry, log_writer):
                self.entry       = entry
                self.log_writer  = log_writer

            def log(self):
                self.log_writer(self)

            def __str__(self):
                call_time        = time.time()
                exc_type, exc, _ = sys.exc_info()

                local_time = time.localtime(call_time)
                millis     = call_time - math.floor(call_time)
                strtime    = '<' + time.strftime("%Y-%m-%d %H:%M:%S", local_time) + ',' + ('%0.3f' % millis)[2:] + '>'

                if ctxt_retriever is not None:
                    ctxt = 'with ctxt %s ' % ctxt_retriever()
                else:
                    ctxt = ''

                return '----{call_id}---- {func_name} started at {time} {ctxt} finished at {finish_time} finished with an exception: {exception_type}, {exception_args}'.format(
                        call_id = self.entry.call_id, func_name = func_name, time = self.entry.initial_strtime, 
                        exception_type= exc_type, exception_args = exc, finish_time = strtime, ctxt = ctxt)

        class FooterReturnLine(object):
            def __init__(self, entry, log_writer):
                self.entry       = entry
                self.log_writer = log_writer

            def log(self, result):
                self.result = result
                self.log_writer(self)

            def __str__(self):
                call_time        = time.time()

                local_time = time.localtime(call_time)
                millis     = call_time - math.floor(call_time)
                strtime    = '<' + time.strftime("%Y-%m-%d %H:%M:%S", local_time) + ',' + ('%0.3f' % millis)[2:] + '>'
                
                try:
                    result_repr = repr(self.result)
                except:
                    result_repr = "WARNING. COULD NOT REPRESENT RESULT DATA"
                if len(result_repr) > max_size:
                    result_repr = result_repr[:max_size-3] + '...'

                if ctxt_retriever is not None:
                    ctxt = 'with ctxt %s ' % ctxt_retriever()
                else:
                    ctxt = ''

                return '----%(call_id)s---- %(func_name)s %(ctxt)s started at %(time)s finished at %(finish_time)s finished with value <%(result)s>' % {
                            'call_id'       : self.entry.call_id,
                            'ctxt'          : ctxt,
                            'func_name'     : func_name,
                            'time'          : self.entry.initial_strtime,
                            'result'        : result_repr,
                            'finish_time'   : strtime
                        }

        if is_class_method:
            @wraps(f)
            def wrapped_class_method(self,*args, **kargs):
                logger_name = _get_full_class_name(self.__class__, f)
                logger = _get_logger(logger_name)
                if not logger.isEnabledFor(logging_level):
                    return f(self, *args, **kargs)

                log_writer = getattr(logger, levelname)

                entry  = LogEntry()
                header = HeaderLine(entry, log_writer)
                header.log(args, kargs)
                try:
                    result = f(self,*args,**kargs)
                except:
                    footer_exc = FooterExcLine(entry, log_writer)
                    footer_exc.log()
                    raise
                else:
                    footer_return = FooterReturnLine(entry, log_writer)
                    footer_return.log(result)

                return result
            wrapped = wrapped_class_method
        else: # For functions
            @wraps(f)
            def wrapped_function(*args, **kargs):
                logger_name = f.__module__
                logger = _get_logger(logger_name)
                if not logger.isEnabledFor(logging_level):
                    return f(*args, **kargs)

                log_writer = getattr(logger, levelname)

                entry  = LogEntry()
                header = HeaderLine(entry, log_writer)
                header.log(args, kargs)
                try:
                    result = f(*args,**kargs)
                except:
                    footer_exc = FooterExcLine(entry, log_writer)
                    footer_exc.log()
                    raise
                else:
                    footer_return = FooterReturnLine(entry, log_writer)
                    footer_return.log(result)

                return result
            wrapped = wrapped_function
        return wrapped
    return real_logger

