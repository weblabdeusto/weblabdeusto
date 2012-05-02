#!/usr/bin/env python
#-*-*- encoding: utf-8 -*-*-
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

WEBLAB_EXPERIMENT_TYPES              = 'weblab:experiment_types'
WEBLAB_EXPERIMENT_RESOURCES          = 'weblab:experiment_types:%s:resource_types'
WEBLAB_EXPERIMENT_INSTANCES          = 'weblab:experiment_types:%s:instances'
WEBLAB_EXPERIMENT_INSTANCE           = 'weblab:experiment_types:%s:instances:%s'

WEBLAB_RESOURCES                     = 'weblab:resources'
WEBLAB_RESOURCE                      = 'weblab:resources:%s'
WEBLAB_RESOURCE_EXPERIMENTS          = 'weblab:resources:%s:experiment_types'
WEBLAB_RESOURCE_RESERVATIONS         = 'weblab:resources:%s:reservations'
WEBLAB_RESOURCE_SLOTS                = 'weblab:resources:%s:slots'
WEBLAB_RESOURCE_WORKING              = 'weblab:resources:%s:working'
WEBLAB_RESOURCE_INSTANCE             = 'weblab:resources:%s:%s'
WEBLAB_RESOURCE_INSTANCE_EXPERIMENTS = 'weblab:resources:%s:%s:experiment_instances'

# PQUEUE
WEBLAB_RESOURCE_PQUEUE_RESERVATIONS  = 'weblab:resources:%s:reservations:pqueue'
WEBLAB_RESOURCE_PQUEUE_POSITIONS     = 'weblab:resources:%s:reservations:pqueue:positions'
WEBLAB_RESOURCE_PQUEUE_MAP           = 'weblab:resources:%s:reservations:pqueue:map'
WEBLAB_RESOURCE_PQUEUE_SORTED        = 'weblab:resources:%s:reservations:pqueue:sorted'

WEBLAB_RESERVATIONS_LOCK              = 'weblab:reservations:lock'
WEBLAB_RESERVATIONS                   = 'weblab:reservations'
WEBLAB_RESERVATION                    = 'weblab:reservations:%s'
WEBLAB_RESERVATION_STATUS             = 'weblab:reservations:%s:status'
WEBLAB_RESERVATIONS_ACTIVE_SCHEDULERS = 'weblab:reservations:%s:active_schedulers'

# PQUEUE
WEBLAB_RESERVATION_PQUEUE         = 'weblab:reservations:%s:pqueue'

CURRENT                      = 'current'

LAB_COORD                    = 'laboratory_coord_address'
RESOURCE_INST                = 'resource_instance'
EXPERIMENT_TYPE              = 'experiment_type'
RESOURCE_TYPE                = 'resource_type'

LATEST_ACCESS                = 'latest_access'
CLIENT_INITIAL_DATA          = 'client_initial_data'
SERVER_INITIAL_DATA          = 'server_initial_data'
REQUEST_INFO                 = 'request_info'
EXPERIMENT_TYPE              = 'experiment_type'

START_TIME                   = 'start_time'
TIME                         = 'time'
INITIALIZATION_IN_ACCOUNTING = 'initialization_in_accounting'
PRIORITY                     = 'priority'
TIMESTAMP_BEFORE             = 'timestamp_before'
TIMESTAMP_AFTER              = 'timestamp_after'
LAB_SESSION_ID               = 'lab_session_id'
INITIAL_CONFIGURATION        = 'initial_configuration'
ACTIVE_STATUS                = 'active_status'

STATUS_RESERVED              = 'status_reserved'
STATUS_WAITING_CONFIRMATION  = 'status_waiting_confirmation'

