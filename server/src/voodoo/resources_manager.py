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

import os
import sys
import threading
from voodoo.lock import locked
from abc import ABCMeta, abstractmethod
import voodoo.log as log

def is_testing():
    # if the runner is unittest or nose, then it is running
    if 'unittest' in sys.argv[0] or 'nose' in sys.argv[0]:
        return True
    # if there is no test module loaded, it's not testing
    if not 'test' in sys.modules:
        return False
    # if the test.* module is our test module...
    voodoo_file = sys.modules['voodoo'].__file__
    voodoo_path = voodoo_file[:voodoo_file.rfind(os.sep) - len('voodoo')]
    test_file = sys.modules['test'].__file__
    test_path = test_file[:test_file.rfind(os.sep) - len('test')]
    testing = test_path == voodoo_path
    return testing

class ResourceManager(object):

    __metaclass__ = ABCMeta

    def __init__(self):
        self._lock = threading.RLock()
        self._resources = []

    @abstractmethod
    def dispose_resource(self, resource):
        pass

    # If the resource manager is not going to be used, we don't want
    # to have @locked methods, since they have a performance impact in
    # Python
    if is_testing():
        @locked('_lock')
        def add_resource_testing(self, resource):
            self._resources.append(resource)

        @locked('_lock')
        def remove_resource_testing(self, resource):
            if resource in self._resources:
                self._resources.remove(resource)

        add_resource    = add_resource_testing
        remove_resource = remove_resource_testing
    else:
        def add_resource(self, resource):
            pass

        def remove_resource(self, resource):
            pass

    #
    # The rest of the methods will never be called in
    # production, so there is no need to reimplement
    # them in a not-locked version
    #

    @locked('_lock')
    def get_current_resources(self):
        return self._resources[:]

    @locked('_lock')
    def _get_different_resources(self, old_resources):
        different_resources = []
        for i in self._resources:
            if not i in old_resources:
                different_resources.append(i)
        return different_resources

    def remove_resources_from(self, old_resources):
        different_resources = self._get_different_resources(old_resources)
        for i in different_resources:
            self.dispose_resource(i)
            self.remove_resource(i)

class CancelAndJoinResourceManager(ResourceManager):
    def __init__(self, name, cancel = True, log_level = log.level.Info, log_exc_level = log.level.Debug, timeout = None):
        ResourceManager.__init__(self)
        self._name          = name
        self._cancel        = True
        self._timeout       = timeout
        self._log_level     = log_level
        self._log_exc_level = log_exc_level

    def dispose_resource(self, resource):
        try:
            if self._cancel:
                resource.cancel()
        except Exception as e:
            log.log( CancelAndJoinResourceManager, self._log_level,
                    "Exception joining resource at %s: %s" % (self._name, e)
                )
            log.log_exc( CancelAndJoinResourceManager, self._log_exc_level)

        try:
            if self._timeout is not None:
                resource.join(self._timeout)
            else:
                resource.join()
        except Exception as e:
            log.log( CancelAndJoinResourceManager, self._log_level,
                    "Exception joining resource at %s: %s" % (self._name, e)
                )
            log.log_exc( CancelAndJoinResourceManager, self._log_exc_level)

