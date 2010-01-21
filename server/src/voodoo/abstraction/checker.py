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

##############################################################################################
#                                                                                            #
#             Copyright:     (c) 2006 Pablo Orduña <pablo@ordunya.com>                       #
#             LICENSE:       MIT License ( http://pablo.ordunya.com/license-mit )            #
#                                                                                            #
##############################################################################################
#                                                                                            #
#                       See checker_examples.py for examples                                 #
#                                                                                            #
##############################################################################################

def __type_handler(errors):
    message = 'TypeError checking parameters! '
    for i in errors:
        message += "\nThe value of parameter number '%i' is '%s', and was suppossed to be a '%s'" % (i,str(errors[i][0]),str(errors[i][1]))
    raise TypeError(message)

def check_types(parameters, data_types, handler = __type_handler):
    """
        check_types will raise an exception if a parameter of "parameters" 
        is not an instance of the corresponding data type in "data_types", and will
        call "handler" passing a dictionary with the errors.
        
        The dictionary format will be:
        errors = {parameter_number : (parameter_value,parameter_type)}
        
        The default behaviour is raising a TypeError informing which parameters
        are wrong.
        
        Another TypeError might be raised if a value in data_types is not a type or
        class.
        
        Obviously, if we don't want to check everyparameter, we don't have to. We can 
        just provide the parameters we want to check
        
        See checker_examples.py for examples
    """
    if len(parameters) != len(data_types):
        raise ValueError('Different number of parameters (%i) and data types (%i)' % (len(parameters),len(data_types)))
    
    errors = {}
    for i in range(len(parameters)):
        if not isinstance(parameters[i],data_types[i]):
            errors[i] = (parameters[i],data_types[i])
    if len(errors) > 0:
        handler(errors)

def __none_handler(errors):
    message = 'Value checking parameters! '
    for i in errors:
        message += "\nThe value of parameter number '%i' is None, and it shouldn't" % i
    raise ValueError(message)

def check_none(parameters, none_parameters = True, handler = __none_handler):
    """
        check_none will call "handler" if a parameter of "parameters"
        is None and none_parameters is True (by default it is), or if a 
        parameter in parameters is None and its corresponding bool value in
        the "none_parameters" list is True. Handler will receive a list with
        the following format:
        
        errors = [ ( parameter_number, parameter_value) ]
        
        The default behaviour is raising a ValueError informing which parameters
        are wrong.
        
        Obviously, if we don't want to check everyparameter, we don't have to. We can 
        just provide the parameters we want to check
        
        See checker_examples.py for examples
    """
    if none_parameters == True:
        errors = []
        for i in range(len(parameters)):
            if parameters[i] is None:
                errors.append(i)
        if len(errors) > 0:
            handler(errors)
    elif isinstance(none_parameters,list) or isinstance(none_parameters,tuple):
        if len(parameters) != len(none_parameters):
            raise ValueError('Different number of parameters (%i) and nullable values (%i)' % (len(parameters),len(none_parameters)))
        errors = []
        for i in range(len(parameters)):
            if none_parameters[i] and parameters[i] is None:
                errors.append(i)
        if len(errors) > 0:
            handler(errors)

def __value_handler(errors):
    message = 'Value checking parameters! '
    for i in errors:
        message += "\nThe value of parameter number '%i' is '%s', which is not acceptable" % (i[0],str(i[1]))
    raise ValueError(message)

def check_values(parameters, parameter_checkers, handle_always = False, handler = __value_handler):
    """
        check_values will raise an exception if a parameter of "parameters" 
        is not valid (the handler returns something different to False or None),
        and will call "handler" passing a list with the errors.
        
        Handler will receive a list with the following format:
        
        errors = [ ( parameter_number, parameter_value) ]
        
        The default behaviour is raising a ValueError informing which parameters
        are wrong.
        
        Obviously, if we don't want to check everyparameter, we don't have to. We can 
        just provide the parameters we want to check
        
        See checker_examples.py for examples
    """
    if len(parameters) != len(parameter_checkers):
        raise ValueError('Different number of parameters (%i) and parameter checkers (%i)' % (len(parameters),len(parameter_checkers)))
    errors = []
    there_was_an_error = False
    for i in range(len(parameters)):
        errors.append((i,parameter_checkers[i](parameters[i])))
        if errors[-1][1]:
            there_was_an_error = True
    if handle_always or there_was_an_error:
        handler(errors)
