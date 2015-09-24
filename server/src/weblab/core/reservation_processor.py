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
#         Luis Rodriguez <luis.rodriguez@opendeusto.es>
#
from __future__ import print_function, unicode_literals

import random
import time as time_module

import voodoo.log as log

import weblab.configuration_doc as configuration_doc

import weblab.data.command as Command

import weblab.core.exc as core_exc
import weblab.core.reservations as Reservation
from weblab.core.file_storer import FileStorer

import weblab.core.coordinator.exc as coord_exc
import weblab.core.coordinator.status as scheduling_status
import weblab.core.coordinator.store as TemporalInformationStore

import weblab.lab.exc as LaboratoryErrors

DEFAULT_EXPERIMENT_POLL_TIME    = 350  # seconds
EXPERIMENT_POLL_TIME            = 'core_experiment_poll_time'


class ReservationProcessor(object):
    """ This class encapsulates the methods of the user dependent on the
    interaction with the experiment. This is a middle step before moving
    this class to the proxy server.  Previously, all these methods were
    implemented in the UserProcessor class, but all methods here only
    rely on the reservation_id (instead of relying on the session_id).
    The difference is that it will be possible to handle more than one
    concurrent reservation with the same session (which is desirable
    when using calendars), and it will be possible to provide a
    reservation_id (that can interact with the experiment) without
    compromising the rest of the session. """

    EXPIRATION_TIME_NOT_SET=-1234

    def __init__(self, cfg_manager, reservation_id, reservation_session, coordinator, locator, commands_store):
        self._cfg_manager            = cfg_manager
        self._reservation_session_id = reservation_id
        self._reservation_id         = reservation_id.id
        self._reservation_session    = reservation_session
        self._coordinator            = coordinator
        self._locator                = locator
        self._commands_store         = commands_store
        self.time_module             = time_module

        # The response to asynchronous commands is not immediately available, so we need to
        # use this map to store the ids of the usage objects (commands sent), identified through
        # their request_ids (which are not the same). As their responses become available, we will
        # use the request_ids to find the ids of the usage objects, and update them.
        #
        # It seems that the UserProcessor is re-created rather often, so we cannot store
        # usage-related information locally. We will store it in the session object instead.
        # TODO: As of now, if the async_commands_ids is not in session we will initialize it.
        # Probably that initialization should be moved to wherever session is initialized.
        if not "async_commands_ids" in self._reservation_session:
            self._reservation_session["async_commands_ids"] = {}

    def get_session(self):
        return self._reservation_session

    def get_reservation_session_id(self):
        return self._reservation_session_id

    def get_reservation_id(self):
        return self._reservation_id

    def get_info(self):
        return self._reservation_session['experiment_id']

    ##############################################################################
    #
    #
    #                     STATUS MANAGEMENT
    #
    #

    def get_status(self):
        """ get_status() -> Reservation

        It returns the state of the reservation (such as "you're waiting in a queue",
        "the experiment is being initialized", "you have the reservation available", etc.)
        """
        try:
            status = self._coordinator.get_reservation_status( self._reservation_id )
        except coord_exc.ExpiredSessionError as e:
            log.log(ReservationProcessor, log.level.Debug, "reason for rejecting:")
            log.log_exc(ReservationProcessor, log.level.Debug)
            human   = self._cfg_manager.get_doc_value(configuration_doc.CORE_UNIVERSAL_IDENTIFIER_HUMAN)
            core_id = self._cfg_manager.get_doc_value(configuration_doc.CORE_UNIVERSAL_IDENTIFIER)
            raise core_exc.NoCurrentReservationError("get_reservation_status at %s (%s) called but coordinator rejected reservation id (%s). Reason: %s" % (human, core_id, self._reservation_id, str(e)))
        else:
            if status.status == scheduling_status.WebLabSchedulingStatus.RESERVED_LOCAL:
                self.process_reserved_status(status)
            
            if status.status == scheduling_status.WebLabSchedulingStatus.RESERVED_REMOTE:
                self.process_reserved_remote_status(status)

            return Reservation.Reservation.translate_reservation( status )

    def process_reserved_status(self, status):
        if 'lab_session_id' in self._reservation_session:
            return # Already called in the past

        self._reservation_session['lab_session_id'] = status.lab_session_id
        self._reservation_session['lab_coordaddr']  = status.coord_address

        if status.exp_info.get('manages_polling', False):
            self.disable_polling()

        # TODO: it should not be time_module.time, but retrieve this information
        # from the status manager to know when it started
        self._renew_expiration_time( self.time_module.time() + status.time )

    def process_reserved_remote_status(self, status):
        self._reservation_session['federated'] = True

    def disable_polling(self):
        self._reservation_session['manages_polling'] = True

    def finish(self):
        """
        Called when the experiment ends, regardless of the way. (That is, it does not matter whether the user finished
        it explicitly or not).
        """

        # If already finished, exit
        if not self.is_polling():
            return

        self._stop_polling()
        self._reservation_session.pop('lab_session_id', None)
        try:
            self._coordinator.finish_reservation(self._reservation_id)
        except Exception as e:
            log.log( ReservationProcessor, log.level.Error, "Exception finishing reservation: %s" % e )
            log.log_exc( ReservationProcessor, log.level.Warning )
            raise core_exc.FailedToFreeReservationError( "There was an error freeing reservation: %s" % e)


    def update_latest_timestamp(self):
        """ Used in weblab.admin.monitor to check the status of current users """
        self._reservation_session['latest_timestamp'] = self._utc_timestamp()

    ##############################################################################
    #
    #
    #                     POLLING MANAGEMENT
    #
    #
    # Whenever the experiment finishes, the server notifies the Reservation
    # Processor. Polling is therefore only required to kick those users that
    # are not using the experiment for a long time.
    #
    # The variable is created when the reservation is created. It is removed
    # when the experiment finishes.
    #
    # TODO: the reservation system should tell the processor whether this
    # experiments expects polling or not.
    #

    def is_polling(self):
        """
        Is this user in a queue or using an experiment, and therefore it should be
        continuosly informing that it is alive? Otherwise, weblab will kick him.
        """

        return 'session_polling' in self._reservation_session

    def is_federated(self):
        return self._reservation_session.get('federated', False)

    def manages_polling(self):
        return self._reservation_session.get('manages_polling', False)

    def _renew_expiration_time(self, expiration_time):
        if self.is_polling():
            self._reservation_session['session_polling'] = (
                    self.time_module.time(),
                    expiration_time
                )

    def poll(self):

        """Inform that it is still online and interested on the reservation"""

        if not self.is_polling():
            raise core_exc.NoCurrentReservationError("poll called but no current reservation")

        latest_poll, expiration_time = self._reservation_session['session_polling']
        self._reservation_session['session_polling'] = (
                self.time_module.time(),
                expiration_time
            )

    def is_expired(self):

        """Did this reservation's user stay out for a long time without polling?"""
   
        # If it has been assigned to a laboratory that explicitly requests to avoid 
        # using polling, then it is only expired when the particular laboratory
        # states that it is expired.
        if self.manages_polling():
            return False

        # If it has been assigned in a foreign server, then, it is never expired
        if self.is_federated():
            return False

        # If it is not polling, it was expired in the past
        if not self.is_polling():
            return True

        #
        # But if it polling and it hasn't polled in some time
        #
        current_time = self.time_module.time()
        latest_poll, expiration_time = self._reservation_session['session_polling']
        if current_time - latest_poll > self._cfg_manager.get_value(EXPERIMENT_POLL_TIME, DEFAULT_EXPERIMENT_POLL_TIME):
            return True
        elif expiration_time != ReservationProcessor.EXPIRATION_TIME_NOT_SET and current_time > expiration_time:
            return True
        return False


    def _stop_polling(self):
        if self.is_polling():
            self._reservation_session.pop('session_polling')

    ##############################################################################
    #
    #
    #                     SENDING COMMANDS AND FILES
    #
    #########################
    #
    # Communications
    #

    def send_file(self, file_content, file_info ):
        #
        # Check that the reservation is enabled
        #
        lab_session_id = self._reservation_session.get('lab_session_id')
        lab_coordaddr  = self._reservation_session.get('lab_coordaddr')
        if lab_session_id is None or lab_coordaddr is None:
            raise core_exc.NoCurrentReservationError("send_file called but the reservation was not enabled")

        #
        # Retrieve the laboratory server
        #

        usage_file_sent = self._store_file(file_content, file_info)
        command_id_pack = self._append_file(usage_file_sent)
        try:
            laboratory_server = self._locator[lab_coordaddr]
            response = laboratory_server.send_file( lab_session_id, file_content, file_info )
            self._update_command_or_file(command_id_pack, response)
            return response
        except LaboratoryErrors.SessionNotFoundInLaboratoryServerError:
            self._update_command_or_file(command_id_pack, Command.Command("ERROR: SessionNotFound"))
            try:
                self.finish()
            except core_exc.FailedToFreeReservationError:
                pass
            raise core_exc.NoCurrentReservationError(
                'Experiment reservation expired'
            )
        except LaboratoryErrors.FailedToInteractError as ftie:
            self._update_command_or_file(command_id_pack, Command.Command("ERROR: " + str(ftie)))
            try:
                self.finish()
            except core_exc.FailedToFreeReservationError:
                pass
            raise core_exc.FailedToInteractError(
                    "Failed to send: %s" % ftie
                )


    def send_command(self, command):
        #
        # Check the that the experiment is enabled
        #
        lab_session_id = self._reservation_session.get('lab_session_id')
        lab_coordaddr  = self._reservation_session.get('lab_coordaddr')

        if lab_session_id is None or lab_coordaddr is None:
            raise core_exc.NoCurrentReservationError("send_command called but the reservation is not enabled")

        command_id_pack = self._append_command(command)
        try:
            laboratory_server = self._locator[lab_coordaddr]
            # We call the laboratory server's send_command, which will finally
            # get the command to be handled by the experiment.
            response = laboratory_server.send_command( lab_session_id, command )

            # The previous call was executed synchronously and we have
            # received the response. Before returning it, we will store it
            # locally so that we can log it.
            self._update_command_or_file(command_id_pack, response)

            return response

        except LaboratoryErrors.SessionNotFoundInLaboratoryServerError:
            self._update_command_or_file(command_id_pack, Command.Command("ERROR: SessionNotFound: None"))
            try:
                self.finish()
            except core_exc.FailedToFreeReservationError:
                pass
            raise core_exc.NoCurrentReservationError(
                'Experiment reservation expired'
            )
        except LaboratoryErrors.FailedToInteractError as ftspe:
            self._update_command_or_file(command_id_pack, Command.Command("ERROR: " + str(ftspe)))
            try:
                self.finish()
            except core_exc.FailedToFreeReservationError:
                pass

            raise core_exc.FailedToInteractError(
                    "Failed to send command: %s" % ftspe
                )


    def send_async_file(self, file_content, file_info ):
        """
        Sends a file asynchronously. Status of the request may be checked through
        check_async_command_status.

        @param file_content: Content of the file being sent
        @param file_info: File information of the file being sent
        @see check_async_command_status
        """

        lab_session_id = self._reservation_session.get('lab_session_id')
        lab_coordaddr  = self._reservation_session.get('lab_coordaddr')


        if lab_session_id is None or lab_coordaddr is None:
            raise core_exc.NoCurrentReservationError("send_async_file called but no current reservation")



        usage_file_sent = self._store_file(file_content, file_info)
        command_id_pack = self._append_file(usage_file_sent)
        try:
            laboratory_server = self._locator[lab_coordaddr]
            response = laboratory_server.send_async_file( lab_session_id, file_content, file_info )

            # TODO: how do we store async files? whenever somebody ask for the status? what if they don't ask for it?

            return response
        except LaboratoryErrors.SessionNotFoundInLaboratoryServerError:
            self._update_command_or_file(command_id_pack, Command.Command("ERROR: SessionNotFound: None"))
            try:
                self.finish()
            except core_exc.FailedToFreeReservationError:
                pass
            raise core_exc.NoCurrentReservationError(
                'Experiment reservation expired'
            )
        except LaboratoryErrors.FailedToInteractError as ftspe:
            self._update_command_or_file(command_id_pack, Command.Command("ERROR: " + str(ftspe)))
            try:
                self.finish()
            except core_exc.FailedToFreeReservationError:
                pass
            raise core_exc.FailedToInteractError(
                    "Failed to send file: %s" % ftspe
                )


    def check_async_command_status(self, request_identifiers):
        """
        Checks the status of several asynchronous commands. The request will be
        internally forwarded to the lab server. Standard async commands
        and file_send commands are treated in the same way.
        Commands reported as finished (either successfully or not) will be
        removed, so check_async_command_status should not be called on them again.
        Before removing the commands, it will also register their response for
        logging purposes.

        @param request_identifiers: List of the identifiers to check
        @return: Dictionary by request-id of tuples: (status, content)
        """

        lab_session_id = self._reservation_session.get('lab_session_id')
        lab_coordaddr  = self._reservation_session.get('lab_coordaddr')

        if lab_session_id is None or lab_coordaddr is None:
            raise core_exc.NoCurrentReservationError("check_async_command called but no current reservation")



        try:
            laboratory_server = self._locator[lab_coordaddr]
            response = laboratory_server.check_async_command_status( lab_session_id, request_identifiers)

            # Within the response map, we might now have the real response to one
            # (or more) async commands. We will update the usage object of the
            # command with its response, so that once the experiment ends it appears
            # in the log as expected.
            for req_id, (cmd_status, cmd_response) in response.items(): #@UnusedVariable
                if(req_id in self._reservation_session["async_commands_ids"]):
                    #usage_obj_id = self._reservation_session["async_commands_ids"][req_id]
                    # TODO: Bug here. async_commands_ids is empty.
                    # self._update_command_or_file(usage_obj_id, cmd_response)
                    pass

            return response

        except LaboratoryErrors.SessionNotFoundInLaboratoryServerError:
            # We did not find the specified session in the laboratory server.
            # We'll finish the experiment.
            #self._update_command(command_id_pack, Command.Command("ERROR: SessionNotFound: None"))
            try:
                self.finish()
            except core_exc.FailedToFreeReservationError:
                pass
            raise core_exc.NoCurrentReservationError(
                'Experiment reservation expired'
            )
        except LaboratoryErrors.FailedToInteractError as ftspe:
            # There was an error while trying to send the command.
            # We'll finish the experiment.
            #self._update_command(command_id_pack, Command.Command("ERROR: " + str(ftspe)))
            try:
                self.finish()
            except core_exc.FailedToFreeReservationError:
                pass

            raise core_exc.FailedToInteractError(
                    "Failed to send command: %s" % ftspe
                )


    def send_async_command(self, command):
        """
        Runs a command asynchronously. Status of the request may be checked
        through the check_async_command_status method.

        @param command The command to run
        @see check_async_command_status
        """

        lab_session_id = self._reservation_session.get('lab_session_id')
        lab_coordaddr  = self._reservation_session.get('lab_coordaddr')

        if lab_session_id is None or lab_coordaddr is None:
            raise core_exc.NoCurrentReservationError("send_async_command called but no current reservation")


        command_id_pack = self._append_command(command)

        try:
            laboratory_server = self._locator[lab_coordaddr]

            # We forward the request to the laboratory server, which
            # will forward it to the actual experiment. Because this is
            # an asynchronous call, we will not receive the actual response
            # to the command, but simply an ID identifying our request. This also
            # means that by the time this call returns, the real response to the
            # command is most likely not available yet.
            request_id = laboratory_server.send_async_command(lab_session_id, command)

            # If this was a standard, synchronous send_command, we would now store the response
            # we received, so that later, when the experiment finishes, the log is properly
            # written. However, the real response is not available yet, so we can't do that here.
            # Instead, we will store a reference to our usage object, so that we can later update it
            # when the response to the asynchronous command is ready.
            self._reservation_session["async_commands_ids"][request_id] = command_id_pack

            # TODO: when do we store async commands? whenever user asks for status? what if they don't ever ask?

            return request_id

        except LaboratoryErrors.SessionNotFoundInLaboratoryServerError:
            self._update_command_or_file(command_id_pack, Command.Command("ERROR: SessionNotFound: None"))
            try:
                self.finish()
            except core_exc.FailedToFreeReservationError:
                pass
            raise core_exc.NoCurrentReservationError(
                'Experiment reservation expired'
            )
        except LaboratoryErrors.FailedToInteractError as ftspe:
            self._update_command_or_file(command_id_pack, Command.Command("ERROR: " + str(ftspe)))
            try:
                self.finish()
            except core_exc.FailedToFreeReservationError:
                pass

            raise core_exc.FailedToInteractError(
                    "Failed to send command: %s" % ftspe
                )


    ##############################################################################
    #
    #
    #                     SENDING COMMANDS AND FILES
    #
    #########################
    #
    # Storage.
    # No reference to session, only to _reservation_id
    #

    def _append_command(self, command):
        return self._append_command_or_file(command, True)

    def _append_file(self, command):
        return self._append_command_or_file(command, False)

    def _append_command_or_file(self, command, command_or_file):
        command_id = random.randint(0, 1000 * 1000 * 1000)
        timestamp = self._utc_timestamp()
        command_entry = TemporalInformationStore.CommandOrFileInformationEntry(self._reservation_id, True, command_or_file, command_id, command, timestamp)
        self._commands_store.put(command_entry)
        return command_id, command_or_file


    def _update_command_or_file(self, (command_id, command_or_file), response):
        timestamp = self._utc_timestamp()
        command_entry = TemporalInformationStore.CommandOrFileInformationEntry(self._reservation_id, False, command_or_file, command_id, response, timestamp)
        self._commands_store.put(command_entry)

    def _utc_timestamp(self):
        return self.time_module.time()

    def _store_file(self, file_content, file_info):
        storer = FileStorer(self._cfg_manager, self._reservation_id, self.time_module)
        return storer.store_file(file_content, file_info)
