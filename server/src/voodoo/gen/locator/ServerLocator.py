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

import sys
import threading
import random
import time

import voodoo.log as log

import voodoo.gen.registry.server_registry as ServerRegistry

import voodoo.gen.exceptions.registry.RegistryErrors as RegistryErrors
import voodoo.gen.exceptions.locator.LocatorErrors as LocatorErrors
import voodoo.gen.exceptions.coordinator.CoordinatorServerErrors as CoordinatorServerErrors
import voodoo.gen.exceptions.protocols.ProtocolErrors as ProtocolErrors

ALL = "all"
MAX_CACHE_TIME = 5 # seconds

class ServerLocator(object):
    # TODO: cache object should be refactored out of this class but first all the "not tested / not unittested must be removed"
    def __init__(self, coordinator_server_address, server_type_handler):
        object.__init__(self)

        self._registry = ServerRegistry.get_instance()
        self._server_type_handler = server_type_handler

        # Cache structure:
        # self._cache = {
        #      ServerType.Login : {
        #         restrictions : server
        #   }
        # }
        self._cache = {}
        self._cache_lock = threading.RLock()

        self._coordinator = self._retrieve_coordinator(coordinator_server_address,server_type_handler)

    def _time(self):
        return time.time()

    def _retrieve_coordinator(self,coordinator_server_address,server_type_handler):
        server_type = server_type_handler.module.Coordinator
        methods = self._server_type_handler.retrieve_methods(
                server_type
            )

        return coordinator_server_address.create_client(methods)

    def retrieve_methods(self, server_type):
        return self._server_type_handler.retrieve_methods(server_type)

    def inform_server_not_working(self,server_not_working,server_type,restrictions_of_server):
        self._cache_lock.acquire()
        try:
            servers = self._cache.get(server_type)
            if servers == None:
                #TODO: not tested
                return
            client, creation_time = servers.get(restrictions_of_server)
            if client == None:
                #TODO: not tested
                return
            if client == server_not_working:
                servers.pop(restrictions_of_server)
        finally:
            self._cache_lock.release()

    def get_server(self,original_server_address, server_type,restrictions):
        if not self._server_type_handler.isMember(server_type):
            raise LocatorErrors.NotAServerTypeError('%s not a member of %s' %
                    (
                        server_type,
                        self._server_type_handler.module
                    )
                )

        server = self._get_server_from_cache(server_type,restrictions)
        if server is not None:
            return server # :-)

        session_id = self._retrieve_session_id_from_coordinator(
                    original_server_address,
                    server_type,
                    restrictions
                )

        try:

            there_are_more_servers = True
            while there_are_more_servers:
                try:
                    address = self._get_server_from_coordinator(session_id)
                except CoordinatorServerErrors.NoServerFoundError:
                    there_are_more_servers = False
                    continue
                server = self._get_server_from_registry(address)
                if server is not None:
                    # The server was in the registry but not in the cache;

                    # First check if the server is up and running
                    if not self._test_server(server,address):
                        # There was some error
                        continue
                    # Server up and running :-)
                    # Now add it to the cache and return it
                    try:
                        self._save_server_in_cache(server, server_type, restrictions)
                    except LocatorErrors.ServerFoundInCacheError as server_found_in_cache:
                        # While we were calling the coordinator, some
                        # other thread retrieved the server. Use the
                        # server that was already in the cache
                        return server_found_in_cache.get_server()
                    else:
                        return server

                # Server was not in the ServerRegistry neither in the cache
                methods = self._server_type_handler.retrieve_methods(
                        server_type
                    )
                try:
                    server = address.create_client(methods)
                except ProtocolErrors.ClientProtocolError as ccce:
                    # TODO: not tested
                    # There was some error creating the client
                    log.log(
                        ServerLocator,
                        log.level.Warning,
                        "Generating client for server with %s raised exception %s. Trying another server..." % (
                            address.address,
                            ccce
                        )
                    )
                    log.log_exc(
                        ServerLocator,
                        log.level.Info
                    )
                    continue

                # Check if the server is up and running
                if not self._test_server(server,address):
                    # There was some error
                    continue
                # Server up and running :-)

                try:
                    self._save_server_in_registry_and_cache(
                            server,
                            server_type,
                            restrictions,
                            address
                        )
                except LocatorErrors.ServerFoundInCacheError as e:
                    return e.get_server()
                else:
                    return server
            else:
                raise LocatorErrors.NoServerFoundError(
                    "No server found of type %s and restrictions %s" %
                    (server_type, restrictions)
                )

        finally:
            self._logout_from_coordinator( session_id )

    def get_all_servers(self,original_server_address, server_type,restrictions =()):
        if not self._server_type_handler.isMember(server_type):
            #TODO: not tested
            raise LocatorErrors.NotAServerTypeError('%s not a member of %s' %
                    (
                        server_type,
                        self._server_type_handler
                    )
                )

        all_servers = self._retrieve_all_servers_from_coordinator(original_server_address,server_type,restrictions)

        ret_value = []

        for server, networks in all_servers:
            server_instances = self._retrieve_server_instances_from_networks(
                    networks,
                    server_type
                )
            ret_value.append((server,server_instances))
        return ret_value

    def get_server_from_coord_address(self, original_server_address, server_coord_address, server_type, how_many = 1):
        networks = self._retrieve_networks_from_coordinator(
                    original_server_address,
                    server_coord_address
                )
        if len(networks) == 0:
            raise LocatorErrors.NoNetworkAvailableError(
                "Couldn't find a network for communicating original_server_address '%s' and server_coord_address '%s'" % (
                    original_server_address,
                    server_coord_address
                )
            )
        return self._retrieve_server_instances_from_networks(networks, server_type, how_many)

    def _retrieve_server_instances_from_networks(self, networks, server_type, how_many = ALL):
        server_instances = []
        for network in networks:
            address = network.address
            cur_server = self._get_server_from_registry(address)
            if cur_server is not None:
                # TODO: not unittested
                # First check if the server is up and running
                if not self._test_server(cur_server,address):
                    # There was some error
                    continue

                server_instances.append(cur_server)
                continue

            # Server was not in the ServerRegistry
            methods = self._server_type_handler.retrieve_methods(
                    server_type
                )
            try:
                cur_server = address.create_client(methods)
            except ProtocolErrors.ClientClassCreationError as ccce:
                # TODO: not unittested
                # There was some error creating the client
                log.log(
                    ServerLocator,
                    log.level.Warning,
                    "Generating client for server with %s raised exception %s. Trying another server..." % (
                        address.address,
                        ccce
                    )
                )
                log.log_exc(
                    ServerLocator,
                    log.level.Info
                )
                continue

            self._save_server_in_registry(address,cur_server)

            # Check if the server is up and running
            if not self._test_server(cur_server,address):
                # TODO: not unittested
                # There was some error
                continue
            # Server up and running :-)
            server_instances.append(cur_server)
            if how_many != ALL and len(server_instances) == how_many:
                break
        return server_instances

    def _test_server(self,server,address):
        """ _test_server(self,server,address) -> bool

        It returns True (if we could perform a call to "test_me"), or False (if we couldn't)
        """
        # Check if the server is up and running
        try:
            random_msg = str(random.random())
            result_msg = server.test_me(random_msg)
            if random_msg != result_msg:
                # This was not a valid server, try another
                log.log(
                    ServerLocator,
                    log.level.Warning,
                    "Test message received from server %s different from the message sent (%s vs %s). Trying another server" %(
                        address.address,
                        random_msg,
                        result_msg
                    )
                )
                return False
        except Exception as e:
            #There was a exception: this is not a valid server, try another
            log.log(
                ServerLocator,
                log.level.Warning,
                "Testing server %s raised exception %s. Trying another server" % (
                    address.address,
                    e
                )
            )
            log.log_exc(ServerLocator, log.level.Info)
            return False
        else:
            return True
            # Server up and running :-)

    def _retrieve_session_id_from_coordinator(self,original_server_address,server_type,restrictions):
        try:
            return self._coordinator.new_query(original_server_address,server_type,restrictions)
        except ProtocolErrors.ProtocolError as pe:
            log.log( ServerLocator, log.level.Error, "Problem while asking for new session id to the coordinator server. %s" % pe )
            log.log_exc( ServerLocator, log.level.Warning )

            raise LocatorErrors.ProblemCommunicatingWithCoordinatorError(
                    "Couldn't retrieve new session id from coordinator server: " + str(pe),
                    pe
                )
        except Exception as e:
            log.log( ServerLocator, log.level.Error, "Unexpected exception while asking for new session id to the coordinator server. %s" % e )
            log.log_exc( ServerLocator, log.level.Warning )

            raise LocatorErrors.ProblemCommunicatingWithCoordinatorError(
                    "Unexpected exception while asking new session id from coordinator server: " + str(e),
                    e
                )

    def _logout_from_coordinator(self, session_id):
        try:
            self._coordinator.logout(session_id)
        except Exception as e:
            log.log( ServerLocator, log.level.Warning, "Unexpected exception while logging out from Coordinator Server. %s " % e)
            log.log_exc( ServerLocator, log.level.Info )

    def _retrieve_all_servers_from_coordinator(self,original_server_address,server_type,restrictions):
        try:
            return self._coordinator.get_all_servers(original_server_address,server_type,restrictions)
        except ProtocolErrors.ProtocolError as pe:
            # TODO: not unittested
            log.log(
                    ServerLocator,
                    log.level.Error,
                    "Problem while asking for all servers to the coordinator server. %s" % pe
                )
            log.log_exc(
                    ServerLocator,
                    log.level.Warning
                )

            raise LocatorErrors.ProblemCommunicatingWithCoordinatorError(
                    "Couldn't retrieve all servers from coordinator server: " + str(pe),
                    pe
                )
        except Exception as e:
            # TODO: not unittested
            log.log(
                    ServerLocator,
                    log.level.Error,
                    "Unexpected exception while asking for all servers to the coordinator server. %s" % e
                )
            log.log_exc(
                    ServerLocator,
                    log.level.Warning
                )

            raise LocatorErrors.ProblemCommunicatingWithCoordinatorError(
                    "Unexpected exception while asking all servers from coordinator server: " + str(e),
                    e
                )

    def _retrieve_networks_from_coordinator(self,original_server_address,server_coord_address):
        try:
            return self._coordinator.get_networks(original_server_address,server_coord_address)
        except ProtocolErrors.ProtocolError as pe:
            # TODO: not unittested
            log.log(
                    ServerLocator,
                    log.level.Error,
                    "Problem while asking for networks to the coordinator server. %s" % pe
                )
            log.log_exc(
                    ServerLocator,
                    log.level.Warning
                )

            raise LocatorErrors.ProblemCommunicatingWithCoordinatorError(
                    "Couldn't retrieve networks from coordinator server: " + str(pe),
                    pe
                )
        except Exception as e:
            # TODO: not unittested
            log.log(
                    ServerLocator,
                    log.level.Error,
                    "Unexpected exception while asking for networks to the coordinator server. %s" % e
                )
            log.log_exc(
                    ServerLocator,
                    log.level.Warning
                )

            import traceback
            traceback.print_exc()

            raise LocatorErrors.ProblemCommunicatingWithCoordinatorError(
                    "Unexpected exception while asking for networks from coordinator server: " + str(e),
                    e
                )

    def _get_server_from_coordinator(self, session_id):
        try:
            return self._coordinator.get_server(session_id)
        except CoordinatorServerErrors.NoServerFoundError as nsfe:
            raise nsfe
        except ProtocolErrors.ProtocolError as pe:
            log.log(
                    ServerLocator,
                    log.level.Error,
                    "Problem while asking for other server to the coordinator server. %s" % pe
                )
            log.log_exc(
                    ServerLocator,
                    log.level.Warning
                )
            raise LocatorErrors.ProblemCommunicatingWithCoordinatorError(
                    "Couldn't ask for other server to coordinator server: " + str(pe),
                    pe
                )
        except Exception as e:
            log.log(
                    ServerLocator,
                    log.level.Error,
                    "Unexpected exception while asking for other server to the coordinator server. %s" % e
                )
            log.log_exc(
                    ServerLocator,
                    log.level.Warning
                )
            raise LocatorErrors.ProblemCommunicatingWithCoordinatorError(
                    "Unexpected exception while asking for other server to the coordinator server: " + str(e),
                    e
                )

    def _get_server_from_cache(self,server_type,restrictions):
        """
        Returns the server if it's found in the cache, or
        None if it's not found.
        """
        self._cache_lock.acquire()
        try:
            if not self._cache.has_key(server_type):
                return None
            server_type_cache = self._cache[server_type]
            if not server_type_cache.has_key(restrictions):
                return None
            server, creation_time = server_type_cache[restrictions]
            if self._time() - creation_time < MAX_CACHE_TIME:
                return server
            else:
                server_type_cache.pop(restrictions)
                return
        finally:
            self._cache_lock.release()

    def _save_server_in_registry(self, address, server):
        self._cache_lock.acquire()
        try:
            try:
                self._registry.register_server(address.address,server)
            except RegistryErrors.RegistryError as e:
                # TODO: not unittested
                log.log( ServerLocator, log.level.Info,
                        "RegistryError found registring server %s with address %s in registry: %s" % (server,address.address,e))
                log.log_exc( ServerLocator, log.level.Debug )
                print >> sys.stderr, "RegistryError found registring server %s with address %s in registry: %s" % (server,address.address,e)
                import traceback
                traceback.print_stack()
                print >> sys.stderr, "Reregistering..."
                print >> sys.stderr, ""
                print >> sys.stderr, ""
            self._registry.reregister_server(address.address,server)
        finally:
            self._cache_lock.release()

    def _save_server_in_cache(self, server, server_type, restrictions):
        self._cache_lock.acquire()
        try:
            if not self._cache.has_key(server_type):
                self._cache[server_type] = {}
            server_type_cache = self._cache[server_type]

            if not server_type_cache.has_key(restrictions):
                server_type_cache[restrictions] = (server, self._time())
            else:
                raise LocatorErrors.ServerFoundInCacheError(
                    server_type_cache[restrictions][0],
                    "There is already a server for server type %s and restrictions %s" % (server_type,restrictions)
                )
        finally:
            self._cache_lock.release()

    def _save_server_in_registry_and_cache(self, server, server_type, restrictions, address):
        self._cache_lock.acquire()
        try:
            self._save_server_in_cache(server, server_type,restrictions)
            self._save_server_in_registry(address, server)
        finally:
            self._cache_lock.release()

    def _get_server_from_registry(self,address):
        try:
            return self._registry.get_server(address.address)
        except RegistryErrors.RegistryError:
            # It was not found in the registry
            return None

