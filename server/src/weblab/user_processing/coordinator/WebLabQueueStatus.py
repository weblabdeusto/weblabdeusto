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

class WebLabQueueStatus(object):
    WAITING              = 'waiting'
    WAITING_CONFIRMATION = 'waiting_confirmation'
    WAITING_INSTANCES    = 'waiting_instances'
    RESERVED             = 'reserved'
    def __init__(self, status):
        super(WebLabQueueStatus,self).__init__()
        self.status = status

    def __eq__(self, other):
        return isinstance(other, WebLabQueueStatus) and str(other) == str(self)

    def __cmp__(self, other):
        return cmp(str(self), str(other))

class WaitingQueueStatus(WebLabQueueStatus):
    def __init__(self, position_in_queue):
        super(WaitingQueueStatus,self).__init__(WebLabQueueStatus.WAITING)
        self.position = position_in_queue
    def __repr__(self):
        full_name = self.__class__.__module__ + '.' + self.__class__.__name__
        return "<%s; position_in_queue: %s>" % (full_name, self.position)

class WaitingInstancesQueueStatus(WebLabQueueStatus):
    def __init__(self, position_in_queue):
        super(WaitingInstancesQueueStatus,self).__init__(WebLabQueueStatus.WAITING_INSTANCES)
        self.position = position_in_queue
    def __repr__(self):
        full_name = self.__class__.__module__ + '.' + self.__class__.__name__
        return "<%s; position_in_queue: %s>" % (full_name, self.position)

class WaitingConfirmationQueueStatus(WebLabQueueStatus):
    def __init__(self, coord_address, time):
        super(WaitingConfirmationQueueStatus,self).__init__(WebLabQueueStatus.WAITING_CONFIRMATION)
        self.coord_address = coord_address
        self.time          = time
    def __repr__(self):
        full_name = self.__class__.__module__ + '.' + self.__class__.__name__
        return "<%s; coord_address: %s; time: %s>" % (full_name, self.coord_address, self.time)

class ReservedQueueStatus(WebLabQueueStatus):
    def __init__(self, coord_address, lab_session_id, time):
        super(ReservedQueueStatus,self).__init__(WebLabQueueStatus.RESERVED)
        self.coord_address  = coord_address
        self.lab_session_id  = lab_session_id
        self.time           = time
    def __repr__(self):
        full_name = self.__class__.__module__ + '.' + self.__class__.__name__
        return "<%s; coord_address: %s; lab_session_id: %s; time: %s>" % (full_name, self.coord_address, self.lab_session_id, self.time)

