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
import types
import threading
import voodoo.log as log
from voodoo.lock import RWLock

import voodoo.exc as VoodooExceptions


class _ConfigurationModule(object):
    def __init__(self, module):
        if not isinstance(module,types.ModuleType):
            raise NotAModuleException(
                    "parameter %s expected to be a module" % module
                )
        self.holder = module
        self.name   = module.__name__

    def reload(self):
        self.holder = reload(self.holder)

class _ConfigurationPath(object):
    def __init__(self, path):
        class Holder(object):
            execfile(path)
        self.holder = Holder
        self._path  = path
        self.name   = path

    def reload(self):
        try:
            class Holder(object):
                execfile(self._path)
        except Exception as e:
            log.log( 
                    _ConfigurationPath, 
                    log.level.Warning, 
                    "Couldn't reload path %s: %s. Skipping..." % (self.name, e)
            )
        self.holder = Holder

#
# If passing this value as a default value, the ConfigurationManager will think
# that in fact there is no default value provided
# 
_not_a_default_value = object()

#
# XXX
# At the moment, WebLab-Deusto does not support dynamic reloading, so
# locking makes no sense. As soon as it's supported, modify this.
# 
CFG_LOCKING = False

class NullLock(object):
    def acquire(self):
        pass
    def release(self):
        pass

class ConfigurationManager(object):
    def __init__(self):
        super(ConfigurationManager,self).__init__()
        self._values = {}
        if CFG_LOCKING:
            self._values_rwlock = RWLock()
            self._values_readlock  = self._values_rwlock.read_lock()
            self._values_writelock = self._values_rwlock.write_lock()
        else:
            self._values_readlock  = NullLock()
            self._values_writelock = NullLock()

        self._modules = []
        if CFG_LOCKING:
            self._modules_lock = threading.RLock()
        else:
            self._modules_lock = NullLock()

    def _set_value(self, key, value):
        self._values_writelock.acquire()
        try:
            if self._values.has_key(key):
                log.log( 
                        ConfigurationManager, 
                        log.level.Info, 
                        "Substituting existing configuration key (%s), from value %s to %s" % (key, self._values[key], value) 
                )
            self._values[key] = value
        finally:
            self._values_writelock.release()
    
    def _append_holder_values(self, holder):
        for i in dir(holder):
            if not i.startswith('_'):
                self._set_value(
                    i,
                    getattr(holder,i)
                )

    def append_module(self, module):
        self._modules_lock.acquire()
        try:
            configuration_module = _ConfigurationModule(module)
            self._modules.append(configuration_module)
            self._append_holder_values(configuration_module.holder)
        finally:
            self._modules_lock.release()

    def append_path(self, path):
        self._modules_lock.acquire()
        try:
            configuration_path = _ConfigurationPath(path)
            self._modules.append(configuration_path)
            self._append_holder_values(configuration_path.holder)
        finally:
            self._modules_lock.release()

    def append_modules(self, modules):
        for i in modules:
            self.append_module(i)

    def append_paths(self, paths):
        for i in paths:
            self.append_path(i)

    def reload(self):
        self._modules_lock.acquire()
        self._values_writelock.acquire()
        try:
            self._values.clear()
            for i in range(len(self._modules)):
                name = self._modules[i].name
                try:
                    self._modules[i].reload()
                    self._append_holder_values(self._modules[i].holder)
                except ImportError:
                    log.log( 
                            ConfigurationManager, 
                            log.level.Warning, 
                            "Couldn't reload module %s. Skipping..." % name 
                    )
        finally:
            self._values_writelock.release()
            self._modules_lock.release()

    def get_value(self, key, default_value = _not_a_default_value):
        self._values_readlock.acquire()
        try:
            if self._values.has_key(key):
                return self._values[key]
            elif default_value != _not_a_default_value:
                return default_value
        finally:
            self._values_readlock.release()
        raise KeyNotFoundException(
                "Key: %s not found" % key,
                key
            )

    def get_values(self, *args, **kargs):
        """
        The default values can be provided in two ways:
           -> get_values("key1", "key2", key3 = "defvalue3")         # The prettiest one :-)
           -> get_values("key1", "key2", ** { "key3": "defvalue3" }) # Useful when "key3" is unknown in the source code 
        """
        class Values(object):
            def __init__(self, values):
                self.__dict__.update(values)

        missing_configurations = []
        values = {}

        # Keys without a provided default value
        for key in args:
            try:
                values[key] = self.get_value(key)
            except KeyNotFoundException:
                missing_configurations.append(key)
        if len(missing_configurations) > 0:
            raise KeysNotFoundException("Missing configuration parameters: %s " % missing_configurations)

        # Keys with a provided default value
        for key in kargs:
            values[key] = self.get_value(key, kargs[key])

        return Values(values)

class ConfigurationException(VoodooExceptions.VoodooException):
    def __init__(self,*args,**kargs):
        VoodooExceptions.VoodooException.__init__(self,*args,**kargs)

class KeyNotFoundException(ConfigurationException):
    def __init__(self, msg, key, *args, **kargs):
        ConfigurationException.__init__(self, msg, key, *args, **kargs)
        self.msg = msg
        self.key = key

class KeysNotFoundException(ConfigurationException):
    def __init__(self, *args, **kargs):
        ConfigurationException.__init__(self, *args, **kargs)

class NotAModuleException(ConfigurationException):
    def __init__(self, *args, **kargs):
        ConfigurationException.__init__(self, *args, **kargs)
