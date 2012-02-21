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

from voodoo.log import logged
import voodoo.sessions.session_id as SessionId

import weblab.comm.manager as RFM

import weblab.data.command as Command
import weblab.data.client_address as ClientAddress
from weblab.data.experiments import ExperimentId

import weblab.core.exc as coreExc
import weblab.exc as WebLabErrors
import voodoo.gen.exceptions.exceptions as VoodooErrors

import weblab.core.comm.codes as UPFCodes

EXCEPTIONS = (
        # EXCEPTION                                              CODE                                                   PROPAGATE TO CLIENT
        (coreExc.SessionNotFoundError,      UPFCodes.CLIENT_SESSION_NOT_FOUND_EXCEPTION_CODE,      True),
        (coreExc.NoCurrentReservationError, UPFCodes.CLIENT_NO_CURRENT_RESERVATION_EXCEPTION_CODE, True),
        (coreExc.UnknownExperimentIdError,  UPFCodes.CLIENT_UNKNOWN_EXPERIMENT_ID_EXCEPTION_CODE,  True),
        (coreExc.WebLabCoreError,       UPFCodes.UPS_GENERAL_EXCEPTION_CODE,                   False),
        (WebLabErrors.WebLabError,                       UPFCodes.WEBLAB_GENERAL_EXCEPTION_CODE,                False),
        (VoodooErrors.GeneratorError,                    UPFCodes.VOODOO_GENERAL_EXCEPTION_CODE,                False),
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
            raises SessionNotFoundError
        """
        sess_id = self._parse_session_id(session_id)
        experiments = self._server.list_experiments(sess_id)

        self._fix_dates_in_experiments(experiments)
        return experiments

    @logged()
    @RFM.check_exceptions(EXCEPTIONS)
    def reserve_experiment(self, session_id, experiment_id, client_initial_data, consumer_data):
        """ reserve_experiment(session_id, experiment_id, client_initial_data) -> Reservation
            raises SessionNotFoundError, NoAvailableExperimentFoundError
        """
        current_client_address = ClientAddress.ClientAddress(self._get_client_address())
        sess_id = self._parse_session_id(session_id)
        exp_id  = self._parse_experiment_id(experiment_id)

        reservation_status = self._server.reserve_experiment(sess_id, exp_id, client_initial_data, consumer_data, current_client_address)
        return reservation_status

    @logged()
    @RFM.check_exceptions(EXCEPTIONS)
    @RFM.check_nullable
    def finished_experiment(self, reservation_id):
        """ finished_experiment(reservation_id)
            raise SessionNotFoundError
        """
        sess_id = self._parse_session_id(reservation_id)
        response = self._server.finished_experiment(sess_id)
        return response

    @logged()
    @RFM.check_exceptions(EXCEPTIONS)
    def get_reservation_status(self, reservation_id):
        """ get_reservation_status(reservation_id) -> Reservation
            raise SessionNotFoundError
        """
        sess_id = self._parse_session_id(reservation_id)
        return self._server.get_reservation_status(sess_id)

    # TODO: does ZSI support Attachments (yes in theory)? And in the rest of libraries used?
    @logged(except_for=(('file_content',2),))
    @RFM.check_exceptions(EXCEPTIONS)
    @RFM.check_nullable
    def send_file(self, reservation_id, file_content, file_info):
        """ send_file(reservation_id, file_content, file_info)
            raise SessionNotFoundError
        """
        sess_id = self._parse_session_id(reservation_id)
        response = self._server.send_file(sess_id, file_content, file_info)
        return response


    @logged(except_for=(('file_content',2),))
    @RFM.check_exceptions(EXCEPTIONS)
    @RFM.check_nullable
    def send_async_file(self, reservation_id, file_content, file_info):
        """ send_async_file(reservation_id, file_content, file_info)
            Sends a file. The request will be executed asynchronously.
            raise SessionNotFoundError
        """
        sess_id = self._parse_session_id(reservation_id)
        response = self._server.send_async_file(sess_id, file_content, file_info)
        return response

    @logged()
    @RFM.check_exceptions(EXCEPTIONS)
    @RFM.check_nullable
    def send_async_command(self, reservation_id, command):
        """ send_command(reservation_id, command)
            raise SessionNotFoundError
        """
        sess_id = self._parse_session_id(reservation_id)
        cmd     = self._parse_command(command)

        response = self._server.send_async_command(sess_id, cmd)
        return response

    @logged()
    @RFM.check_exceptions(EXCEPTIONS)
    @RFM.check_nullable
    def send_command(self, reservation_id, command):
        """ send_command(reservation_id, command)
            raise SessionNotFoundError
        """
        sess_id = self._parse_session_id(reservation_id)
        cmd     = self._parse_command(command)

        response = self._server.send_command(sess_id, cmd)
        return response

    @logged()
    @RFM.check_exceptions(EXCEPTIONS)
    @RFM.check_nullable
    def check_async_command_status(self, reservation_id, request_identifiers):
        """ check_async_command_status(reservation_id, command)
            raise SessionNotFoundError
        """

        # TODO: This will most likely require modifications.
        sess_id = self._parse_session_id(reservation_id)
        req_ids = self._parse_request_identifiers(request_identifiers)

        response = self._server.check_async_command_status(sess_id, req_ids)
        return response

    @logged()
    @RFM.check_exceptions(EXCEPTIONS)
    @RFM.check_nullable
    def poll(self, reservation_id):
        """ poll(session_id)
            raise SessionNotFoundError
        """
        sess_id = self._parse_session_id(reservation_id)
        return self._server.poll(sess_id)

    @logged()
    @RFM.check_exceptions(EXCEPTIONS)
    def get_user_information(self, session_id):
        """ get_user_information(session_id) -> User
            raise SessionNotFoundError
        """
        sess_id = self._parse_session_id(session_id)
        return self._server.get_user_information(sess_id)

    @logged()
    @RFM.check_exceptions(EXCEPTIONS)
    def get_experiment_use_by_id(self, session_id, reservation_id):
        """ get_experiment_use_by_id(session_id, reservation_id) -> ReservationResult
            raise SessionNotFoundError
        """
        sess_id = self._parse_session_id(session_id)
        reservation_id    = self._parse_session_id(reservation_id)
        experiment_result = self._server.get_experiment_use_by_id(sess_id, reservation_id)
        return self._serialize_experiment_result(experiment_result)

    @logged()
    @RFM.check_exceptions(EXCEPTIONS)
    def get_experiment_uses_by_id(self, session_id, reservation_ids):
        """ get_experiment_uses_by_id(session_id, reservation_ids) -> ReservationResult
            raise SessionNotFoundError
        """
        sess_id = self._parse_session_id(session_id)
        parsed_reservation_ids = []
        for reservation_id in reservation_ids:
            parsed_reservation_id = self._parse_session_id(reservation_id)
            parsed_reservation_ids.append(parsed_reservation_id)

        experiment_results = self._server.get_experiment_uses_by_id(sess_id, parsed_reservation_ids)

        serialized_experiment_results = []
        for experiment_result in experiment_results:
            serialized_experiment_result = self._serialize_experiment_result(experiment_result)
            serialized_experiment_results.append(serialized_experiment_result)

        return serialized_experiment_results

    #
    # admin service
    #

    @logged()
    @RFM.check_exceptions(EXCEPTIONS)
    def get_groups(self, session_id):
        """ get_groups(session_id) -> array of Group
            raises SessionNotFoundError
        """
        sess_id = self._parse_session_id(session_id)
        groups = self._server.get_groups(sess_id)
        return groups

    @logged()
    @RFM.check_exceptions(EXCEPTIONS)
    def get_experiments(self, session_id):
        """ get_experiments(session_id) -> array of Experiment
            raises SessionNotFoundError
        """
        sess_id = self._parse_session_id(session_id)
        experiments = self._server.get_experiments(sess_id)
        return experiments

    @logged()
    @RFM.check_exceptions(EXCEPTIONS)
    def get_users(self, session_id):
        """get_users(session_id) -> array of User
    	   raises SessionNotFoundError
		"""
        sess_id = self._parse_session_id(session_id)
        users = self._server.get_users(sess_id)
        return users

    @logged()
    @RFM.check_exceptions(EXCEPTIONS)
    def get_roles(self, session_id):
        """get_roles(session_id) -> array of Role
           raises SessionNotFoundError
        """
        sess_id = self._parse_session_id(session_id)
        roles = self._server.get_roles(sess_id)
        return roles

    @logged()
    @RFM.check_exceptions(EXCEPTIONS)
    def get_experiment_uses(self, session_id, from_date, to_date, group_id, experiment_id, start_row, end_row, sort_by):
        """ get_experiment_uses(session_id, from_date, to_date, group_id, experiment_id) -> array of ExperimentUse
            raises SessionNotFoundError
        """
        sess_id = self._parse_session_id(session_id)
        experiment_uses = self._server.get_experiment_uses(sess_id, from_date, to_date, group_id, experiment_id, start_row, end_row, sort_by)
        return experiment_uses

    @logged()
    @RFM.check_exceptions(EXCEPTIONS)
    def get_user_permissions(self, session_id):
        """ get_user_permissions(session_id) -> array of Permission
            raises SessionNotFoundError
        """
        sess_id = self._parse_session_id(session_id)
        permissions = self._server.get_user_permissions(sess_id)
        return permissions

    @logged()
    @RFM.check_exceptions(EXCEPTIONS)
    def get_permission_types(self, session_id):
        """ get_permission_types(session_id) -> array of PermissionType
        """
        sess_id = self._parse_session_id(session_id)
        permission_types = self._server.get_permission_types(sess_id)
        return permission_types

    def _fix_dates_in_experiments(self, experiments_allowed):
        # This is the default behaviour. Overrided by XML-RPC
        pass

    def _check_nullable_response(self, response):
        # This is the default behaviuor. Overrided by XML-RPC,
        # where None is not an option
        return response

    def _serialize_experiment_result(self, experiment_result):
        return experiment_result

class AbstractUserProcessingRemoteFacadeManagerObject(AbstractUserProcessingRemoteFacadeManager):
    # When accessing structures, this class uses instance.attribute
    # Useful for ZSI and other libraries

    def _parse_session_id(self, session_id):
        return SessionId.SessionId(session_id.id)

    def _parse_experiment_id(self, exp_id):
        return ExperimentId(
                exp_id.exp_name,
                exp_id.cat_name
            )

    def _parse_command(self, command):
        return Command.Command(command.commandstring)

    def _parse_request_identifiers(self, request_identifiers):
        print "[DBG] Request identifiers: " + str(request_identifiers)
        return request_identifiers

class AbstractUserProcessingRemoteFacadeManagerDict(AbstractUserProcessingRemoteFacadeManager):
    # When accessing structures, this class uses instance['attribute']
    # Useful for SimpleXMLRPCServer, JSON, etc.

    def _parse_session_id(self, session_id):
        return SessionId.SessionId(session_id['id'])

    def _parse_experiment_id(self, exp_id):
        return ExperimentId(
            exp_id['exp_name'],
            exp_id['cat_name']
        )

    def _parse_command(self, command):
        return Command.Command(command['commandstring'])

    def _parse_request_identifiers(self, request_identifiers):
        """ Like the other _parse methods, thise receives the parameter and
            returns the appropriate object. In this case, it receives and
            returns a simple list, so nothing needs to be done
        """
        print "[DBG] Request identifiers dict: " + str(request_identifiers)
        return request_identifiers

class UserProcessingRemoteFacadeManagerZSI(RFM.AbstractZSI, AbstractUserProcessingRemoteFacadeManagerObject):
    pass

class UserProcessingRemoteFacadeManagerJSON(RFM.AbstractJSON, AbstractUserProcessingRemoteFacadeManagerDict):
    pass

class UserProcessingRemoteFacadeManagerXMLRPC(RFM.AbstractXMLRPC, AbstractUserProcessingRemoteFacadeManagerDict):
    pass



