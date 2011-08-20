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
import sys
import time
import traceback
import StringIO
import math
import random
import logging
import threading
import new
from voodoo.cache import fast_cache

def log(instance_or_module_or_class, level, message):
    logging_log_level = getattr(logging,level.upper())
    if isinstance(instance_or_module_or_class,str):
        logger_name = instance_or_module_or_class
    elif isinstance(instance_or_module_or_class, new.classobj) or isinstance(instance_or_module_or_class, type):
        logger_name = instance_or_module_or_class.__module__ + '.' + instance_or_module_or_class.__name__
    else:
        logger_name = instance_or_module_or_class.__class__.__module__ + '.' + instance_or_module_or_class.__class__.__name__ 
    logger = logging.getLogger(logger_name)
    logger.log(logging_log_level,message)

def log_exc(instance_or_module_or_class, level):
    f = StringIO.StringIO()
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
        if cur_class.__dict__.has_key(func_name):
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

def logged(level='debug', except_for=None):
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
    levelname = level.lower()
    if not hasattr(logging, levelname):
        raise RuntimeError("level %s does not exist")

    def real_logger(f):
        # parameter_names is a list. Being "f" defined like:
        # def f(name1,name2,name3,*args,**kargs):
        # parameter_names will be ['name1','name2','name3']
        parameter_names = list(f.func_code.co_varnames[:f.func_code.co_argcount])
        func_name       = f.__name__

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
            def __init__(self, entry, logger_name):
                self.entry       = entry
                self.logger_name = logger_name

            def log(self, args, kargs):
                logger     = _get_logger(self.logger_name)
                log_writer = getattr(logger, levelname)
                # Build it always: the purpose is to alert
                # everytime that a method is incorrectly
                # called
                self._build_fake_args(args, kargs)
                log_writer(self)

            def _build_fake_args(self, args, kargs):
                # args doesn't include "self"
                if except_for != None:
                    self.fake_args = list(args)
                    self.fake_kargs = kargs.copy()

                    if isinstance(except_for,basestring) or isinstance(except_for, int):
                        except_for_parameters = (except_for,) 
                    else:
                        except_for_parameters = except_for

                    for parameter in except_for_parameters:
                        replaced = False
                        if isinstance(parameter, int):
                            if len(args) <= parameter - 1:
                                self.fake_args[parameter - 1] = '<hidden>'
                                replaced = True
                        else:
                            if isinstance(parameter, basestring):
                                given_position  = -1
                                parameter_name = parameter
                            else:
                                parameter_name, given_position = parameter
                            
                            if kargs.has_key(parameter_name):
                                self.fake_kargs[parameter_name] = '<hidden>'
                                replaced = True
                            else:
                                if parameter_name in parameter_names:
                                    position = parameter_names.index(parameter_name)
                                else:
                                    position = given_position

                                if position >= 0 and len(args) > position - 1:
                                    self.fake_args[position - 1] = '<hidden>'
                                    replaced = True

                        if not replaced:
                            print >> sys.stderr, "Warning!!! Function %s didn't receive a parameter %s" % (f, parameter)
                            self.fake_args  = ('<error: all hidden because the parameter %s was not found>' % parameter,)
                            self.fake_kargs = {}
                else:
                    self.fake_args = args
                    self.fake_kargs = kargs


            def __str__(self): 
                strtime = self.entry.initial_strtime

                return '++++%(call_id)s++++ %(thread_id)s Calling %(func_name)s with parameters %(args)s and kargs: %(kargs)s at %(time)s' % {
                            'call_id'   : self.entry.call_id,
                            'thread_id' : self.entry.current_thread,
                            'func_name' : func_name,
                            'args'      : self.fake_args,
                            'kargs'     : self.fake_kargs,
                            'time'      : strtime
                        }

        class FooterExcLine(object):
            def __init__(self, entry, logger_name):
                self.entry       = entry
                self.logger_name = logger_name

            def log(self):
                logger     = _get_logger(self.logger_name)
                log_writer = getattr(logger, levelname)
                log_writer(self)

            def __str__(self):
                call_time        = time.time()
                exc_type, exc, _ = sys.exc_info()

                local_time = time.localtime(call_time)
                millis     = call_time - math.floor(call_time)
                strtime    = '<' + time.strftime("%Y-%m-%d %H:%M:%S", local_time) + ',' + ('%0.3f' % millis)[2:] + '>'

                return '----%(call_id)s---- %(func_name)s started at %(time)s finished at %(finish_time)s finished with an exception: %(exception_type)s, %(exception_args)s' % {
                            'call_id'       : self.entry.call_id,
                            'func_name'     : func_name,
                            'time'          : self.entry.initial_strtime,
                            'exception_type': exc_type,
                            'exception_args': exc,
                            'finish_time'   : strtime
                        }

        class FooterReturnLine(object):
            def __init__(self, entry, logger_name):
                self.entry       = entry
                self.logger_name = logger_name

            def log(self, result):
                logger     = _get_logger(self.logger_name)
                log_writer = getattr(logger, levelname)
                self.result = result
                log_writer(self)

            def __str__(self):
                call_time        = time.time()

                local_time = time.localtime(call_time)
                millis     = call_time - math.floor(call_time)
                strtime    = '<' + time.strftime("%Y-%m-%d %H:%M:%S", local_time) + ',' + ('%0.3f' % millis)[2:] + '>'

                return '----%(call_id)s---- %(func_name)s started at %(time)s finished at %(finish_time)s finished with value <%(result)s>' % {
                            'call_id'       : self.entry.call_id,
                            'func_name'     : func_name,
                            'time'          : self.entry.initial_strtime,
                            'result'        : self.result,
                            'finish_time'   : strtime
                        }

        def wrapped(self,*args, **kargs):
            logger_name = _get_full_class_name(self.__class__, f)

            entry  = LogEntry()
            header = HeaderLine(entry, logger_name)
            header.log(args, kargs)
            try:
                result = f(self,*args,**kargs)
            except:
                footer_exc = FooterExcLine(entry, logger_name)
                footer_exc.log()
                raise
            else:
                footer_return = FooterReturnLine(entry, logger_name)
                footer_return.log(result)

            return result

        wrapped.__doc__ = f.__doc__
        wrapped.__name__ = f.__name__
        return wrapped
    return real_logger

