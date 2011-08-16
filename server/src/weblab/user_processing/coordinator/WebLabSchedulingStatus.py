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

class WebLabSchedulingStatus(object):
    WAITING              = 'waiting'
    WAITING_CONFIRMATION = 'waiting_confirmation'
    WAITING_INSTANCES    = 'waiting_instances'
    RESERVED             = 'reserved'
    POST_RESERVATION     = 'post_reservation'

    def __init__(self, status):
        super(WebLabSchedulingStatus,self).__init__()
        self.status = status

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
    def __init__(self, position_in_queue):
        super(WaitingInstancesQueueStatus,self).__init__(WebLabSchedulingStatus.WAITING_INSTANCES)
        self.position = position_in_queue
    def __repr__(self):
        full_name = self.__class__.__module__ + '.' + self.__class__.__name__
        return "<%s; position_in_queue: %s>" % (full_name, self.position)

    def __eq__(self, other):
        return isinstance(other, WaitingInstancesQueueStatus) and self.position == other.position

    def __cmp__(self, other):
        if isinstance(other, (WaitingQueueStatus, WaitingConfirmationQueueStatus, ReservedStatus, PostReservationStatus)):
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
    def __init__(self, position_in_queue):
        super(WaitingQueueStatus,self).__init__(WebLabSchedulingStatus.WAITING)
        self.position = position_in_queue
    def __repr__(self):
        full_name = self.__class__.__module__ + '.' + self.__class__.__name__
        return "<%s; position_in_queue: %s>" % (full_name, self.position)

    def __eq__(self, other):
        return isinstance(other, WaitingQueueStatus) and self.position == other.position

    def __cmp__(self, other):
        if isinstance(other, (WaitingConfirmationQueueStatus, ReservedStatus, PostReservationStatus)):
            return 1
        if isinstance(other, WaitingQueueStatus):
            return cmp(self.position, other.position)
        return -1

############################################################
# 
# This status represents users which have been granted to 
# use an experiment but who are still waiting the experiment
# server to reply that the experiment has been initialized.
# 
class WaitingConfirmationQueueStatus(WebLabSchedulingStatus):
    def __init__(self, coord_address, time):
        super(WaitingConfirmationQueueStatus,self).__init__(WebLabSchedulingStatus.WAITING_CONFIRMATION)
        self.coord_address = coord_address
        self.time          = time
    def __repr__(self):
        full_name = self.__class__.__module__ + '.' + self.__class__.__name__
        return "<%s; coord_address: %s; time: %s>" % (full_name, self.coord_address, self.time)

    def __eq__(self, other):
        return isinstance(other, WaitingConfirmationQueueStatus) and self.coord_address == other.coord_address and self.time == other.time

    def __cmp__(self, other):
        if isinstance(other, (ReservedStatus, PostReservationStatus)):
            return 1
        if isinstance(other, WaitingConfirmationQueueStatus):
            return 0
        return -1

############################################################
# 
# This status represents users which are actively using  
# the experiment.
#
class ReservedStatus(WebLabSchedulingStatus):
    def __init__(self, coord_address, lab_session_id, time, initial_configuration, timestamp_before, timestamp_after):
        super(ReservedStatus,self).__init__(WebLabSchedulingStatus.RESERVED)
        self.coord_address         = coord_address
        self.lab_session_id        = lab_session_id
        self.time                  = time
        self.initial_configuration = initial_configuration
        self.timestamp_before      = timestamp_before
        self.timestamp_after       = timestamp_after

    def __repr__(self):
        full_name = self.__class__.__module__ + '.' + self.__class__.__name__
        return "<%s; coord_address: %s; lab_session_id: %s; time: %s; initial_configuration: %s; timestamp_before: %s; timestamp_after: %s>" % (full_name, self.coord_address, self.lab_session_id, self.time, self.initial_configuration, self.timestamp_before, self.timestamp_after)

    def __eq__(self, other):
        if not isinstance(other, ReservedStatus):
            return False

        return self.coord_address == other.coord_address and self.lab_session_id == other.lab_session_id \
                and self.time == other.time and self.initial_configuration == other.initial_configuration \
                and self.timestamp_before == other.timestamp_before and self.timestamp_after == other.timestamp_after

    def __cmp__(self, other):
        if isinstance(other, PostReservationStatus):
            return 1
        if isinstance(other, ReservedStatus):
            return 0
        return -1

############################################################
# 
# This status represents users which are actively using  
# the experiment.
#
class PostReservationStatus(WebLabSchedulingStatus):
    def __init__(self, finished, initial_data, end_data):
        super(PostReservationStatus,self).__init__(WebLabSchedulingStatus.POST_RESERVATION)
        self.finished     = finished
        self.initial_data = initial_data
        self.end_data     = end_data

    def __repr__(self):
        full_name = self.__class__.__module__ + '.' + self.__class__.__name__
        return "<%r; finished: %r; initial_data: %r; end_data: %r>" % (full_name, self.finished, self.initial_data, self.end_data)

    def __eq__(self, other):
        if not isinstance(other, PostReservationStatus):
            return False
        return self.finished == other.finished and self.initial_data == other.initial_data and self.end_data == other.end_data

    def __cmp__(self, other):
        if isinstance(other, PostReservationStatus):
            return 0
        return -1

