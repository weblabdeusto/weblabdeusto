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
# 

from voodoo.log import logged
import voodoo.sessions.SessionId as SessionId

import weblab.facade.RemoteFacadeManager as RFM

import weblab.data.Command as Command
import weblab.data.ClientAddress as ClientAddress
import weblab.data.experiments.ExperimentId as ExperimentId

import weblab.exceptions.user_processing.UserProcessingExceptions as UserProcessingExceptions
import weblab.exceptions.WebLabExceptions as WebLabExceptions
import voodoo.gen.exceptions.exceptions as VoodooExceptions

import weblab.user_processing.facade.UserProcessingFacadeCodes as UPFCodes

EXCEPTIONS = (
        # EXCEPTION                                              CODE                                                   PROPAGATE TO CLIENT
        (UserProcessingExceptions.SessionNotFoundException,      UPFCodes.CLIENT_SESSION_NOT_FOUND_EXCEPTION_CODE,      True),
        (UserProcessingExceptions.NoCurrentReservationException, UPFCodes.CLIENT_NO_CURRENT_RESERVATION_EXCEPTION_CODE, True),
        (UserProcessingExceptions.UnknownExperimentIdException,  UPFCodes.CLIENT_UNKNOWN_EXPERIMENT_ID_EXCEPTION_CODE,  True),
        (UserProcessingExceptions.UserProcessingException,       UPFCodes.UPS_GENERAL_EXCEPTION_CODE,                   False),
        (WebLabExceptions.WebLabException,                       UPFCodes.WEBLAB_GENERAL_EXCEPTION_CODE,                False),
        (VoodooExceptions.GeneratorException,                    UPFCodes.VOODOO_GENERAL_EXCEPTION_CODE,                False),
        (Exception,                                              UPFCodes.PYTHON_GENERAL_EXCEPTION_CODE,                False)
    )

class AbstractUserProcessingRemoteFacadeManager(RFM.AbstractRemoteFacadeManager):
    @logged()
    @RFM.check_exceptions(EXCEPTIONS)
    @RFM.check_nullable
    def logout(self, session_id):
        """ logout(session_id)
        """
        sess_id = self._parse_session_id(session_id)
        response = self._server.logout(sess_id)
        return response
   
    @logged()
    @RFM.check_exceptions(EXCEPTIONS)
    def list_experiments(self, session_id):
        """ list_experiments(session_id) -> array of ExperimentAllowed
            raises SessionNotFoundException
        """
        sess_id = self._parse_session_id(session_id)
        experiments = self._server.list_experiments(sess_id)

        self._fix_dates_in_experiments(experiments)
        return experiments

    @logged()
    @RFM.check_exceptions(EXCEPTIONS)
    def reserve_experiment(self, session_id, experiment_id):
        """ reserve_experiment(session_id, experiment_id) -> Reservation
            raises SessionNotFoundException, NoAvailableExperimentFoundException
        """
        current_client_address = ClientAddress.ClientAddress(self._get_client_address())
        sess_id = self._parse_session_id(session_id)
        exp_id  = self._parse_experiment_id(experiment_id)

        reservation_status = self._server.reserve_experiment(sess_id, exp_id, current_client_address)
        return reservation_status
    
    @logged()
    @RFM.check_exceptions(EXCEPTIONS)
    @RFM.check_nullable
    def finished_experiment(self, session_id):
        """ finished_experiment(session_id)
            raise SessionNotFoundException
        """
        sess_id = self._parse_session_id(session_id)
        response = self._server.finished_experiment(sess_id)
        return response
    
    @logged()
    @RFM.check_exceptions(EXCEPTIONS)
    def get_reservation_status(self, session_id):
        """ get_reservation_status(session_id) -> Reservation
            raise SessionNotFoundException
        """
        sess_id = self._parse_session_id(session_id)
        return self._server.get_reservation_status(sess_id)
    
    # TODO: does ZSI support Attachments (yes in theory)? And in the rest of libraries used?
    @logged(except_for=(('file_content',2),))
    @RFM.check_exceptions(EXCEPTIONS)
    @RFM.check_nullable
    def send_file(self, session_id, file_content, file_info):
        """ send_file(session_id, file_content, file_info)
            raise SessionNotFoundException
        """
        sess_id = self._parse_session_id(session_id)
        response = self._server.send_file(sess_id, file_content, file_info)
        return response
    
    # TODO: Implement this asynchronously. For now it's just a copy
    # of the standard send_file.
    @logged(except_for=(('file_content',2),))
    @RFM.check_exceptions(EXCEPTIONS)
    @RFM.check_nullable
    def send_async_file(self, session_id, file_content, file_info):
        """ send_async_file(session_id, file_content, file_info)
            raise SessionNotFoundException
        """
        sess_id = self._parse_session_id(session_id)
        response = self._server.send_async_file(sess_id, file_content, file_info)
        return response
    
    @logged()
    @RFM.check_exceptions(EXCEPTIONS)
    @RFM.check_nullable
    def send_async_command(self, session_id, command):
        """ send_command(session_id, command)
            raise SessionNotFoundException
        """
        sess_id = self._parse_session_id(session_id)
        cmd     = self._parse_command(command)

        response = self._server.send_async_command(sess_id, cmd)
        return response

    @logged()
    @RFM.check_exceptions(EXCEPTIONS)
    @RFM.check_nullable
    def send_command(self, session_id, command):
        """ send_command(session_id, command)
            raise SessionNotFoundException
        """
        sess_id = self._parse_session_id(session_id)
        cmd     = self._parse_command(command)

        response = self._server.send_command(sess_id, cmd)
        return response
    
    @logged()
    @RFM.check_exceptions(EXCEPTIONS)
    @RFM.check_nullable
    def check_async_command_status(self, session_id, request_identifiers):
        """ check_async_command_status(session_id, command)
            raise SessionNotFoundException
        """
        
        # TODO: This will most likely require modifications.
        sess_id = self._parse_session_id(session_id)
        req_ids = self._parse_request_identifiers(request_identifiers)
        
        response = self._server.check_async_command_status(sess_id, req_ids)
        return response
   
    @logged()
    @RFM.check_exceptions(EXCEPTIONS)
    @RFM.check_nullable
    def poll(self, session_id):
        """ poll(session_id)
            raise SessionNotFoundException
        """        
        sess_id = self._parse_session_id(session_id)
        return self._server.poll(sess_id)

    @logged()
    @RFM.check_exceptions(EXCEPTIONS)
    def get_user_information(self, session_id):
        """ get_user_information(session_id) -> User
            raise SessionNotFoundException
        """
        sess_id = self._parse_session_id(session_id)
        return self._server.get_user_information(sess_id)
   
    #
    # admin service
    #
    
    @logged()
    @RFM.check_exceptions(EXCEPTIONS)
    def get_groups(self, session_id):
        """ get_groups(session_id) -> array of Group
            raises SessionNotFoundException
        """
        sess_id = self._parse_session_id(session_id)
        groups = self._server.get_groups(sess_id)
        return groups
    
    @logged()
    @RFM.check_exceptions(EXCEPTIONS)
    def get_experiments(self, session_id):
        """ get_experiments(session_id) -> array of Experiment
            raises SessionNotFoundException
        """
        sess_id = self._parse_session_id(session_id)
        experiments = self._server.get_experiments(sess_id)
        return experiments
       
    @logged()
    @RFM.check_exceptions(EXCEPTIONS)
    def get_users(self, session_id):
        """get_users(session_id) -> array of User
    	   raises SessionNotFoundException
		"""
        sess_id = self._parse_session_id(session_id)
        users = self._server.get_users(sess_id)
        return users
    
    @logged()
    @RFM.check_exceptions(EXCEPTIONS)
    def get_roles(self, session_id):
        """get_roles(session_id) -> array of Role
           raises SessionNotFoundException
        """
        sess_id = self._parse_session_id(session_id)
        roles = self._server.get_roles(sess_id)
        return roles
    
    @logged()
    @RFM.check_exceptions(EXCEPTIONS)
    def get_experiment_uses(self, session_id, from_date, to_date, group_id, experiment_id, start_row, end_row, sort_by):
        """ get_experiment_uses(session_id, from_date, to_date, group_id, experiment_id) -> array of ExperimentUse
            raises SessionNotFoundException
        """
        sess_id = self._parse_session_id(session_id)
        experiment_uses = self._server.get_experiment_uses(sess_id, from_date, to_date, group_id, experiment_id, start_row, end_row, sort_by)
        return experiment_uses
    
    @logged()
    @RFM.check_exceptions(EXCEPTIONS)
    def get_user_permissions(self, session_id):
        """ get_user_permissions(session_id) -> array of Permission
            raises SessionNotFoundException
        """
        sess_id = self._parse_session_id(session_id)
        permissions = self._server.get_user_permissions(sess_id)
        return permissions

    def _fix_dates_in_experiments(self, experiments_allowed):
        # This is the default behaviour. Overrided by XML-RPC
        pass

    def _check_nullable_response(self, response):
        # This is the default behaviuor. Overrided by XML-RPC, 
        # where None is not an option
        return response

class AbstractUserProcessingRemoteFacadeManagerObject(AbstractUserProcessingRemoteFacadeManager):
    # When accessing structures, this class uses instance.attribute
    # Useful for ZSI and other libraries

    def _parse_session_id(self, session_id):
        return SessionId.SessionId(session_id.id)

    def _parse_experiment_id(self, exp_id):
        return ExperimentId.ExperimentId(
                exp_id.exp_name,
                exp_id.cat_name
            )

    def _parse_command(self, command):
        return Command.Command(command.commandstring)
    
    # TODO: This is yet to be implemented
    def _parse_request_identifiers(self, request_identifiers):
        return ""

class AbstractUserProcessingRemoteFacadeManagerDict(AbstractUserProcessingRemoteFacadeManager):
    # When accessing structures, this class uses instance['attribute']
    # Useful for SimpleXMLRPCServer, JSON, etc.

    def _parse_session_id(self, session_id):
        return SessionId.SessionId(session_id['id'])

    def _parse_experiment_id(self, exp_id):
        return ExperimentId.ExperimentId(
            exp_id['exp_name'],
            exp_id['cat_name']
        )

    def _parse_command(self, command):
        return Command.Command(command['commandstring'])

class UserProcessingRemoteFacadeManagerZSI(RFM.AbstractZSI, AbstractUserProcessingRemoteFacadeManagerObject):
    pass

class UserProcessingRemoteFacadeManagerJSON(RFM.AbstractJSON, AbstractUserProcessingRemoteFacadeManagerDict):
    pass

class UserProcessingRemoteFacadeManagerXMLRPC(RFM.AbstractXMLRPC, AbstractUserProcessingRemoteFacadeManagerDict):
    pass



