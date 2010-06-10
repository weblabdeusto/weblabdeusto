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
import voodoo.log as log

import weblab.data.dto.Experiment as Experiment
import weblab.data.experiments.ExperimentId as ExperimentId

try:
    import ZSI
except ImportError:
    ZSI_AVAILABLE = False
else:
    ZSI_AVAILABLE = True

import SimpleXMLRPCServer
import datetime
import traceback

import weblab.facade.RemoteFacadeContext as RemoteFacadeContext
import weblab.facade.RemoteFacadeManagerCodes as RemoteFacadeManagerCodes

PROPAGATE_STACK_TRACES_TO_CLIENT                = 'propagate_stack_traces_to_client'
DEFAULT_PROPAGATE_STACK_TRACES_TO_CLIENT        = False

DEBUG_MODE                                      = 'debug_mode'
DEFAULT_DEBUG_MODE                              = False

UNEXPECTED_ERROR_MESSAGE_TEMPLATE               = "Unexpected error ocurred in WebLab-Deusto. Please contact the administrator at %s"
SERVER_ADMIN_EMAIL                              = 'server_admin'
DEFAULT_SERVER_ADMIN_EMAIL                      = '<server_admin not set>'


def check_exceptions(exceptions_to_check):
    for i, (exc, _, _) in enumerate(exceptions_to_check):
        for exc2, _, _ in exceptions_to_check[i + 1:]:
            if issubclass(exc2, exc):
                raise AssertionError("In Facade Exceptions the order is important. There can't be any exception that is a subclass of a previous exception. In this case %s is before %s" % (exc, exc2))

    def real_check_exceptions(func):
        def wrapped(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except Exception, e:
                for exc, code, propagate in exceptions_to_check:
                    if issubclass(e.__class__, exc):
                        if propagate or self._cfg_manager.get_value(DEBUG_MODE, DEFAULT_DEBUG_MODE):
                            log.log(
                                    self.__class__,
                                    log.LogLevel.Info,
                                    "%s raised on %s: %s: %s" % ( exc.__name__, func.__name__, e, e.args)
                            )
                            log.log_exc(self.__class__, log.LogLevel.Debug)
                            return self._raise_exception(code, e.args[0])
                        else:
                            # WebLabInternalServerError
                            log.log(
                                    self.__class__,
                                    log.LogLevel.Warning,
                                    "Unexpected %s raised on %s: %s: %s" % ( exc.__name__, func.__name__, e, e.args)
                            )
                            log.log_exc(self.__class__, log.LogLevel.Info)
                            return self._raise_exception(RemoteFacadeManagerCodes.WEBLAB_GENERAL_EXCEPTION_CODE, UNEXPECTED_ERROR_MESSAGE_TEMPLATE % self._cfg_manager.get_value(SERVER_ADMIN_EMAIL, DEFAULT_SERVER_ADMIN_EMAIL) )

        wrapped.__name__ = func.__name__
        wrapped.__doc__  = func.__doc__
        return wrapped
    return real_check_exceptions

def check_nullable(func):
    def wrapped(self, *args, **kwargs):
        response = func(self, *args, **kwargs)
        return self._check_nullable_response(response)
    wrapped.__name__ = func.__name__
    wrapped.__doc__  = func.__doc__
    return wrapped

class AbstractRemoteFacadeManager(object):
    def __init__(self, cfg_manager, server):
        super(AbstractRemoteFacadeManager, self).__init__()
        self._server        = server
        self._cfg_manager   = cfg_manager

    def _get_client_address(self):
        return RemoteFacadeContext.get_context().get_ip_address()
   
def _propagate_stack_trace(cfg_manager, msg):
    formatted_exc = traceback.format_exc()
    propagate = cfg_manager.get_value(PROPAGATE_STACK_TRACES_TO_CLIENT, DEFAULT_PROPAGATE_STACK_TRACES_TO_CLIENT)
    if propagate:
        msg = str(msg) + "; Traceback: " + formatted_exc
    return msg

class AbstractZSI(object):
    def _raise_exception(self, code, msg):
        if ZSI_AVAILABLE:
            msg = _propagate_stack_trace(self._cfg_manager, msg)
            raise ZSI.Fault( 'ZSI:' + code, msg )
        else:
            msg = "Optional library 'ZSI' is not available, so SOAP clients will not be supported. However, AbstractZSI is being used, so problems will arise"
            log.log( self, log.LogLevel.Error, msg )
            print >> sys.stderr, msg

class JSONException(Exception):
    pass

class AbstractJSON(object):
    def _raise_exception(self, code, msg):
        msg = _propagate_stack_trace(self._cfg_manager, msg)
        raise JSONException({ 'is_exception' : True, 'code' : 'JSON:' + code, 'message' : msg })

class AbstractXMLRPC(object):
    def _raise_exception(self, code, msg):
        msg = _propagate_stack_trace(self._cfg_manager, msg)
        raise SimpleXMLRPCServer.Fault('XMLRPC:' + code, msg)

    def _parse_experiment_id(self, exp_id):
        return ExperimentId.ExperimentId(
                exp_id['exp_name'],
                exp_id['cat_name']
            )
       
    def _fix_dates_in_experiments(self, experiments_allowed):
        for experiment_allowed in experiments_allowed:
            experiment = experiment_allowed.experiment
            experiment_allowed.experiment = Experiment.Experiment(experiment.name, experiment.category,
                                datetime.datetime( experiment.start_date.year, experiment.start_date.month, experiment.start_date.day ),
                                datetime.datetime( experiment.end_date.year, experiment.end_date.month, experiment.end_date.day )
                            )

    def _check_nullable_response(self, response):
        # In XML-RPC, None doesn't exist
        return response or ''

