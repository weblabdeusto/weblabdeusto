#!/usr/bin/env python
#-*-*- encoding: utf-8 -*-*-
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
#         Luis Rodriguez <luis.rodriguez@opendeusto.es>
# 

import time as time_module
import json

from voodoo.cache import cache
import voodoo.resources_manager as ResourceManager

import weblab.comm.context as RemoteFacadeContext

import weblab.core.exc as core_exc
import weblab.core.coordinator.exc as coord_exc

_resource_manager = ResourceManager.CancelAndJoinResourceManager("UserProcessor")

#TODO: configuration
LIST_EXPERIMENTS_CACHE_TIME     = 15  # seconds
GET_GROUPS_CACHE_TIME           = 15  # seconds
GET_ROLES_CACHE_TIME            = 15  # seconds
GET_USERS_CACHE_TIME            = 15  # seconds
GET_EXPERIMENTS_CACHE_TIME      = 15  # seconds
GET_EXPERIMENT_USES_CACHE_TIME  = 15  # seconds
GET_USER_INFORMATION_CACHE_TIME = 200 # seconds
GET_USER_PERMISSIONS_CACHE_TIME = 200 # seconds
DEFAULT_EXPERIMENT_POLL_TIME    = 300  # seconds
EXPERIMENT_POLL_TIME            = 'core_experiment_poll_time'

@cache(LIST_EXPERIMENTS_CACHE_TIME, _resource_manager)
def list_experiments(db_manager, db_session_id):
    return db_manager.get_available_experiments(db_session_id)

@cache(GET_USER_INFORMATION_CACHE_TIME, _resource_manager)
def get_user_information(db_manager, db_session_id):
    return db_manager.retrieve_user_information(db_session_id)

@cache(GET_GROUPS_CACHE_TIME, _resource_manager)
def get_groups(db_manager, db_session_id, parent_id):
    return db_manager.get_groups(db_session_id, parent_id)

@cache(GET_ROLES_CACHE_TIME, _resource_manager)
def get_roles(db_manager, db_session_id):
    return db_manager.get_roles(db_session_id)

@cache(GET_USERS_CACHE_TIME, _resource_manager)
def get_users(db_manager, db_session_id):
    """ Retrieves the users from the database, through the database manager. """
    return db_manager.get_users(db_session_id)

@cache(GET_EXPERIMENTS_CACHE_TIME, _resource_manager)
def get_experiments(db_manager, db_session_id):
    return db_manager.get_experiments(db_session_id)

@cache(GET_EXPERIMENT_USES_CACHE_TIME, _resource_manager)
def get_experiment_uses(db_manager, db_session_id, from_date, to_date, group_id, experiment_id, start_row, end_row, sort_by):
    return db_manager.get_experiment_uses(db_session_id, from_date, to_date, group_id, experiment_id, start_row, end_row, sort_by)

@cache(GET_USER_PERMISSIONS_CACHE_TIME, _resource_manager)
def get_user_permissions(db_manager, db_session_id):
    return db_manager.get_user_permissions(db_session_id)


class UserProcessor(object):
    """
    User processors are linked to specific sessions. Requests that arrive to the
    UserProcessingManager will be told apart through their session_id and forwarded
    to the appropriate UserProcessor.
    """

    EXPIRATION_TIME_NOT_SET=-1234

    def __init__(self, locator, session, cfg_manager, coordinator, db_manager, commands_store):
        self._locator         = locator
        self._session         = session
        self._cfg_manager     = cfg_manager
        self._coordinator     = coordinator
        self._db_manager      = db_manager
        self._commands_store  = commands_store
        self.time_module      = time_module

    def list_experiments(self):
        db_session_id         = self._session['db_session_id']
        return list_experiments(self._db_manager, db_session_id)

    def get_user_information(self):
        if 'user_information' in self._session:
            return self._session['user_information']

        db_session_id               = self._session['db_session_id']
        user_information            = get_user_information(self._db_manager, db_session_id)
        self._session['user_information'] = user_information
        return user_information

    def get_session(self):
        return self._session

    def get_session_id(self):
        return self._session['session_id']

    # 
    # Experiments
    # 

    def reserve_experiment(self, experiment_id, serialized_client_initial_data, serialized_consumer_data, client_address):

        context = RemoteFacadeContext.get_context()

        # Put user information in the session
        self.get_user_information()

        self._session['experiment_id'] = experiment_id

        reservation_info = self._session['reservation_information'] = {}
        reservation_info['user_agent']    = context.get_user_agent()
        reservation_info['referer']       = context.get_referer()
        reservation_info['mobile']        = context.is_mobile()
        reservation_info['facebook']      = context.is_facebook()
        reservation_info['from_ip']       = client_address.client_address
        reservation_info['username']      = self._session['db_session_id'].username
        reservation_info['role']          = self._session['db_session_id'].role

        try:
            client_initial_data = json.loads(serialized_client_initial_data)
        except ValueError:
            # TODO: to be tested
            raise core_exc.UserProcessingException( "Invalid client_initial_data provided: a json-serialized object expected" )

        try:
            consumer_data = json.loads(serialized_consumer_data)
        except ValueError:
            raise core_exc.UserProcessingException( "Invalid serialized_consumer_data provided: a json-serialized object expected" )
            

        experiments = [ 
                exp for exp in self.list_experiments()
                if exp.experiment.name           == experiment_id.exp_name 
                and exp.experiment.category.name == experiment_id.cat_name
            ]

        if len(experiments) == 0:
            raise core_exc.UnknownExperimentIdException( "User can't access that experiment (or that experiment type does not exist)" )

        experiment_allowed = experiments[0]
        try:
            status, reservation_id    = self._coordinator.reserve_experiment(
                    experiment_allowed.experiment.to_experiment_id(), 
                    experiment_allowed.time_allowed, 
                    experiment_allowed.priority,
                    experiment_allowed.initialization_in_accounting,
                    client_initial_data,
                    reservation_info
                )
        except coord_exc.ExperimentNotFoundException:
            raise core_exc.NoAvailableExperimentFoundException(
                "No experiment of type <%s,%s> is currently deployed" % (
                        experiment_id.exp_name, 
                        experiment_id.cat_name
                    )
            )


        self._session['reservation_information'].pop('from_ip', None)
        self._session['reservation_id']   = reservation_id
            
        return status

    def logout(self):
        # self.finished_experiment()
        pass

    def update_latest_timestamp(self):
        self._session['latest_timestamp'] = self._utc_timestamp()

    def _utc_timestamp(self):
        return self.time_module.time()

    #
    # admin service
    #
    
    def get_users(self):
        db_session_id        = self._session['db_session_id']
        return get_users(self._db_manager, db_session_id)

    def get_groups(self, parent_id=None):
        db_session_id         = self._session['db_session_id']
        return get_groups(self._db_manager, db_session_id, parent_id)
    
    def get_roles(self):
        db_session_id         = self._session['db_session_id']
        return get_roles(self._db_manager, db_session_id)

    def get_experiments(self):
        db_session_id         = self._session['db_session_id']
        return get_experiments(self._db_manager, db_session_id)

    def get_experiment_uses(self, from_date, to_date, group_id, experiment_id, start_row, end_row, sort_by):
        db_session_id         = self._session['db_session_id']
        return get_experiment_uses(self._db_manager, db_session_id, from_date, to_date, group_id, experiment_id, start_row, end_row, sort_by)

    def get_user_permissions(self):
        db_session_id         = self._session['db_session_id']
        return get_user_permissions(self._db_manager, db_session_id)

