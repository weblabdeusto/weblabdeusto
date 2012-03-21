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

#
# CoordVersions:
#
# The coordinator servers will get informed of new or modified
# servers. They will have to update each other about the information
# they have. In order to do this, they'll have to interchange
# some kind of message.
#
# The problem here is concurrency. We can't have a simple number of
# version, since two different servers could increment it at the same
# time. We need every single server to have their own ID, and every
# coordinator server needs to have a map of { id : server_version }.
#
# Any time a server knows that anything changes, it will increase its
# own version, with the changes from the last version, and then it
# tell the changes to other servers.
#
# The possible problems of this approach are the lack of previous
# versions. If a server gets connected for first time, it doesn't have
# the previous versions of each server, so it doesn't know how to apply
# the changes. If a server loses a message, if it simply can't find it
# (it's on other network or something like that), or even worse, if a
# server misses to send a message, all the servers would get collapsed,
# because they wouldn't be able to update ones each other.
#
# Due to this possible problems, the versions system should be able to
# sum multiple patches. Something like "Changes between version 12 and
# 14". Patches should also be dependent on versions of other servers.
#
# So, a patch will have:
# a) That server's version number
# b) The dependencies of that version
# c) The changes themselves, in the following format:
#   an ordered list of a change:
#       1) CoordAddress
#       2) new | delete | switch_on | switch_off
# d) Servers which already know about this patch
#
# When a coordinator server receives a patch, it will check if it has
# already been applied. If it hasn't, it will try to apply it.
# To do so, it will check if the dependencies of the patch are matched.
# If they're not matched, it will ask the server who provided the patch
# for the dependencies, calculating which ones are needed. Once
# dependencies are all applied, the server will try to apply the patch
# itself. If successfully applied, it will add itself to the list of
# servers which already know about the patch, and will contact the rest
# of the servers.
#
# The main problem a coordinator server might have is receiving
# information from a server, with dependencies in earlier versions, and
# coming from other branch. In these cases, where integrity is in danger,
# the coordinator server will have to modify the new patch into another
# patch that will fit in the current branch. It will also contact the
# server which provided the patch to update it to the current branch.
#
# How are these modifications managed?
#  _________________________________________________________________
# |                |        |          |             |              |
# | State \ Action |  New   |  Delete  |  Switch on  |  Switch off  |
# |                |        |          |             |              |
# |________________|________|__________|_____________|______________|
# |                |        |          |             |              |
# |   It's on      |  Ign   | CONFLICT |    Ign      |  CONFLICT    |
# |________________|________|__________|_____________|______________|
# |                |        |          |             |              |
# |   It's off     |  Ign   | CONFLICT |  CONFLICT   |    Ign       |
# |________________|________|__________|_____________|______________|
# |                |        |          |             |              |
# | Doesn't exist  |  New   |   Ign    |  CONFLICT   |  CONFLICT    |
# |________________|________|__________|_____________|______________|
#
#
# As we can see, there are two kinds of conflicts here:
# a) A machine that we think that exists is said to be removed
# b) A machine that we think that doesn't exist is said to be switched
# on or off
# c) A machine that we think is switched on is said to be switched off
# or viceversa
#
# The only way to solve these conflicts is to check this information. To
# do so, if the coordinator server can talk with the machine directly, it
# will do so. If there is no way to contact, the coordinator server will
# just look for a coordinator which can talk with the server, or a coordinator
# that can talk with a coordinator which can talk with the server.
#

import voodoo.gen.coordinator.CoordAddress as CoordAddress
import voodoo.gen.exceptions.coordinator.CoordVersionErrors as CoordVersionErrors

###############################################################################
#                                                                             #
#                            ChangeActions                                    #
#                                                                             #
###############################################################################

class ChangeActions(object):
    NEW        = 'NEW'
    DELETE     = 'DELETE'
    SWITCH_ON  = 'SWITCH_ON'
    SWITCH_OFF = 'SWITCH_OFF'

    @staticmethod
    def getChangeActionValues():
        return ChangeActions.NEW, ChangeActions.DELETE, ChangeActions.SWITCH_ON, ChangeActions.SWITCH_OFF


###############################################################################
#                                                                             #
#                         CoordVersionChange                                  #
#                                                                             #
###############################################################################

class CoordVersionChange(object):
    # CoordVersionChange: it just has the action and where the action is taken
    def __init__(self, address, action):
        object.__init__(self)

        if not action in ChangeActions.getChangeActionValues():
            raise CoordVersionErrors.CoordVersionNotAnActionError(
                        '%s: not a ChangeAction' % action
                    )
        if not address.__class__ == CoordAddress.CoordAddress:
            raise CoordVersionErrors.CoordVersionNotAnAddressError(
                        '%s: not a CoordAddress' % address
                    )
        self.address = address
        self.action = action
        self.number_in_patch = 0

# The changes should be applied in order, but not sequentially:
# In case there is an error, we don't want to apply the rest of
# the branch, but we might want to apply other branches to reduce
# the number of not-updated information.
#
# In order to do so, we will build a tree of dependencies:
#
# Imagine machine1, which has instance1 and instance2, machine2,
# which has instance3, and instance4 is member of machine3, which
# is not modified. If everything (except for machine3) is modified,
# the structure would be something like:
#
# {
#    machine1 : MachineChange (1),
#    machine2 : MachineChange (2),
#    instance3 : InstanceChange (1)
# }
#
# where:
#
# MachineChange (1)
#     changes = [ change ]
#     instances = {
#            instance1 : InstanceChange (2)
#            instance2 : InstanceChange (3)
#     }
#
# MachineChange (2)
#    changes = [ change ]
#    instances = {
#           instance3 : InstanceChange (4)
#    }
#
# InstanceChange (1)
#    changes = [ change ]
#
# InstanceChange (2)
#    changes = [ change ]
#
# InstanceChange (3)
#    change = [ change, change ]
#
# If there is a problem in change1 at instance2, the server
# will still be able to apply changes in machine2, instance3,
# and instance1. If the problem is in machine2, changes in instance3
# will not be applicable, but still all machine1 and instance3 will.
#
# TODO: Consider deletes: if I create a machine, I delete it, I
# create it again, and I delete it again... well, somehow there can
# be problems. Should some changes modify other changes?
#

###############################################################################
#                                                                             #
#                            ServerChange                                     #
#                                                                             #
###############################################################################

class ServerChange(object):
    def __init__(self):
        object.__init__(self)
        self.changes = []
    def append_change(self,change):
        self.changes.append(change)

###############################################################################
#                                                                             #
#                           InstanceChange                                    #
#                                                                             #
###############################################################################

class InstanceChange(object):
    def __init__(self):
        object.__init__(self)
        self.changes = []
        self.servers = {}
    def append_change(self,change):
        if change.address.is_instance():
            self.changes.append(change)
        elif change.address.is_server():
            if not self.servers.has_key(change.address):
                self.servers[change.address] = ServerChange()
            self.servers[change.address].append_change(change)
        else:
            pass #TODO

###############################################################################
#                                                                             #
#                           MachineChange                                     #
#                                                                             #
###############################################################################

class MachineChange(object):
    def __init__(self):
        object.__init__(self)
        self.changes = []
        self.instances = {}
        self.servers = {}
    def append_change(self,change):
        if change.address.is_machine():
            self.changes.append(change)
        elif change.address.is_instance():
            if not self.instances.has_key(change.address):
                self.instances[change.address] = InstanceChange()
            self.instances[change.address].append_change(change)
        elif change.address.is_server():
            instance_address = change.address.get_instance_address()
            if self.instances.has_key(instance_address):
                self.instances[instance_address].append_change(change)
            elif self.servers.has_key(change.address):
                self.servers[change.address].append_change(change)
            else:
                self.servers[change.address] = ServerChange()
                self.servers[change.address].append_change(change)
        else:
            pass #TODO

###############################################################################
#                                                                             #
#                              CoordPatch                                     #
#                                                                             #
###############################################################################

class CoordPatch(object):
    def __init__(self, version_number ):
        object.__init__(self)
        # The version_number is given
        self.version_number = version_number
        self.dependencies = {}
        self.changes = {}
        self.servers_who_know_about = []
        self.current_number = 0
    def append_change(self,change):
        change.number_in_patch = self.current_number
        self.current_number += 1

        if change.address.is_machine():

            if not self.changes.has_key(change.address):
                self.changes[change.address] = MachineChange()
            self.changes[change.address].append_change(change)

        elif change.address.is_instance():

            machine_address = change.address.get_machine_address()

            if self.changes.has_key(machine_address):
                self.changes[machine_address].append_change(change)
            elif self.changes.has_key(change.address):
                self.changes[change.address].append_change(change)
            else:
                self.changes[change.address] = InstanceChange()
                self.changes[change.address].append_change(change)

        elif change.address.is_server():

            machine_address = change.address.get_machine_address()
            instance_address = change.address.get_instance_address()

            if self.changes.has_key(machine_address):
                self.changes[machine_address].append_change(change)
            elif self.changes.has_key(instance_address):
                self.changes[instance_address].append_change(change)
            elif self.changes.has_key(change.address):
                self.changes[change.address].append_change(change)
            else:
                self.changes[change.address] = ServerChange()
                self.changes[change.address].append_change(change)

        else:
            pass # TODO

###############################################################################
#                                                                             #
#                             CoordVersion                                    #
#                                                                             #
###############################################################################


class CoordVersion(object):
    def __init__(self,address):
        object.__init__(self)
        self._address = address
        self._version_lock = threading.Lock()
        self._versions = {
            #Sample
            # some_CoordAddress.address : CoordAtomicVersion
        }

    def increment(self):
        self._version_lock.acquire()
        try:
            #TODO
            self._versions[self._address].increment()
        finally:
            self._version_lock.release()

