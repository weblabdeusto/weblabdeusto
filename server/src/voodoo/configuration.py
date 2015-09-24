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
import types
import threading
import os
import voodoo.log as log
from voodoo.lock import RWLock

import voodoo.exc as VoodooErrors

import weblab.configuration_doc as configuration_doc


class _ConfigurationModule(object):
    def __init__(self, module):
        if not isinstance(module,types.ModuleType):
            raise NotAModuleError(
                    "parameter %s expected to be a module" % module
                )
        self.holder = module
        self.name   = module.__name__

    def reload(self):
        self.holder = reload(self.holder)

class _ConfigurationPath(object):
    def __init__(self, path):
        class Holder(object):
            CURRENT_PATH = os.path.dirname(path)
            execfile(path, globals(), locals())
        self.holder = Holder
        self._path  = path
        self.name   = path

    def reload(self):
        try:
            class Holder(object):
                CURRENT_PATH = os.path.dirname(self._path)
                execfile(self._path, globals(), locals())
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

    def __enter__(self):
        pass

    def __exit__(self, *args, **kwargs):
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

        self.client = {}
        self.server = {}
        self._modules = []
        if CFG_LOCKING:
            self._modules_lock = threading.RLock()
        else:
            self._modules_lock = NullLock()

    @staticmethod
    def create(directory, configuration_files, configuration_values):
        config = ConfigurationManager()
        config.append_paths([ os.path.abspath(os.path.join(directory, configuration_file)) for configuration_file in configuration_files ])
        for key, value in dict(configuration_values).iteritems():
            config.append_value(key, value)
        return config

    def _set_value(self, key, value):
        self._values_writelock.acquire()
        try:
            if key in self._values:
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

    def append_value(self, name, value):
        self._set_value(name, value)
        return self

    def append_module(self, module):
        self._modules_lock.acquire()
        try:
            configuration_module = _ConfigurationModule(module)
            self._modules.append(configuration_module)
            self._append_holder_values(configuration_module.holder)
        finally:
            self._modules_lock.release()
        return self

    def append_path(self, path):
        self._modules_lock.acquire()
        try:
            configuration_path = _ConfigurationPath(path)
            self._modules.append(configuration_path)
            self._append_holder_values(configuration_path.holder)
        finally:
            self._modules_lock.release()
        return self

    def append_modules(self, modules):
        for i in modules:
            self.append_module(i)
        return self

    def append_paths(self, paths):
        for i in paths:
            self.append_path(i)
        return self

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
        return self

    def get_value(self, key, default_value = _not_a_default_value):
        self._values_readlock.acquire()
        try:
            if key in self._values:
                return self._values[key]
            elif default_value != _not_a_default_value:
                return default_value
        finally:
            self._values_readlock.release()
        raise KeyNotFoundError(
                "Key: %s not found" % key,
                key
            )

    def get_doc_value(self, key):
        try:
            arg = configuration_doc.variables[key]
        except KeyError:
            raise KeyDocNotFound("Could not find documented variable %s" % key)

        if arg.default == configuration_doc.NO_DEFAULT:
            default_value = _not_a_default_value
        else:
            default_value = arg.default
            
        value = self.get_value(key, default_value)
        if arg.type != configuration_doc.ANY_TYPE:
            if isinstance(arg.type, basestring):
                expected_type = eval(arg.type)
            else:
                expected_type = arg.type

            if not isinstance(value, (expected_type, type(None))):
                if expected_type == int and isinstance(value, long):
                    pass
                else:
                    raise InvalidTypeError("Configuration value '%s' expected of type '%r' but '%r' found" % (key, arg.type, value))

        return value

    def __getitem__(self, key):
        return self.get_doc_value(key)
    
    def get(self, key, default = None):
        return self.get_value(key, default)

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
            except KeyNotFoundError:
                missing_configurations.append(key)
        if len(missing_configurations) > 0:
            raise KeysNotFoundError("Missing configuration parameters: %s " % missing_configurations)

        # Keys with a provided default value
        for key in kargs:
            values[key] = self.get_value(key, kargs[key])

        return Values(values)

class ConfigurationError(VoodooErrors.VoodooError):
    def __init__(self,*args,**kargs):
        VoodooErrors.VoodooError.__init__(self,*args,**kargs)

class KeyNotFoundError(ConfigurationError):
    def __init__(self, msg, key, *args, **kargs):
        ConfigurationError.__init__(self, msg, key, *args, **kargs)
        self.msg = msg
        self.key = key

class InvalidTypeError(ConfigurationError):
    pass

class KeyDocNotFound(KeyNotFoundError):
    def __init__(self, msg, key, *args, **kargs):
        KeyNotFoundError.__init__(self, msg, key, *args, **kargs)

class KeysNotFoundError(ConfigurationError):
    def __init__(self, *args, **kargs):
        ConfigurationError.__init__(self, *args, **kargs)

class NotAModuleError(ConfigurationError):
    def __init__(self, *args, **kargs):
        ConfigurationError.__init__(self, *args, **kargs)
