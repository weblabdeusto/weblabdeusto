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

import threading

import weblab.configuration_doc as configuration_doc

import datetime

import voodoo.counter as counter
import voodoo.resources_manager as ResourceManager

import weblab.comm.exc as FacadeErrors
import voodoo.configuration as ConfigurationErrors

BASE_LOCATION_PROPERTY                = 'base_location'
_resource_manager = ResourceManager.CancelAndJoinResourceManager("RemoteFacadeServer")

def strdate(days=0,hours=0,minutes=0,seconds=0):
    return (datetime.datetime.utcnow() + datetime.timedelta(days=days,hours=hours,minutes=minutes,seconds=seconds)).strftime("%a, %d %b %Y %H:%M:%S GMT")

class AbstractProtocolRemoteFacadeServer(threading.Thread):
    protocol_name = 'FILL_ME!' # For instance: JSON

    def __init__(self, server, configuration_manager, remote_facade_server):
        threading.Thread.__init__(self)
        self.setName(counter.next_name("RemoteFacadeServer_" + self.protocol_name))
        self.setDaemon(True)
        self._configuration_manager = configuration_manager
        self._stopped               = False
        self._rfm                   = getattr(remote_facade_server,'_create_%s_remote_facade_manager' % self.protocol_name)(
                            server,
                            configuration_manager
                        )
        self._rfs                   = remote_facade_server

    def run(self):
        try:
            while not self._rfs._get_stopped():
                self._server.handle_request()
            self._server = None
        finally:
            _resource_manager.remove_resource(self)

    def get_timeout(self):
        return self._configuration_manager.get_doc_value(configuration_doc.FACADE_TIMEOUT)

    def parse_configuration(self, *args, **kargs):
        try:
            return self._configuration_manager.get_values(*args, **kargs)
        except ConfigurationErrors.ConfigurationError as ce:
            raise FacadeErrors.MisconfiguredError("Missing params: " + ce.args[0])

class AbstractRemoteFacadeServer(object):
    SERVERS = ()

    def __init__(self, server, configuration_manager):
        self._configuration_manager = configuration_manager
        self._stopped               = False
        self._stop_lock             = threading.Lock()

        self._servers               = []

        for ServerClass in self.SERVERS:
            self._servers.append(
                    ServerClass(server, configuration_manager, self)
                )

    def start(self):
        for server in self._servers:
            server.initialize()

        # And, if all of them are correctly configured...
        for server in self._servers:
            server.start()
            _resource_manager.add_resource(server)

    def cancel(self):
        # Used by the _resource_manager
        self.stop()

    def _get_stopped(self):
        with self._stop_lock:
            return self._stopped

    def stop(self):
        with self._stop_lock:
            self._stopped = True

        for server in self._servers:
            server.join()

