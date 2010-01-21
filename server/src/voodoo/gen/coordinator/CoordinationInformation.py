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

# TODO: versions are not used
# There should be a diff system, instead of a simple _increase_version
# This way, each "version" would be something pretty more complex like
# a dictionary of changes, with the last changes of everyone. Each time
# someone makes a change, this change may depend on other changes.

import logging

import voodoo.lock as lock
from voodoo.lock import locked

import voodoo.gen.coordinator.CoordAddress as CoordAddress
import voodoo.gen.coordinator.CoordinationInformationMapper as CoordinationInformationMapper

import voodoo.gen.exceptions.coordinator.CoordinatorExceptions as CoordExceptions

#
# In this file, the following classes are defined
# *) CoordServer
# *) CoordInstance
# *) CoordMachine
# *) CoordinationMap
# *) CoordinationMapController
#
# Except for the last one, *nobody should ever instance* any of these classes.
# The CoordinationMapController will create and update all the structures, and
# it will provide the user of these classes an API to operate with them.
#
#       
###############################################################################
#                                                                             #
#                             CoordServer                                     #
#                                                                             #
###############################################################################

class CoordServer(object):
    def __init__(self, 
            server_type,
            server_name,
            parent_instance,
            accesses,
            restrictions = ()
        ):
        """ CoordServer(server_type,server_name[, parent_instance[,accesses]]) -> CoordServer

        * server_type is a member of an enumerator listing the types of server
        * server_name is the name of the server
        * parent_instance is a member of CoordInstance, and can be later 
        * accesses is a sequence of instances of Access
        * restrictions is a sequence of restrictions. For instance, a server for FPGAs, etc.
        
        modified with the "parent" property.
        """
        object.__init__(self)

        # Server information
        self._server_type   = server_type
        self._status        = False
        self._accesses_lock = lock.RWLock()
        self._accesses_read_lock  = self._accesses_lock.read_lock()
        self._accesses_write_lock = self._accesses_lock.write_lock()
        self._version       = 0
        self._accesses      = list(accesses)
        self._restrictions      = list(restrictions)
        
        # Addressing information
        self._name      = server_name
        self._parent        = parent_instance
        self._address   = CoordAddress.CoordAddress (
                    self._parent.parent.name,
                    self._parent.name,
                    self._name
                )

    def can_handle(self,restriction):
        for i in self._restrictions:
            if restriction == i:
                return True
        return False

    @locked('_accesses_read_lock')
    def copy(self):
        new_coord = CoordServer(
                self._server_type,
                self.name,
                self._parent,
                self._accesses,
                self._restrictions
            )
        new_coord._address = self._address.copy()
        new_coord._version = self._version
        new_coord._status  = self._status
        return new_coord

    @property
    @locked('_accesses_read_lock')
    def status(self):
        return self._status

    @property
    def parent(self):
        return self._parent

    @property
    def server_type(self):
        return self._server_type
    
    @property
    def address(self):
        return self._address

    @property
    def name(self):
        return self._name

    @property
    @locked('_accesses_read_lock')
    def version(self):
        return self._version

    def _increase_version(self):
        # Important: this method should be called
        # after a self._accesses_lock.acquire()
        self._version += 1

    @locked('_accesses_write_lock')
    def _set_status(self,new_status):
        self._status = new_status
        self._increase_version()
    
    @locked('_accesses_write_lock')
    def _append_accesses(self,accesses):
        for i in accesses:
            self._accesses.append(i)
        self._increase_version()
       
    @locked('_accesses_read_lock')
    def can_connect(self,other_server):
        """ can_connect(self,other_server) -> list

        This method returns a list of networks. This server
        can connect to the other_server through all these networks
        """
        networks = []
        for i in self.get_accesses():
            for j in other_server.get_accesses():
                for k in i.possible_connections(j):
                    networks.append(k)
        return networks
    
    def get_accesses(self):
        """ get_accesses(self) -> iterator

        This method returns all the accesses this server has, one by one, in an iterator.
        If, while processing each access, another access is added or one is removed, the 
        iterator will provide the new ones and will skip the old ones. 
        """
        walked_accesses = []
        while True:
            self._accesses_read_lock.acquire()
            accesses = [ i for i in self._accesses if not i in walked_accesses ]
            if len(accesses) >= 1:
                access = accesses[0]
                self._accesses_read_lock.release()
                walked_accesses.append(access)
                yield access
            else:
                #End :-)
                self._accesses_read_lock.release()
                return

###############################################################################
#                                                                             #
#                             CoordInstance                                   #
#                                                                             #
###############################################################################


class CoordInstance(object):
    def __init__(self,instance_name,parent_machine):
        object.__init__(self)

        # An instance is a set of CoordServers
        self._servers_lock  = lock.RWLock()
        self._servers_read_lock  = self._servers_lock.read_lock()
        self._servers_write_lock = self._servers_lock.write_lock()
        self._servers       = {}
        self._version       = 0

        # Addressing information
        self.name       = instance_name
        self._parent        = parent_machine
        self._address   = CoordAddress.CoordAddress (
                    self._parent.name,
                    self.name,
                    ''
                )

    def copy(self):
        new_coord_instance = CoordInstance(self.name,self._parent)
        self._servers_read_lock.acquire()
        try:
            for i in self._servers:
                new_server = self._servers[i].copy()
                new_server._parent = new_coord_instance
                new_coord_instance._servers[new_server.name] = new_server
            new_coord_instance._version = self._version
        finally:
            self._servers_read_lock.release()
        return new_coord_instance

    def _increase_version(self):
        # Important: this method should be called
        # after a self._accesses_lock.acquire()
        self._version += 1

    @property
    def parent(self):
        return self._parent

    @property
    def address(self):
        return self._address

    @property
    @locked('_servers_read_lock')
    def version(self):
        return self._version
    
    def get_servers(self):
        """ get_servers() -> iterator

        get_servers provides a thread-safe iterator which will return a new
        server in every iteration. If between iteration and iteration a server 
        is added or removed, the iterator will return the new servers and will
        avoid the removed ones.
        """
        walked_servers = []
        while True:
            
            self._servers_read_lock.acquire()
            
            keys = [ i for i in self._servers.keys() if not i in walked_servers ]
            if len(keys) >= 1:
                server = self._servers[keys[0]]
                self._servers_read_lock.release()
                walked_servers.append(keys[0])
                yield server
            else:
                #End :-)
                self._servers_read_lock.release()
                return

    @locked('_servers_write_lock')
    def _add_new_server(self,server_name,server_type,accesses,restrictions = ()):
        new_server = CoordServer(
                    server_type,
                    server_name,
                    self,
                    accesses,
                    restrictions
                )
        if self._servers.has_key(server_name):
            logger = logging.getLogger(self.__class__.__name__)
            logger.warn('Is this normal? Replacing %s by %s' % (
                    self._servers[server_name],
                    new_server
                )
            )
        self._servers[server_name] = new_server
        self._increase_version()
    
    @locked('_servers_write_lock')
    def _append_accesses(self,server_name,accesses):
        if not self._servers.has_key(server_name):
            raise CoordExceptions.CoordServerNotFound(
                        'Server %s not found' 
                        % server_name
                    )
        self._servers[server_name]._append_accesses(accesses)
        self._increase_version()
            
    @locked('_servers_write_lock')
    def _set_status(self,server_name,new_status):
        if not self._servers.has_key(server_name):
            raise CoordExceptions.CoordServerNotFound(
                        'Server %s not found' 
                        % server_name
                    )
        self._servers[server_name]._set_status(new_status)
        self._increase_version()

    @locked('_servers_read_lock')
    def __getitem__(self,name):
        if type(name) is str:
            key = name
        elif isinstance(name,CoordAddress.CoordAddress) and name.is_server():
            key = name.server_id
        else:
            raise CoordExceptions.CoordInvalidKey(
                "Invalid key: %s. Only strings and server CoordAddress are allowed" 
                % name
            )
        if self._servers.has_key(key):
            return self._servers[key]
        else:
            raise CoordExceptions.CoordServerNotFound(
                    'server %s not found in %s' %
                    (
                        name,
                        self.name
                    )
            )
            
    @locked('_servers_write_lock')
    def __setitem__(self,number,value):
        self._servers[number] = value
        self._increase_version()
            
###############################################################################
#                                                                             #
#                             CoordMachine                                    #
#                                                                             #
###############################################################################


class CoordMachine(object):
    def __init__(self,machine_id,parent_map):
        object.__init__(self)

        # A machine is a set of CoordInstances
        self._instances_lock      = lock.RWLock()
        self._instances_read_lock  = self._instances_lock.read_lock()
        self._instances_write_lock = self._instances_lock.write_lock()
        self._instances     = {}
        self._version       = 0
    
        # Addressing information
        self.name       = machine_id
        self.parent     = parent_map
        self.address        = CoordAddress.CoordAddress (
                        machine_id,
                        '',
                        ''
                    )

    @locked('_instances_read_lock')
    def copy(self):
        new_coord_machine = CoordMachine(self.name,self._parent)
        for i in self._instances:
            new_instance = self._instances[i].copy()
            new_instance._parent = new_coord_machine
            new_coord_machine._instances[new_instance.name] = new_instance
        new_coord_machine._version = self._version
        return new_coord_machine

    def _increase_version(self):
        # Important: this method should be called
        # after a self._accesses_lock.acquire()
        self._version += 1

    @locked('_instances_write_lock')
    def _add_new_instance(self,instance_name):
        new_instance = CoordInstance(instance_name, self)
        if self._instances.has_key(instance_name):
            logger = logging.getLogger(self.__class__.__name__)
            logger.warn('Is this normal? Replacing %s by %s' % (
                    self._instances[instance_name],
                    new_instance
                )
            )
        self._instances[instance_name] = new_instance
        self._increase_version()

    @locked('_instances_write_lock')
    def _add_new_server(self,instance_name,server_name,server_type,accesses,restrictions = ()):
        if not self._instances.has_key(instance_name):
            raise CoordExceptions.CoordInstanceNotFound(
                "Instance %s not found. Couldn't add server"
                % instance_name
            )
        self._instances[instance_name]._add_new_server(
                    server_name,
                    server_type,
                    accesses,
                    restrictions
                )
        self._increase_version()

    @locked('_instances_write_lock')
    def _append_accesses(self, instance_name, server_name, accesses):
        if not self._instances.has_key(instance_name):
            raise CoordExceptions.CoordInstanceNotFound(
                        'Instance %s not found' 
                        % instance_name
                    )
        self._instances[instance_name]._append_accesses(
                server_name,
                accesses
            )
        self._increase_version()
   
    @locked('_instances_write_lock')
    def _set_status(self, instance_name, server_name, new_status):
        if not self._instances.has_key(instance_name):
            raise CoordExceptions.CoordInstanceNotFound(
                        'Instance %s not found' 
                        % instance_name
                    )
        self._instances[instance_name]._set_status(
                server_name,
                new_status
            )
        self._increase_version()

    @locked('_instances_read_lock')
    def get_instances(self):
        """ get_instances() -> iterator

        get_instances provides a thread-safe iterator which will return a new
        instance in every iteration. If between iteration and iteration an 
        instance is added or removed, the iterator will return the new 
        instance and will avoid the removed ones.
        """
        walked_instances = []
        while True:
            
            self._instances_read_lock.acquire()
            
            keys = [ i for i in self._instances.keys() if not i in walked_instances ]
            if len(keys) >= 1:
                instance = self._instances[keys[0]]
                self._instances_read_lock.release()
                walked_instances.append(keys[0])
                yield instance
            else:
                #End :-)
                self._instances_read_lock.release()
                return
    
    def _update_info(self,other_machine):
        for other_instance in other_machine.get_instances():
            self._instances_write_lock.acquire()
            try:
                try:
                    instance = self._instances[other_instance.name]
                except CoordExceptions.CoordInstanceNotFound:
                    instance = self._add_new_instance(
                            other_instance.name
                        )
                instance._update_info(other_instance)
            finally:
                self._instances_write_lock.release()


    def __getitem__(self,name):
        if type(name) is str:
            key = name
        elif isinstance(name,CoordAddress.CoordAddress) and (
                name.is_instance() or name.is_server()
            ):
            key = name.instance_id
        else:
            raise CoordExceptions.CoordInvalidKey(
                "Invalid key: %s. Only strings and server or instance CoordAddress are allowed" 
                % name
            )
        self._instances_read_lock.acquire()
        try:
            if self._instances.has_key(key):
                instance = self._instances[key]
            else:
                raise CoordExceptions.CoordInstanceNotFound(
                        'Instance %s not found in %s' %
                        (
                            name,
                            self.name
                        )
                )
        finally:
            self._instances_read_lock.release()
        if type(name) is str or name.is_instance():
            return instance
        else:   #name is a CoordAddress aiming a server
            return instance[name]

    @locked('_instances_write_lock')
    def __setitem__(self,number,value):
        self._instances[number] = value
        self._increase_version()
            
###############################################################################
#                                                                             #
#                           CoordinationMap                                   #
#                                                                             #
###############################################################################

class CoordinationMap(object):
    def __init__(self):
        object.__init__(self)

        self._machines_lock = lock.RWLock()
        self._machines_read_lock  = self._machines_lock.read_lock()
        self._machines_write_lock = self._machines_lock.write_lock()
        #self._version will increase each time something is changed
        self._version = 0
        #_machines is a set of CoordMachines
        self._machines = {}
        #Some way, make relationships or graphs between different
        #nodes, to know who can talk with who

    def copy(self):
        new_coord_map = CoordinationMap()
        self._machines_read_lock.acquire()
        try:
            for i in self._machines:
                new_machine = self._machines[i].copy()
                new_machine._parent = new_coord_map
                new_coord_map._machines[new_machine.name] = new_machine
            new_coord_map._version = self._version
        finally:
            self._machines_read_lock.release()
        return new_coord_map

    @property
    @locked('_machines_read_lock')
    def version(self):
        return self._version
    
    def _increase_version(self):
        # Important: this method should be called
        # after a self._accesses_lock.acquire()
        self._version += 1

    @locked('_machines_write_lock')
    def add_new_machine(self, machine_name):
        new_machine = CoordMachine(machine_name,self)
        if self._machines.has_key(machine_name):
            logger = logging.getLogger(self.__class__.__name__)
            logger.warn('Is this normal? Replacing %s by %s' % (
                    self._machines[machine_name],
                    new_machine
                )
            )
        self._machines[machine_name] = new_machine
        self._increase_version()
   
    @locked('_machines_write_lock')
    def add_new_instance(self, machine_name, instance_name):
        if not self._machines.has_key(machine_name):
            raise CoordExceptions.CoordMachineNotFound(
                "Machine %s not found. Couldn't add instance"
                % machine_name
            )
        self._machines[machine_name]._add_new_instance(instance_name)
        self._increase_version()
    
    @locked('_machines_write_lock')
    def add_new_server(self, 
            machine_name, 
            instance_name, 
            server_name,
            server_type,
            accesses,
            restrictions = ()
        ):
        if not self._machines.has_key(machine_name):
            #TODO: testme (and all exceptions in this file)
            raise CoordExceptions.CoordMachineNotFound(
                "Machine %s not found. Couldn't add instance"
                % machine_name
            )
        self._machines[machine_name]._add_new_server(
                instance_name,
                server_name,
                server_type,
                accesses,
                restrictions
            )
        self._increase_version()

    @locked('_machines_write_lock')
    def append_accesses(self, machine_name, instance_name, server_name, accesses):
        if not self._machines.has_key(machine_name):
            raise CoordExceptions.CoordMachineNotFound(
                        'machine %s not found' 
                        % machine_name
                    )
        self._machines[machine_name]._append_accesses(
                instance_name,
                server_name,
                accesses
            )
        self._increase_version()
    
    @locked('_machines_write_lock')
    def set_status(self, machine_name, instance_name, server_name, new_status):
        if not self._machines.has_key(machine_name):
            raise CoordExceptions.CoordMachineNotFound(
                        'machine %s not found' 
                        % machine_name
                    )
        self._machines[machine_name]._set_status(
                instance_name,
                server_name,
                new_status
            )
        self._increase_version()

    def get_machines(self):
        """ get_machines() -> iterator

        get_machines provides a thread-safe iterator which will return a new
        machine in every iteration. If between iteration and iteration an 
        machine is added or removed, the iterator will return the new 
        machine and will avoid the removed ones.
        """
        walked_machines = []
        while True:
            
            self._machines_read_lock.acquire()
            
            keys = [ i for i in self._machines.keys() if not i in walked_machines ]
            if len(keys) >= 1:
                machine = self._machines[keys[0]]
                self._machines_read_lock.release()
                walked_machines.append(keys[0])
                yield machine
            else:
                #End :-)
                self._machines_read_lock.release()
                return

    def __getitem__(self,name):
        """ __getitem__(self,name)

        If name is a string, it is interpreted as a machine_id, and 
        it returns the machine with that ID (or a CoordMachineNotFound 
        exception).

        If name is a CoordAddress, it returns the node pointed by the
        address. If the CoordAddress points a machine, it returns the
        machine, if the CoordAddress points a instance, it returns the
        instance, if the CoordAddress points a server, it returns the
        server. It can raise any CoordNodeNotFound exception
        (CoordMachineNotFound, CoordInstanceNotFound, CoordServerNotFound)
        """
        if type(name) is str:
            key = name
        elif isinstance(name,CoordAddress.CoordAddress):
            key = name.machine_id
        else:
            raise CoordExceptions.CoordInvalidKey(
                "Invalid key: %s. Only strings and CoordAddress are allowed" 
                % name
            )
        self._machines_read_lock.acquire()
        try:
            if self._machines.has_key(key):
                machine = self._machines[key]
            else:
                raise CoordExceptions.CoordMachineNotFound(
                        'Machine %s not found' %
                        name
                )
        finally:
            self._machines_read_lock.release()
        if type(name) is str or name.is_machine():
            return machine
        else:   #name is a CoordAddress aiming instance or server
            return machine[name]

    def get_servers(self,original_server, server_type, restriction = None):
        """ get_servers(original_server,server_type) -> iterator 
        
        original_server is an instance of CoordServer
        server_type is a member of an enumerator listing the types of server

        Provided a CoordServer which needs to talk with a server of
        type server_type, the CoordinationMap will provide an iterator
        which will look from the closest to the furthest server which
        matches server_type. The point is that if in the same instance
        of the original_server we have a server of server_type, that 
        will be the best option, and nobody needs to look for anything
        better. But, if when trying to contact this server, it has too
        much load or whatever, the .next() will look for the next closest
        node, and so on. 

        The result is an iterator of voodoo.gen.coordinator.Access.Network,
        which will provide the way to connect to that network.
        """
        if original_server.address is None:
            raise CoordExceptions.CoordInvalidServer(
                    "Can't search original_server's address: %s" 
                        % original_server
                )
        instance_address = original_server.address.get_instance_address()
        instance = self[instance_address]
        
        # The first place to look for is in the same instance
        for i in instance.get_servers():
            if i.server_type == server_type:
                if i.address != original_server.address:
                    if restriction is None or restriction == () or i.can_handle(restriction):
                        networks = original_server.can_connect(i)
                        if len(networks) > 0:
                            yield i,networks

        # The next place to look for is in the same machine
        machine_address = original_server.address.get_machine_address()
        machine = self[machine_address]
        
        # TODO: This could be optimized so that when checking another
        # instance and a server is added to a walked instance, the
        # new server would be checked
        
        # Let's look for all the instances in the same machine
        # (except for the instance we have just checked)
        for i in machine.get_instances():
            if i != instance:
                for j in i.get_servers():
                    if j.server_type == server_type:
                        if restriction is None or restriction == () or j.can_handle(restriction):
                            networks = original_server.can_connect(j)
                            if len(networks) > 0:
                                yield j,networks
        
        # The next place to look for is in other machine
        for i in self.get_machines():
            if i != machine:
                for j in i.get_instances():
                    for k in j.get_servers():
                        if k.server_type == server_type:
                            if restriction is None or restriction == () or k.can_handle(restriction):
                                networks = original_server.can_connect(k)
                                if len(networks) > 0:
                                    yield k, networks

###############################################################################
#                                                                             #
#                     CoordinationMapController                               #
#                                                                             #
###############################################################################

def _map_checker(func):
    def wrapper(self,*args,**kargs):
        self._map_read_lock.acquire()
        try:
            if self._map is None:
                raise CoordExceptions.CoordMapNotInitialized(
                    'Map not initialized at %s' % self
                )
        finally:
            self._map_read_lock.release()
        return func(self,*args,**kargs)
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper

class CoordinationMapController(object):
    """ CoordinationController is a class that will provide an abstraction
    layer for all the information available about different servers. 
    Nobody except for CoordinationMap should modify any data of all
    this structure. CoordinationMap provides the methods to modify
    anything, and whenever asking for something, a deep copy will be
    received. In order to check if information has been modified, a 
    "version" field is given, increasing each time information is
    modified.

    It is important to note that this class just controls the CoordinationMap,
    it does not communicate with any server or anything like that. That's 
    delegated in an upper layer, here we trust everything is true. If
    set_server_status is called saying that one server is down, we will change
    this in the map. Whoever calls us should check if this is true or not.
    """
    def __init__(self, map = None):
        """ CoordinationMapController([map])

        Creates a new instance of the map
        """
        object.__init__(self)

        self._map_lock = lock.RWLock()
        self._map_read_lock  = self._map_lock.read_lock()
        self._map_write_lock = self._map_lock.write_lock()
        self._map = map

    @_map_checker
    @locked('_map_read_lock')
    def store(self,where):
        """store(self,where)

        Stores current coordination map in "where".
        Right now, where should be a file object.
        """
        # This could be improved using get_machines, etc.
        CoordinationInformationMapper.dump_to_file(
                    self._map,
                    where
                )

    @locked('_map_write_lock')
    def load(self,where):
        """ load(self,where)
        
        Loads current coordination map from "where".
        Right now, where should be a file object.

        Can raise any voodoo.gen.exceptions.coordination.CoordMappingException
        exception
        """
        # This could be improved using get_machines, etc.
        self._map = CoordinationInformationMapper.load_from_file(
                    where
                )

    @_map_checker
    @locked('_map_read_lock')
    def get_servers(self, original_server_address, server_type, restriction = None):
        original_server = self._map[original_server_address]
        return self._map.get_servers(original_server, server_type, restriction)
        
    @_map_checker
    @locked('_map_read_lock')
    def can_connect(self, server_address1, server_address2):
        server1 = self._map[server_address1]
        server2 = self._map[server_address2]
        return server1.can_connect(server2)
    

