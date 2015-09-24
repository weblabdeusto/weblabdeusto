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
#         Jaime Irurzun <jaime.irurzun@gmail.com>
#         Luis Rodriguez <luis.rodriguez@opendeusto.es>
#
from __future__ import print_function, unicode_literals

import re
import traceback

import voodoo.log as log
from voodoo.log import logged
from voodoo.sessions.checker import check_session
import voodoo.sessions.session_type as SessionType
from voodoo.gen import CoordAddress
from voodoo.gen.exc import GeneratorError

from voodoo.threaded import threaded
import weblab.lab.async_request as AsyncRequest

import weblab.lab.exc as LaboratoryErrors

from voodoo.gen.caller_checker import caller_check

import weblab.data.server_type as ServerType
from weblab.data.experiments import ExperimentInstanceId
import weblab.data.command as Command

import weblab.core.coordinator.coordinator as Coordinator

import weblab.lab.assigned_experiments as AssignedExperiments
import weblab.lab.status_handler as IsUpAndRunningHandler

import weblab.experiment.level as ExperimentApiLevel

import voodoo.sessions.manager as SessionManager
from voodoo.sessions import generator as SessionGenerator
import json

check_session_params = (
        LaboratoryErrors.SessionNotFoundInLaboratoryServerError,
        "Laboratory Server"
    )


WEBLAB_LABORATORY_SERVER_SESSION_TYPE            = "laboratory_session_type"
DEFAULT_WEBLAB_LABORATORY_SERVER_SESSION_TYPE    = SessionType.Memory
WEBLAB_LABORATORY_SERVER_SESSION_POOL_ID         = "laboratory_session_pool_id"
DEFAULT_WEBLAB_LABORATORY_SERVER_SESSION_POOL_ID = "LaboratoryServer"
WEBLAB_LABORATORY_SERVER_ASSIGNED_EXPERIMENTS    = "laboratory_assigned_experiments"
WEBLAB_LABORATORY_EXCLUDE_CHECKING               = "laboratory_exclude_checking"
DEFAULT_WEBLAB_LABORATORY_EXCLUDE_CHECKING       = []

DEBUG = False

##########################################################
#
# The Laboratory Server is a proxy server between WebLab
# and the experiments. The main purpose is to provide
# low level features (such as encryption, low level
# protocols, etc.) to the experiment, through the WebLab
# stack.
#
class LaboratoryServer(object):

    # exp_inst_name|exp_name|exp_cat;coord_address
    EXPERIMENT_INSTANCE_ID_REGEX = r"^(.*)\:(.*)\@(.*)$"

    def __init__(self, coord_address, locator, cfg_manager, *args, **kwargs):
        """
        :param coord_address: Structure that identifies a concrete machine / server [correct? type?]
        :param locator: Registry through which we can get access to the ExperimentServer connectors. It
        is through this registry that we can actually send requests to the Experiment Servers.
        :param cfg_manager: Provides access to the experiment configuration
        :param args: [unused?]
        :param kwargs: [unused?]
        :return:
        """

        super(LaboratoryServer,self).__init__(*args, **kwargs)

        session_type    = cfg_manager.get_value(WEBLAB_LABORATORY_SERVER_SESSION_TYPE,
                                           DEFAULT_WEBLAB_LABORATORY_SERVER_SESSION_TYPE)
        session_pool_id = cfg_manager.get_value(WEBLAB_LABORATORY_SERVER_SESSION_POOL_ID,
                                           DEFAULT_WEBLAB_LABORATORY_SERVER_SESSION_POOL_ID)
        self._session_manager = SessionManager.SessionManager(
                cfg_manager,
                getattr(SessionType, session_type),
                session_pool_id
            )
        self._coord_address         = coord_address
        self._locator               = locator
        self._cfg_manager           = cfg_manager

        # This dictionary will be used to store the ongoing and not-yet-queried
        # async requests. They will be stored by session.
        # TODO: Consider refactoring this.
        self._async_requests = {}

        self._load_assigned_experiments()



    #######################################################
    #
    # Parse the configuration and load all the experiments
    # found. This task is executed at the beginning.
    #
    def _parse_assigned_experiments(self):
        """
        Parses the configuration that was provided to the server and loads every Experiment
        that is declared in it. This task is executed at the beginning.
        :return: List of tuples, each tuple containing information for an Experiment
        """

        assigned_experiments = self._cfg_manager.get_value(WEBLAB_LABORATORY_SERVER_ASSIGNED_EXPERIMENTS)

        parsed_experiments = []

        for experiment_instance_id, data in assigned_experiments.items():
            mo = re.match(self.EXPERIMENT_INSTANCE_ID_REGEX, experiment_instance_id)
            if mo == None:
                raise LaboratoryErrors.InvalidLaboratoryConfigurationError("Invalid configuration entry. Expected format: %s; found: %s" %
                    (LaboratoryServer.EXPERIMENT_INSTANCE_ID_REGEX, experiment_instance_id))
            else:
                number = data.get('number', 1)

                for n in range(1, number + 1):
                    # ExperimentInstanceId
                    groups = mo.groups()
                    (   exp_inst_name,
                        exp_name,
                        exp_cat_name
                    ) = groups

                    if number > 1:
                        exp_inst_name += '__%s' % n

                    experiment_instance_id = ExperimentInstanceId(exp_inst_name, exp_name, exp_cat_name)

                    # CoordAddress
                    try:
                        coord_address = CoordAddress.translate(data['coord_address'])
                    except GeneratorError:
                        raise LaboratoryErrors.InvalidLaboratoryConfigurationError("Invalid coordination address: %s" % data['coord_address'])

                    # CheckingHandlers
                    checkers = data.get('checkers', ())
                    checking_handlers = {}
                    for checker in checkers:
                        klazz = checker[0]
                        if klazz in IsUpAndRunningHandler.HANDLERS:
                            argss, kargss = (), {}
                            if len(checker) >= 3:
                                kargss = checker[2]
                            if len(checker) >= 2:
                                argss = checker[1]
                            checking_handlers[repr(checker)] = eval('IsUpAndRunningHandler.'+klazz)(*argss, **kargss)
                        else:
                            raise LaboratoryErrors.InvalidLaboratoryConfigurationError("Invalid IsUpAndRunningHandler: %s" % klazz)

                    # API
                    api = data.get('api', None)
                    
                    # Polling: if it manages its own polling, the client does not need to manage it
                    manages_polling = data.get('manages_polling', False)

                    parsed_experiments.append( (experiment_instance_id, coord_address, { 'checkers' : checking_handlers, 'api' : api, 'manages_polling' : manages_polling, 'number' : number }) )
        return parsed_experiments


    def _load_assigned_experiments(self):
        """
        Parses the experiments from the server config and loads them into the internal registry.
        :return: None
        """

        # Create the registry in which to store the Experiments.
        self._assigned_experiments = AssignedExperiments.AssignedExperiments()

        parsed_experiments         = self._parse_assigned_experiments()

        for exp_inst_id, coord_address, exp_info in parsed_experiments:
            self._assigned_experiments.add_server(exp_inst_id, coord_address, exp_info)

    #####################################################
    #
    # Experiments management
    #
    
    
    def _find_api(self, experiment_instance_id, experiment_coord_address = None):
        """
        _find_api(experiment_instance_id)
        
        Tries to retrieve the API version of the specified experiment.
        
        @param experiment_instance_id Experiment instance identifier for the experiment whose API 
        we want.
        @param experiment_coord_address Experiment coord address. May be None.
        @return API version, as a string. Will return the current API if for any reason
        it is unable to obtain the version.
        """
        
        # Check whether we know the API version already.
        api = self._assigned_experiments.get_api(experiment_instance_id)

        # If we don't know the API version yet, we will have to ask the experiment server itself
        if api is None:
            reported_api = self._get_experiment_api(experiment_instance_id)
            if reported_api is None:
                log.log( LaboratoryServer, log.level.Warning, "It was not possible to find out the api version of %r. Using current version as default."
                         % experiment_coord_address)
                if DEBUG:
                    print("[DBG] Was not possible to find out the api version of %r" % experiment_coord_address)
            else:
                # Remember the api version that we retrieved
                self._assigned_experiments.set_api(experiment_instance_id, reported_api)
                api = reported_api

        # If we don't know the api, we will use the current version as default.
        if api is None:
            api = ExperimentApiLevel.current
            self._assigned_experiments.set_api(experiment_instance_id, api)
            
        return api
    
    @logged(log.level.Info)
    @caller_check(ServerType.UserProcessing)
    def do_list_experiments(self):
        # TODO: this should return a list of elements such as:
        # [
        #      {
        #           'id'     : 'experiment_id1',
        #           'number' : 60,
        #      }
        # ]
        return []

    @logged(log.level.Info)
    @caller_check(ServerType.UserProcessing)
    def do_reserve_experiment(self, experiment_instance_id, client_initial_data, server_initial_data):
        lab_sess_id = self._session_manager.create_session()
        try:
            experiment_coord_address = self._assigned_experiments.reserve_experiment(experiment_instance_id, lab_sess_id)
        except LaboratoryErrors.BusyExperimentError:
            # If it was already busy, free it and reserve it again
            try:
                old_lab_sess_id = self._assigned_experiments.get_lab_session_id(experiment_instance_id)
                self._free_experiment(old_lab_sess_id)
            except Exception as e:
                # If there is an error freeing the experiment, we don't want to propagate it to the User Processing Server:
                # our focus is to reserve the new session.
                log.log( LaboratoryServer, log.level.Warning, "Exception freeing already reserved experiment: %s" % e )
                log.log_exc(LaboratoryServer, log.level.Info)

            try:
                experiment_coord_address = self._assigned_experiments.reserve_experiment(experiment_instance_id, lab_sess_id)
            except LaboratoryErrors.BusyExperimentError:
                # The session might have expired and that's why this experiment is still reserved. Free it directly from
                # assigned_experiments.
                self._free_experiment_from_assigned_experiments(experiment_instance_id, lab_sess_id)
                experiment_coord_address = self._assigned_experiments.reserve_experiment(experiment_instance_id, lab_sess_id)

        self._session_manager.modify_session(lab_sess_id, {
                'experiment_instance_id'   : experiment_instance_id,
                'experiment_coord_address' : experiment_coord_address,
                'session_id' : lab_sess_id
            })
        
        # Obtain the API of the experiment.
        api = self._find_api(experiment_instance_id, experiment_coord_address)

        experiment_server = self._locator[experiment_coord_address]

        if api == ExperimentApiLevel.level_1:
            experiment_server.start_experiment()
            experiment_server_response = "ok"
        elif api == ExperimentApiLevel.level_2:
            experiment_server_response = experiment_server.start_experiment(client_initial_data, server_initial_data)
        # If the API version is concurrent, we will also send the session id, to be able to identify the user for each request.
        elif api == ExperimentApiLevel.level_2_concurrent:
            experiment_server_response = experiment_server.start_experiment(lab_sess_id, client_initial_data, server_initial_data)
        else:
            # ERROR: Unrecognized version.
            experiment_server_response = experiment_server.start_experiment(lab_sess_id, client_initial_data, server_initial_data)

        experiment_info = {
            'address' : experiment_coord_address.address,
            'manages_polling' : self._assigned_experiments.manages_polling(experiment_instance_id),
        }

        return lab_sess_id, experiment_server_response, experiment_info


    @logged(log.level.Info)
    @caller_check(ServerType.UserProcessing)
    def do_free_experiment(self, lab_session_id):
        return self._free_experiment(lab_session_id)

    def _free_experiment(self, lab_session_id):
        if not self._session_manager.has_session(lab_session_id):
            return

        session = self._session_manager.get_session_locking(lab_session_id)
        finished = True
        experiment_response = None
        try:
            # Remove the async requests whose results we have not retrieved.
            # It seems that they might still be running when free gets called.
            # TODO: Consider possible issues.
            session_id = session['session_id']
            if session_id in self._async_requests:
                del self._async_requests[session_id]

            experiment_instance_id = session['experiment_instance_id']
            try:
                experiment_response = self._free_experiment_from_assigned_experiments(experiment_instance_id, lab_session_id)
            except Exception as e:
                log.log( LaboratoryServer, log.level.Error, "Exception freeing experiment" % e )
                log.log_exc(LaboratoryServer, log.level.Error)
                experiment_response = ''

            if experiment_response is not None and experiment_response.lower() != 'ok' and experiment_response != '':
                try:
                    response = json.loads(experiment_response)
                    finished = response.get(Coordinator.FINISH_FINISHED_MESSAGE)
                except:
                    traceback.print_exc()
        finally:
            if finished:
                self._session_manager.delete_session_unlocking(lab_session_id)
            else:
                self._session_manager.modify_session_unlocking(lab_session_id, session)
            return experiment_response

    def _free_experiment_from_assigned_experiments(self, experiment_instance_id, lab_session_id ):
        """
        _free_experiment_from_assigned_experiments(lab_session_id, experiment_instance_id)
        
        Frees the experiment, calling the appropriate dispose on it.
        @param lab_session_id To identify the user
        @param experiment_instance_id To identify the experiment instance
        """
        experiment_coord_address = self._assigned_experiments.get_coord_address(experiment_instance_id)
        experiment_server = self._locator[experiment_coord_address]
        
        # Find out which api we're supposed to use
        api = self._assigned_experiments.get_api(experiment_instance_id)
        
        if api == ExperimentApiLevel.level_1:
            # First version. Can't return information through dispose.
            experiment_server.dispose()
            return "ok"
        elif api == ExperimentApiLevel.level_2:
            # Second version. Result of dispose is reported.
            return experiment_server.dispose()
        elif api == ExperimentApiLevel.level_2_concurrent:
            # Concurrent version of the second version. The sessionid is provided
            # so that the client may be identified.
            return experiment_server.dispose(lab_session_id)
        else:
            # TODO: Error: Unrecognized version
            return experiment_server.dispose()

    @logged(log.level.Info)
    def _get_experiment_api(self, experiment_instance_id):
        """
        _get_experiment_api(experiment_instance_id) -> api

        Retrieves the API version of the specified experiment instance (which will generally be the same
        for every experiment of the same kind).

        @param experiment_instance_id The id of the experiment instance whose API to retrieve
        @return The API version, or None if an error occurred or it wasn't possible to retrieve the version.
        """
        try:
            experiment_coord_address = self._assigned_experiments.get_coord_address(experiment_instance_id)
            experiment_server = self._locator[experiment_coord_address]

            reported_api = experiment_server.get_api()
        except:
            # get_api failed, test if the server is online
            try:
                experiment_coord_address = self._assigned_experiments.get_coord_address(experiment_instance_id)
                self._locator[experiment_coord_address]
                # it is online! check the get_api
                try:
                    reported_api = experiment_server.get_api()
                except:
                    # Failed again to get_api, but test had previously worked?
                    # Then it is probably using the version 1,
                    # where the get_api method was not supported
                    reported_api = ExperimentApiLevel.level_1
            except:
                # It's not online. No get_api.
                reported_api = None

        return reported_api


    @logged(log.level.Info)
    @caller_check(ServerType.UserProcessing)
    def do_check_experiments_resources(self):
        """Are the resources that the assigned experiment servers use working? It does not matter if this
        experiment is being used or not, this method will only check things like certain IP addresses replying,
        webcams returning valid images, or the experiment server returning correctly on test_me.
        """
        experiment_instance_ids = self._assigned_experiments.list_experiment_instance_ids()
        failing_experiment_instance_ids = {
                # experiment_instance_id : error_message
            }

        exclude_checking = self._cfg_manager.get_value(WEBLAB_LABORATORY_EXCLUDE_CHECKING, DEFAULT_WEBLAB_LABORATORY_EXCLUDE_CHECKING)

        all_handlers = {
            # checker_repr : ( checker, [ experiment_instance_id1, experiment_instance_id2, ... ])
        }

        for experiment_instance_id in experiment_instance_ids:
            if experiment_instance_id.to_weblab_str() in exclude_checking:
                continue # Exclude experiment

            handlers = self._assigned_experiments.get_is_up_and_running_handlers(experiment_instance_id)
            # handlers is a dict as:
            # {
            #    checker_repr : checker
            # }
            # 
            for handler_repr in handlers:
                if handler_repr in all_handlers:
                    checker, experiment_instances = all_handlers[handler_repr]
                    experiment_instances.append(experiment_instance_id)
                else:
                    all_handlers[handler_repr] = (handlers[handler_repr], [ experiment_instance_id ])

            # Try to call the WebLab service
            experiment_coord_address = self._assigned_experiments.get_coord_address(experiment_instance_id)
            self._checking_component = experiment_coord_address
            try:
                self._locator.check_component(experiment_coord_address)
            except Exception as e:
                failing_experiment_instance_ids[experiment_instance_id] = str(e)
                self.log_error(experiment_instance_id, str(e))
            self._checking_component = None

        # In VISIR, for instance, there might be 60 or 80 handlers pointing to the same server. There
        # is no need to contact that server so many times. So we collect all the checkers and run only
        # once each unique checker.
        for checker, experiment_instance_ids in all_handlers.values():
            self._checking_handlers = (checker, experiment_instance_ids)
            handler_messages = checker.run_times()
            self._checking_handlers = None

            if len(handler_messages) > 0:
                error_message = '; '.join(handler_messages)
                for experiment_instance_id in experiment_instance_ids:
                    current_error_message = error_message
                    if experiment_instance_id in failing_experiment_instance_ids:
                        current_error_message += '; ' + failing_experiment_instance_ids[experiment_instance_id]
                    failing_experiment_instance_ids[experiment_instance_id] = current_error_message
                    self.log_error(experiment_instance_id, current_error_message)

        return failing_experiment_instance_ids

    def log_error(self, experiment_instance_id, error_message):
        log.log(
            LaboratoryServer,
            log.level.Warning,
            "Exception testing experiment %s: %s" % (experiment_instance_id, error_message)
        )

    @logged(log.level.Info)
    @caller_check(ServerType.UserProcessing)
    def do_experiment_is_up_and_running(self, experiment_instance_id):
        """Does the experiment server consider that the experiment is up and running? This method will only
        be called by the coordinator whenever there is an available slot, so the experiment server can
        perform a test knowing that it is not going to be interrupted."""
        api = self._assigned_experiments.get_api(experiment_instance_id)
        if api == ExperimentApiLevel.level_1:
            return (0, '') # No way to know this information; don't ask again
        else:
            experiment_coord_address = self._assigned_experiments.get_coord_address(experiment_instance_id)
            experiment_server = self._locator[experiment_coord_address]
            return experiment_server.is_up_and_running()

    @logged(log.level.Info)
    @check_session(*check_session_params)
    @caller_check(ServerType.UserProcessing)
    def do_should_experiment_finish(self, session):
        """Does the experiment server consider that it should finish current session?"""
        experiment_instance_id   = session['experiment_instance_id']
        api = self._assigned_experiments.get_api(experiment_instance_id)
        if api == ExperimentApiLevel.level_1:
            return 0 # No way to know this information: don't ask again
        else:
            experiment_coord_address = session['experiment_coord_address']
            experiment_server = self._locator[experiment_coord_address]
            api = self._assigned_experiments.get_api(experiment_instance_id)
            if api == ExperimentApiLevel.level_2_concurrent:
                lab_session_id = session['session_id']
                return experiment_server.should_finish(lab_session_id)
            else:
                return experiment_server.should_finish()

    #
    # TODO
    # If an experiment can handle multiple users, then
    # we'll have a coord_address with multiple uses,
    # so this method might not actually be not be useful
    #
    @logged(log.level.Info)
    @check_session(*check_session_params)
    @caller_check(ServerType.UserProcessing)
    def do_resolve_experiment_address(self, session):
        experiment_instance_id = session['experiment_instance_id']
        return self._assigned_experiments.get_coord_address(experiment_instance_id)

    #####################################################
    #
    # Experiments interaction
    #

    @logged(log.level.Info,except_for=(('file_content',2),))
    @check_session(*check_session_params)
    @caller_check(ServerType.UserProcessing)
    def do_send_file(self, session, file_content, file_info):
        
        lab_session_id = session['session_id']
        experiment_instance_id = session['experiment_instance_id']
        api = self._assigned_experiments.get_api(experiment_instance_id)
        
        experiment_coord_address = session['experiment_coord_address']
        experiment_server = self._locator[experiment_coord_address]

        try:
            if api.endswith("concurrent"):
                response = experiment_server.send_file_to_device(lab_session_id, file_content, file_info)
            else:
                response = experiment_server.send_file_to_device(file_content, file_info)
        except Exception as e:
            log.log( LaboratoryServer, log.level.Warning, "Exception sending file to experiment: %s" % e )
            log.log_exc(LaboratoryServer, log.level.Info)
            raise LaboratoryErrors.FailedToSendFileError("Couldn't send file: %s" % str(e))

        return Command.Command(str(response))

    @logged(log.level.Info)
    @check_session(*check_session_params)
    @caller_check(ServerType.UserProcessing)
    def do_send_command(self, session, command):
        
        lab_session_id = session['session_id']
        experiment_instance_id = session['experiment_instance_id']
        api = self._assigned_experiments.get_api(experiment_instance_id)
        
        experiment_coord_address = session['experiment_coord_address']
        experiment_server = self._locator[experiment_coord_address]

        try:
            if api.endswith("concurrent"):
                response = experiment_server.send_command_to_device(lab_session_id, command.get_command_string())
            else:
                response = experiment_server.send_command_to_device(command.get_command_string())
        except Exception as e:
            log.log( LaboratoryServer, log.level.Warning, "Exception sending command to experiment: %s" % e )
            log.log_exc(LaboratoryServer, log.level.Info)
            raise LaboratoryErrors.FailedToSendCommandError("Couldn't send command: %s" % str(e))

        return Command.Command(str(response))


    @logged(log.level.Info)
    @threaded()
    def _send_async_file_t(self, session, file_content, file_info):
        """
        This method is used for asynchronously calling the experiment server's
        send_file_to_device, and for that purpose runs on its own thread.
        This implies that its response will arrive asynchronously to the client.
        """
        
        lab_session_id = session['session_id']
        experiment_instance_id = session['experiment_instance_id']
        api = self._assigned_experiments.get_api(experiment_instance_id)
        
        experiment_coord_address = session['experiment_coord_address']
        experiment_server = self._locator[experiment_coord_address]

        try:
            if api.endswith("concurrent"):
                response = experiment_server.send_file_to_device(lab_session_id, file_content, file_info)
            else:
                response = experiment_server.send_file_to_device(file_content, file_info)
        except Exception as e:
            log.log( LaboratoryServer, log.level.Warning, "Exception sending async file to experiment: %s" % e )
            log.log_exc(LaboratoryServer, log.level.Info)
            raise LaboratoryErrors.FailedToSendFileError("Couldn't send async file: %s" % str(e))

        return Command.Command(str(response))


    @logged(log.level.Info,except_for=(('file_content',2),))
    @check_session(*check_session_params)
    @caller_check(ServerType.UserProcessing)
    def do_send_async_file(self, session, file_content, file_info):
        """
        Runs the experiment server's send_file_to_device asynchronously, by running the
        call on its own thread and storing the result, to be returned through the
        check_async_command_status request.

        @param session: Session
        @param request_identifiers: List of request identifiers whose status to check.
        @return A dictionary with each request identifier as key and a (status, contents) tuple as values.
        The status can either be "ok", if the request is done, "error", if it failed, and "running", if it
        has not finished yet. In the first two cases, contents will return the response.
        """

        # Call the async method which will run on its own thread. Store the object
        # it returns, so that we can know whether it has finished.
        threadobj = self._send_async_file_t(session, file_content, file_info)

        # Create a new identifier for the new request
        # TODO: Consider refactoring this
        gen = SessionGenerator.SessionGenerator()
        request_id = gen.generate_id(16)

        # Store the new request in our dictionary
        session_id = session['session_id']
        if(session_id not in self._async_requests):
            self._async_requests[session_id] = {}
        self._async_requests[session_id][request_id] = threadobj

        return request_id


    @logged(log.level.Info)
    @check_session(*check_session_params)
    @caller_check(ServerType.UserProcessing)
    def do_check_async_command_status(self, session, request_identifiers):
        """
        Checks the status of several asynchronous commands.
        Note that at this respect there is no difference between a standard async command and an async send_file.
        This method will work for either, and request_identifiers of both types can be mixed freely.
        Requests reported as finished (either successfully or not) will be removed.

        @param session: Session
        @param request_identifiers: List of request identifiers whose status to check.
        @return A dictionary with each request identifier as key and a (status, contents) tuple as values.
        The status can either be "ok", if the request is done, "error", if it failed, and "running", if it
        has not finished yet. In the first two cases, contents will return the response.
        """

        session_id = session['session_id']
        if(session_id not in self._async_requests):
            self._async_requests[session_id] = {}

        # Build and return a dictionary with information about the status of every
        # specified async command.
        response = {}
        for req_id in request_identifiers:

            # If one of the specified request ids does not seem to exist, we
            # will simply ignore it and return nothing about it. We will handle
            # the remaining request ids normally.
            # TODO: Consider whether doing this is appropriate.
            if( req_id not in self._async_requests[session_id] ):
                continue

            req = self._async_requests[session_id][req_id]

            status = None
            contents = None

            if(req.raised_exc is not None):
                status = AsyncRequest.STATUS_ERROR
                contents = str(req.raised_exc)
                del self._async_requests[session_id][req_id]
            elif(req.finished_ok == True):
                status = AsyncRequest.STATUS_OK
                contents = req.result.get_command_string()
                del self._async_requests[session_id][req_id]
            else:
                status = AsyncRequest.STATUS_RUNNING


            response[req_id] = (status, contents)

        return response

    @logged(log.level.Info)
    @threaded()
    def _send_async_command_t(self, session, command):
        """
        This method is used for asynchronously calling the experiment server's
        send_command_to_device, and for that purpose runs on its own thread.
        This implies that its response will arrive asynchronously to the client.
        """
        
        lab_session_id = session['session_id']
        experiment_instance_id = session['experiment_instance_id']
        api = self._assigned_experiments.get_api(experiment_instance_id)
        
        experiment_coord_address = session['experiment_coord_address']
        experiment_server = self._locator[experiment_coord_address]

        try:
            if api.endswith("concurrent"):
                response = experiment_server.send_command_to_device(lab_session_id, command.get_command_string())
            else:
                response = experiment_server.send_command_to_device(command.get_command_string())
        except Exception as e:
            log.log( LaboratoryServer, log.level.Warning, "Exception sending async command to experiment: %s" % e )
            log.log_exc(LaboratoryServer, log.level.Info)
            raise LaboratoryErrors.FailedToSendCommandError("Couldn't send async command: %s" % str(e))

        return Command.Command(str(response))

    @logged(log.level.Info)
    @check_session(*check_session_params)
    @caller_check(ServerType.UserProcessing)
    def do_send_async_command(self, session, command):
        """
        Runs the experiment server's send_command_to_device asynchronously, by running the
        call on its own thread and storing the result, to be returned through the
        check_async_command_status request.

        @param session: Session
        @param command: Command to execute asynchronously
        """

        # Call the async method which will run on its own thread. Store the object
        # it returns, so that we can know whether it has finished.
        threadobj = self._send_async_command_t(session, command)

        # Create a new identifier for the new request
        # TODO: Consider refactoring this
        gen = SessionGenerator.SessionGenerator()
        request_id = gen.generate_id(16)

        # Store the new request in our dictionary
        session_id = session['session_id']
        if(session_id not in self._async_requests):
            self._async_requests[session_id] = {}
        self._async_requests[session_id][request_id] = threadobj

        return request_id
