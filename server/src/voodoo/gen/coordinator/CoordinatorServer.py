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
import voodoo.sessions.manager as SessionManager
import voodoo.sessions.SessionType    as SessionType

import voodoo.gen.exceptions.coordinator.CoordinatorServerExceptions as CoordinatorServerExceptions
import voodoo.exceptions.sessions.SessionExceptions as SessionExceptions

import voodoo.gen.coordinator.CoordinationInformation as CoordinationInformation
import voodoo.gen.coordinator.CoordAddress as CoordAddress

COORDINATOR_SERVER_SESSION_TYPE = "coordinator_server_session_type"
DEFAULT_COORDINATOR_SERVER_SESSION_TYPE = "Memory"

COORDINATOR_SERVER_SESSION_POOL_ID = "coordinator_server_session_pool_id"
DEFAULT_COORDINATOR_SERVER_SESSION_POOL_ID = "CoordinatorServer"

class CoordinatorServer(object):
    def __init__(self, cfg_manager, map = None, map_file = None, *args, **kwargs):
        """ 
        session_type: member of voodoo.sessions.SessionType 
        map: voodoo.gen.coordinator.CoordinationInformation.CoordinationMap
        map_file: file object

        The parameter session_type must be provided; if "map" parameter is provided, the CoordinatorServer 
        uses this map. If map_file is provided, a new CoordinatorMap is created, and loaded from the map_file. 
        If no one of these two parameters is provided, a new CoordinatorMap is created, waiting for the method
        "load" to be called. Finally, if both parameters are provided, an exception is raised.
        """
        super(CoordinatorServer, self).__init__(*args, **kwargs)
        session_type = cfg_manager.get_value(COORDINATOR_SERVER_SESSION_TYPE, DEFAULT_COORDINATOR_SERVER_SESSION_TYPE)
        session_pool_id = cfg_manager.get_value(COORDINATOR_SERVER_SESSION_POOL_ID, DEFAULT_COORDINATOR_SERVER_SESSION_POOL_ID)
        if session_type in SessionType.getSessionTypeValues():
            self._session_manager = SessionManager.SessionManager(
                    cfg_manager,
                    session_type,
                    session_pool_id
                )
        else:
            raise CoordinatorServerExceptions.NotASessionTypeException(
                    "Not a session_type: %s" % session_type
                )
        if map is not None and map_file is None:
            self._coordination_map_controller = CoordinationInformation.CoordinationMapController(map)
        elif map is None and map_file is not None:
            self._coordination_map_controller = CoordinationInformation.CoordinationMapController()
            self._coordination_map_controller.load(map_file)
        elif map is not None and map_file is not None:
            raise CoordinatorServerExceptions.BothMapAndMapFileProvidedException(
                "Can't provide both map_file and map to CoordinatorServer"
            )
        elif map is None and map_file is None:
            raise CoordinatorServerExceptions.NeitherMapNorFileProvidedException("Can't build the Coordination Map if neither map nor map_file fields are provided!")
        else:
            raise RuntimeError("This possibility should never happen -voodoo.gen.coordinator.CoordinatorServer.__init__-")
    
    def do_new_query(self, original_server_address, server_type, restrictions):
        """ 
        Returns a new session_id for coordination server. This session_id corresponds to an empty session which contains
        the server_type and the restrictions.
        """
        sess_id = self._session_manager.create_session()
        try:
            self._session_manager.modify_session(
                sess_id,
                dict(
                    server_type             = server_type,
                    restrictions            = restrictions,
                    original_server_address = original_server_address,
                    already_checked_servers = {
                        # CoordAddress : {
                        #     ProtocolA : [ address1, address2 ]
                        # }
                    }
                )
            )
        except SessionExceptions.SessionException as se:
            raise CoordinatorServerExceptions.CouldNotCreateSessionException(
                    "Couldn't create session: " + str(se),
                    se
                )
        #
        # already_checked_servers controls which servers has the server with this session_id already checked.
        # Whenever the method get_server is called, the session will be retrieved, and, for each server the 
        # CoordinationMap finds that fulfills the server type and the restrictions, it is checked if all its
        # networks have already been checked.
        # 
        return sess_id

    def do_logout(self, session_id):
        try:
            self._session_manager.delete_session(session_id)
        except SessionExceptions.SessionException:
            pass

    def do_get_server(self, session_id):
        try:
            session = self._session_manager.get_session_locking(session_id)
        except SessionExceptions.SessionInvalidSessionIdException as sisi:
            raise CoordinatorServerExceptions.SessionNotFoundException(*sisi.args)
        try:
            server_type                 = session['server_type']
            restrictions                = session['restrictions']
            str_original_server_address = session['original_server_address']

            original_server_address = CoordAddress.CoordAddress.translate_address(
                    str_original_server_address
                )
            for server, networks in self._coordination_map_controller.get_servers(
                    original_server_address,
                    server_type,
                    restrictions
                ):
                coord_address = server.address
                if coord_address.address in session['already_checked_servers']:
                    network = self._retrieve_network_and_modify_session(
                            coord_address,
                            networks,
                            session
                        )
                    if network == None:
                        continue # all networks checked, looking for another server
                    #Ok, this server is the server, and network is the network
                else:
                    if len(networks) == 0:
                        # a server with no network is not useful. It shouldn't happen, but still
                        continue 
                    #This server is the server
                    network = self._add_server_and_network_to_server(coord_address,networks,session)

                #At this point, the "server" (and "network" are chosen), we just need to save the cache and return them
                return network.address
            raise CoordinatorServerExceptions.NoServerFoundException(
                    "No server found for server_type: " + server_type.name + " and restrictions: " + str(restrictions) 
                )
        finally:
            self._session_manager.modify_session_unlocking(
                    session_id,
                    session
                )


    def do_get_all_servers(self, original_server_address, server_type, restrictions):
        str_original_server_address = original_server_address
        original_server_address = CoordAddress.CoordAddress.translate_address(
                str_original_server_address
            )
        servers = []
        for server, networks in self._coordination_map_controller.get_servers(
                original_server_address,
                server_type,
                restrictions
            ):
            servers.append((server,networks))
        return servers

    def do_get_networks(self, original_server_address, server_address):
        """ get_networks( original_server_address, server_address) -> [Network]
        Given two CoordAddresses, it returns the networks the server in the
        first address can use to communicate with server in the second address.
        """
        return self._coordination_map_controller.can_connect(original_server_address, server_address)

    def _add_server_and_network_to_server(self,coord_address,networks,session):
        session['already_checked_servers'][coord_address.address] = {}
        network = networks[0] # First network
        protocol_name = network.get_protocol().name
        session['already_checked_servers'][coord_address.address][protocol_name] = [network.address]
        return network

    def _retrieve_network_and_modify_session(self,coord_address,networks,session):
        already_checked_networks = session['already_checked_servers'][coord_address.address]
        for network in networks:
            protocol_name = network.get_protocol().name
            if protocol_name in already_checked_networks:
                # We have already worked with this network; checking address
                already_checked_addresses = already_checked_networks[protocol_name]
                if not network.address in already_checked_addresses:
                    # New address!
                    already_checked_addresses.append(network.address)
                    return network
            else:
                already_checked_networks[protocol_name] = [network.address]
                return network

