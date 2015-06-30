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

class WebLabSchedulingStatus(object):
    WAITING              = 'waiting'
    WAITING_CONFIRMATION = 'waiting_confirmation'
    WAITING_INSTANCES    = 'waiting_instances'
    RESERVED_LOCAL       = 'reserved_local'
    RESERVED_REMOTE      = 'reserved_remote'
    POST_RESERVATION     = 'post_reservation'

    NOT_USED_YET_EXPERIMENT_STATUS  = (WAITING, WAITING_INSTANCES)
    POLLING_STATUS  = (WAITING, WAITING_CONFIRMATION, WAITING_INSTANCES, RESERVED_LOCAL)
    RESERVED_STATUS = (RESERVED_LOCAL, RESERVED_REMOTE)

    def __init__(self, status, reservation_id):
        super(WebLabSchedulingStatus,self).__init__()
        self.status         = status
        self.reservation_id = reservation_id

    def set_reservation_id(self, reservation_id):
        self.reservation_id = reservation_id

    def __eq__(self, other):
        return isinstance(other, WebLabSchedulingStatus) and str(other) == str(self)

###########################################################
#
# This status represents that the user is in a queue,
# waiting for an experiment which has no running instance,
# because these instances are all broken or because no
# instance is provided. Whenever a new instance is added
# or fixed, this reservation will advance moving to
# WaitingConfirmation and then to Reserved. Otherwise, it
# will only move when users which are before cancel the
# reservation.
#
class WaitingInstancesQueueStatus(WebLabSchedulingStatus):
    def __init__(self, reservation_id, position_in_queue):
        super(WaitingInstancesQueueStatus,self).__init__(WebLabSchedulingStatus.WAITING_INSTANCES, reservation_id)
        self.position = position_in_queue
    def __repr__(self):
        full_name = self.__class__.__module__ + '.' + self.__class__.__name__
        return "%s(reservation_id = %r position_in_queue = %r" % (full_name, self.reservation_id, self.position)

    def __eq__(self, other):
        return isinstance(other, WaitingInstancesQueueStatus) and self.position == other.position

    def __cmp__(self, other):
        if isinstance(other, (WaitingQueueStatus, WaitingConfirmationQueueStatus, LocalReservedStatus, RemoteReservedStatus, PostReservationStatus)):
            return 1
        if isinstance(other, WaitingInstancesQueueStatus):
            return cmp(self.position, other.position)
        return -1

############################################################
#
# This status represents users which are waiting for an
# active experiment.
#
class WaitingQueueStatus(WebLabSchedulingStatus):
    def __init__(self, reservation_id, position_in_queue):
        super(WaitingQueueStatus,self).__init__(WebLabSchedulingStatus.WAITING, reservation_id)
        self.position = position_in_queue
    def __repr__(self):
        full_name = self.__class__.__module__ + '.' + self.__class__.__name__
        return "%s(reservation_id = %r, position_in_queue= %r)" % (full_name, self.reservation_id, self.position)

    def __eq__(self, other):
        return isinstance(other, WaitingQueueStatus) and self.position == other.position

    def __cmp__(self, other):
        if isinstance(other, (WaitingConfirmationQueueStatus, LocalReservedStatus, RemoteReservedStatus, PostReservationStatus)):
            return 1
        if isinstance(other, WaitingQueueStatus):
            return cmp(self.position, other.position)
        return -1

############################################################
#
# This status represents users which are actively using
# the experiment.
#
class PostReservationStatus(WebLabSchedulingStatus):
    def __init__(self, reservation_id, finished, initial_data, end_data):
        super(PostReservationStatus,self).__init__(WebLabSchedulingStatus.POST_RESERVATION, reservation_id)
        self.finished     = finished
        self.initial_data = initial_data
        self.end_data     = end_data

    def __repr__(self):
        full_name = self.__class__.__module__ + '.' + self.__class__.__name__
        return "%s( reservation_id = %r, finished = %r, initial_data = %r, end_data = %r)" % (full_name, self.reservation_id, self.finished, self.initial_data, self.end_data)

    def __eq__(self, other):
        if not isinstance(other, PostReservationStatus):
            return False
        return self.finished == other.finished and self.initial_data == other.initial_data and self.end_data == other.end_data

    def __cmp__(self, other):
        if isinstance(other, (WaitingConfirmationQueueStatus, LocalReservedStatus, RemoteReservedStatus)):
            return 1
        if isinstance(other, PostReservationStatus):
            return 0
        return -1


############################################################
#
# This status represents users which have been granted to
# use an experiment but who are still waiting the experiment
# server to reply that the experiment has been initialized.
#
class WaitingConfirmationQueueStatus(WebLabSchedulingStatus):
    def __init__(self, reservation_id, url):
        super(WaitingConfirmationQueueStatus,self).__init__(WebLabSchedulingStatus.WAITING_CONFIRMATION, reservation_id)
        self.url           = url

    def __repr__(self):
        full_name = self.__class__.__module__ + '.' + self.__class__.__name__
        return "%s( reservation_id = %r, url = %r)" % (full_name, self.reservation_id, self.url)

    def __eq__(self, other):
        return isinstance(other, WaitingConfirmationQueueStatus)

    def __cmp__(self, other):
        if isinstance(other, (LocalReservedStatus, RemoteReservedStatus)):
            return 1
        if isinstance(other, WaitingConfirmationQueueStatus):
            return 0
        return -1

############################################################
#
# This status represents users which are actively using
# the experiment in this campus.
#
class LocalReservedStatus(WebLabSchedulingStatus):
    def __init__(self, reservation_id, coord_address, lab_session_id, exp_info, time, initial_configuration, timestamp_before, timestamp_after, initialization_in_accounting, remaining_time, url):
        super(LocalReservedStatus,self).__init__(WebLabSchedulingStatus.RESERVED_LOCAL, reservation_id)
        self.coord_address                = coord_address
        self.lab_session_id               = lab_session_id
        self.exp_info                     = exp_info
        self.time                         = time
        self.initial_configuration        = initial_configuration
        self.timestamp_before             = timestamp_before
        self.timestamp_after              = timestamp_after
        self.initialization_in_accounting = initialization_in_accounting
        self.remaining_time               = remaining_time
        self.url                          = url

    def __repr__(self):
        full_name = self.__class__.__module__ + '.' + self.__class__.__name__
        return "%s( reservation_id = %r, coord_address = %r, lab_session_id = %r, exp_info = %r, time = %r, initial_configuration = %r, timestamp_before = %r, timestamp_after = %r, initialization_in_accounting = %r, remaining_time = %r, url = %r)" % (full_name, self.reservation_id, self.coord_address, self.lab_session_id, self.exp_info, self.time, self.initial_configuration, self.timestamp_before, self.timestamp_after, self.initialization_in_accounting, self.remaining_time, self.url)

    def __eq__(self, other):
        if not isinstance(other, LocalReservedStatus):
            return False

        return self.coord_address == other.coord_address and self.lab_session_id == other.lab_session_id \
                and self.exp_info == other.exp_info \
                and self.time == other.time and self.initial_configuration == other.initial_configuration \
                and self.timestamp_before == other.timestamp_before and self.timestamp_after == other.timestamp_after \
                and self.initialization_in_accounting == other.initialization_in_accounting

    def __cmp__(self, other):
        if isinstance(other, LocalReservedStatus):
            return 0
        if isinstance(other, RemoteReservedStatus):
            return 0
        return -1

############################################################
#
# This status represents users which are actively using
# the experiment in other campus.
#
class RemoteReservedStatus(WebLabSchedulingStatus):
    def __init__(self, reservation_id, remaining_time, initial_configuration, url, remote_reservation_id):
        super(RemoteReservedStatus,self).__init__(WebLabSchedulingStatus.RESERVED_REMOTE, reservation_id)
        self.remaining_time               = remaining_time
        self.initial_configuration        = initial_configuration
        self.url                          = url
        self.remote_reservation_id        = remote_reservation_id

    def set_remote_reservation_id(self, remote_reservation_id):
        self.remote_reservation_id = remote_reservation_id

    def __repr__(self):
        full_name = self.__class__.__module__ + '.' + self.__class__.__name__
        return "%s( reservation_id = %r, remaining_time = %r, initial_configuration = %r, url = %r, remote_reservation_id = %r)" % (full_name, self.reservation_id, self.remaining_time, self.initial_configuration, self.url, self.remote_reservation_id)

    def __eq__(self, other):
        if not isinstance(other, RemoteReservedStatus):
            return False

        return self.remaining_time == other.remaining_time and self.initial_configuration == other.initial_configuration and self.remote_reservation_id == other.remote_reservation_id

    def __cmp__(self, other):
        if isinstance(other, RemoteReservedStatus):
            return 0
        if isinstance(other, LocalReservedStatus):
            return 0
        return -1


