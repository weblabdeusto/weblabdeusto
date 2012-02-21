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

import voodoo.log as log
import voodoo.gen.exceptions.protocols.ProtocolExceptions as ProtocolExceptions
import voodoo.gen.exceptions.locator.LocatorExceptions as LocatorExceptions
import voodoo.gen.locator.ServerLocator as ServerLocator

class EasyLocator(object):

    def __init__(self, server_coordadd, server_locator):
        super(EasyLocator, self).__init__()
        self._server_coordaddr = server_coordadd
        self._server_locator          = server_locator

    def get_server_coordaddr(self):
        return self._server_coordaddr

    def get_server(self, server_type, restrictions = ()):
        return self._server_locator.get_server(
                self._server_coordaddr.address,
                server_type,
                restrictions
            )

    def get_all_servers(self,original_server_address, server_type,restrictions =()):
        return self._server_locator.get_all_servers(original_server_address, server_type, restrictions)

    def check_server_at_coordaddr(self, coord_addr, server_type):
        if len(self._get_server_from_coordaddr(coord_addr, server_type)) == 0:
            raise Exception("Could not connect to experiment %s through any interface" % coord_addr)

    def _get_server_from_coordaddr(self, coord_addr, server_type, how_many=1):
        return self._server_locator.get_server_from_coord_address(
                self._server_coordaddr,
                coord_addr,
                server_type,
                how_many
            )

    def inform_server_not_working(self,server_not_working,server_type,restrictions_of_server):
        return self._server_locator.inform_server_not_working(
                server_not_working,
                server_type,
                restrictions_of_server
            )

    def get_easy_server(self, server_type, restrictions = ()):
        methods = self._server_locator.retrieve_methods(server_type)
        easy_locator = self

        class EasyServer(object):
            def __init__(self, server_type):
                self._easy_locator     = easy_locator
                self._server_type = server_type
            def __repr__(self):
                return "EasyServer of type %s" % self._server_type

        for method in methods:
            #
            # Call method. For each method in methods
            # the EasyServer will have this method with the
            # same name. If method is "reserve_session", calling
            #
            # easy_server.reserve_session(db_session_id)
            #
            # will actually call the reserve_method (trying all
            # the servers the locator can find)

            func = _generate_call(server_type, method)
            setattr(EasyServer,method,func)

        return EasyServer(server_type)

    def get_server_from_coordaddr(self, coord_addr, server_type, how_many = ServerLocator.ALL):
        methods = self._server_locator.retrieve_methods(server_type)
        easy_locator = self

        class EasyServerFromCoordAddr(object):
            def __init__(self, server_type, other_coord_addr, how_many):
                self._easy_locator  = easy_locator
                self._server_type   = server_type
                self._other_coord   = other_coord_addr
                self._how_many      = how_many
            def __repr__(self):
                return "EasyServerFromCoordAddr of type %s" % self._server_type

        for method in methods:
            func = _generate_call_from_coordaddr(server_type, method)
            setattr(EasyServerFromCoordAddr,method,func)

        return EasyServerFromCoordAddr(server_type, coord_addr, how_many)

def _generate_call(server_type, method):
    def _call(self, *args, **kwargs):
        wrong_servers = []
        while True:
            try:
                server = self._easy_locator.get_server(server_type)
            except LocatorExceptions.NoServerFoundException:
                log.log( EasyLocator, log.level.Error, "Can't get a %s server! Error in get_server " % server_type)
                raise LocatorExceptions.UnableToCompleteOperationException(
                        "Couldn't connect to %s" % server_type
                    )

            try:
                return getattr(server, method)(*args, **kwargs)
            except ProtocolExceptions.RemoteException as re:
                log.log(
                    EasyLocator,
                    log.level.Warning,
                    "%s failed in reserve_session" % server_type
                )
                if not server in wrong_servers:
                    wrong_servers.append(server)
                    self._easy_locator.inform_server_not_working(
                            server,
                            server_type,
                            ()
                        )
                else:
                    log.log( EasyLocator, log.level.Error, "Locator provides twice the same server that fails in reserve_session! Can't use %s" % server_type )
                    raise LocatorExceptions.UnableToCompleteOperationException(
                            "Error retrieving reserve_session answer",
                            re
                        )
    return _call

def _generate_call_from_coordaddr(server_type, method):
    def _call_from_coordaddr(self, *args, **kwargs):
        try:
            servers = self._easy_locator._get_server_from_coordaddr(self._other_coord, server_type, self._how_many)
        except LocatorExceptions.NoServerFoundException:
            log.log( EasyLocator, log.level.Error, "Can't get %s servers! Error in get_server_from_coordaddr " % server_type)
            raise LocatorExceptions.UnableToCompleteOperationException(
                    "Couldn't connect to %s" % server_type
                )

        tested = 0
        for server in servers:
            tested += 1
            try:
                return getattr(server, method)(*args, **kwargs)
            except ProtocolExceptions.RemoteException:
                log.log(
                    EasyLocator,
                    log.level.Warning,
                    "%s failed in reserve_session" % server_type
                )
                log.log_exc( EasyLocator, log.level.Warning )
                self._easy_locator.inform_server_not_working(
                        server,
                        server_type,
                        ()
                    )

        log.log( EasyLocator, log.level.Error, "Can't get a %s server! Error in get_server after testing %s servers " % (server_type, tested))
        raise LocatorExceptions.UnableToCompleteOperationException(
                "Couldn't connect to any %s" % server_type
            )
    return _call_from_coordaddr
