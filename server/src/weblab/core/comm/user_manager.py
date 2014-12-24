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
        return experiments

    @logged()
    @RFM.check_exceptions(EXCEPTIONS)
    def reserve_experiment(self, session_id, experiment_id, client_initial_data, consumer_data):
        """ reserve_experiment(session_id, experiment_id, client_initial_data) -> Reservation
            raises SessionNotFoundError, NoAvailableExperimentFoundError
        """
        sess_id = self._parse_session_id(session_id)
        exp_id  = self._parse_experiment_id(experiment_id)

        reservation_status = self._server.reserve_experiment(sess_id, exp_id, client_initial_data, consumer_data)
        return reservation_status

    @logged()
    @RFM.check_exceptions(EXCEPTIONS)
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

    @logged(except_for=(('file_content',2),))
    @RFM.check_exceptions(EXCEPTIONS)
    def send_file(self, reservation_id, file_content, file_info):
        """ send_file(reservation_id, file_content, file_info)
            raise SessionNotFoundError
        """
        sess_id = self._parse_session_id(reservation_id)
        response = self._server.send_file(sess_id, file_content, file_info)
        return response


    @logged(except_for=(('file_content',2),))
    @RFM.check_exceptions(EXCEPTIONS)
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
        return experiment_result

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
            serialized_experiment_result = experiment_result
            serialized_experiment_results.append(serialized_experiment_result)

        return serialized_experiment_results

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

class UserProcessingRemoteFacadeManagerJSON(RFM.AbstractJSON, AbstractUserProcessingRemoteFacadeManagerDict):
    pass

