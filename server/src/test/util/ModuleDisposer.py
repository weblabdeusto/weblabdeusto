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

VERBOSE = False

def uses_module(module, verbose = None):
    """Decorator. Sample:

    @uses_module(UserProcessingServer)
    def test_foo(self):
        # Something related with the UserProcessingServer

    uses_module will use the '_resource_manager' variable in that module
    (which is an instance of voodoo.ResourceManager), will check how many
    resources are used before calling to the test and how many after 
    calling the test, and it will try to clean the new ones. The main
    drawback of this code is that it misses the resources created in the
    setUp method and those disposed in the tearDown method.
    """
    def wrapped_func(func):
        def real_func(self,*args, **kargs):
            if verbose == None:
                vvv = VERBOSE
            else:
                vvv = verbose

            if vvv:
                print "Test %s: retrieving current resources" % func.__name__
            resources = module._resource_manager.get_current_resources()
            if vvv:
                print "Test %s: retrieved resources: %s" % (func.__name__, resources)
                print "Test %s: running test..." % func.__name__
            try:
                _ = func(self,*args,**kargs)
            finally:
                if vvv:
                    print "Test %s: Test run..." % func.__name__
                    resources_after = module._resource_manager.get_current_resources()
                    print "Test %s: Resources after running test: %s" % (func.__name__,resources_after)
                module._resource_manager.remove_resources_from(resources)
                if vvv:
                    print "Test %s: resources cleaned" % func.__name__
                    new_resources = module._resource_manager.get_current_resources()
                    print "Test %s: remaining resources: %s" % (func.__name__,new_resources)

        real_func.__name__ = wrapped_func.__name__
        real_func.__doc___ = wrapped_func.__doc__
        return real_func
    return wrapped_func

class _ResourceMonitor(object):
    def __init__(self):
        self.before_last_setup = None

def case_uses_module(module):
    def wrapped_func(klass):
        if not hasattr(klass, '_module_disposer'):
            klass._module_disposer = {}
        klass._module_disposer[module.__name__] = _ResourceMonitor()

        realSetUp = klass.setUp
        def wrappedSetUp(self):
            klass._module_disposer[module.__name__].before_last_setup = module._resource_manager.get_current_resources()
            realSetUp(self)
        klass.setUp = wrappedSetUp

        realTearDown = klass.tearDown
        def wrappedTearDown(self):
            realTearDown(self)
            resources = klass._module_disposer[module.__name__].before_last_setup
            module._resource_manager.remove_resources_from(resources)
        klass.tearDown = wrappedTearDown

        return klass
    return wrapped_func

