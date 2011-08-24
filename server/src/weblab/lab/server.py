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
#         Jaime Irurzun <jaime.irurzun@gmail.com>
#         Luis Rodriguez <luis.rodriguez@opendeusto.es>
# 

import re

import voodoo.log as log
import voodoo.LogLevel as LogLevel
from voodoo.log import logged
from voodoo.sessions.checker import check_session
import voodoo.sessions.SessionType as SessionType
import voodoo.gen.coordinator.CoordAddress as CoordAddress
import voodoo.gen.exceptions.exceptions as GeneratorExceptions

from voodoo.threaded import threaded
import weblab.lab.async_request as AsyncRequest

import weblab.lab.exc as LaboratoryExceptions

from voodoo.gen.caller_checker import caller_check

import weblab.data.ServerType as ServerType
import weblab.data.experiments.ExperimentInstanceId as ExperimentInstanceId
import weblab.data.Command as Command

import weblab.core.coordinator.coordinator as Coordinator

import weblab.lab.assigned_experiments as AssignedExperiments
import weblab.lab.status_handler as IsUpAndRunningHandler

import weblab.experiment.level as ExperimentApiLevel

import voodoo.sessions.manager as SessionManager
from voodoo.sessions import SessionGenerator
import json

check_session_params = (
        LaboratoryExceptions.SessionNotFoundInLaboratoryServerException,
        "Laboratory Server"
    )


WEBLAB_LABORATORY_SERVER_SESSION_TYPE            = "laboratory_session_type"
DEFAULT_WEBLAB_LABORATORY_SERVER_SESSION_TYPE    = SessionType.Memory
WEBLAB_LABORATORY_SERVER_SESSION_POOL_ID         = "laboratory_session_pool_id"
DEFAULT_WEBLAB_LABORATORY_SERVER_SESSION_POOL_ID = "LaboratoryServer"
WEBLAB_LABORATORY_SERVER_ASSIGNED_EXPERIMENTS    = "laboratory_assigned_experiments"
WEBLAB_LABORATORY_EXCLUDE_CHECKING               = "laboratory_exclude_checking"
DEFAULT_WEBLAB_LABORATORY_EXCLUDE_CHECKING       = []


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
        assigned_experiments = self._cfg_manager.get_value(WEBLAB_LABORATORY_SERVER_ASSIGNED_EXPERIMENTS)

        parsed_experiments = []

        for experiment_instance_id, data in assigned_experiments.items():
            mo = re.match(self.EXPERIMENT_INSTANCE_ID_REGEX, experiment_instance_id)
            if mo == None:
                raise LaboratoryExceptions.InvalidLaboratoryConfigurationException("Invalid configuration entry. Expected format: %s; found: %s" % 
                    (LaboratoryServer.EXPERIMENT_INSTANCE_ID_REGEX, experiment_instance_id))
            else:
                # ExperimentInstanceId
                groups = mo.groups()
                (   exp_inst_name,
                    exp_name,
                    exp_cat_name
                ) = groups
                experiment_instance_id = ExperimentInstanceId.ExperimentInstanceId(exp_inst_name, exp_name, exp_cat_name)

                # CoordAddress
                try:
                    coord_address = CoordAddress.CoordAddress.translate_address(data['coord_address'])
                except GeneratorExceptions.GeneratorException:
                    raise LaboratoryExceptions.InvalidLaboratoryConfigurationException("Invalid coordination address: %s" % data['coord_address'])
                
                # CheckingHandlers
                checkers = data.get('checkers', ())
                checking_handlers = []
                for checker in checkers:
                    klazz = checker[0]
                    if klazz in IsUpAndRunningHandler.HANDLERS:
                        argss, kargss = (), {}
                        if len(checker) >= 3:
                            kargss = checker[2]
                        if len(checker) >= 2:
                            argss = checker[1]
                        checking_handlers.append(eval('IsUpAndRunningHandler.'+klazz)(*argss, **kargss))
                    else:
                        raise LaboratoryExceptions.InvalidLaboratoryConfigurationException("Invalid IsUpAndRunningHandler: %s" % klazz)

                api = data.get('api', 'current')
                if not ExperimentApiLevel.is_level(api):
                    raise LaboratoryExceptions.InvalidLaboratoryConfigurationException("Invalid api: %s. See %s" % (api, ExperimentApiLevel.__file__))

                if not ExperimentApiLevel.is_supported(api):
                    raise LaboratoryExceptions.InvalidLaboratoryConfigurationException("Unsupported api: %s" % api)

                parsed_experiments.append( (experiment_instance_id, coord_address, checking_handlers, ExperimentApiLevel.get_level(api)) )
        return parsed_experiments

    def _load_assigned_experiments(self):
        self._assigned_experiments = AssignedExperiments.AssignedExperiments()
        parsed_experiments         = self._parse_assigned_experiments()
        for exp_inst_id, coord_address, checking_handlers, api in parsed_experiments:
            self._assigned_experiments.add_server(exp_inst_id, coord_address, checking_handlers, api)


    #####################################################
    # 
    # Experiments management
    # 

    @logged(LogLevel.Info)
    @caller_check(ServerType.UserProcessing)
    def do_reserve_experiment(self, experiment_instance_id, client_initial_data, server_initial_data):
        lab_sess_id = self._session_manager.create_session()
        try:
            experiment_coord_address = self._assigned_experiments.reserve_experiment(experiment_instance_id, lab_sess_id)
        except LaboratoryExceptions.BusyExperimentException:
            # If it was already busy, free it and reserve it again
            try:
                old_lab_sess_id = self._assigned_experiments.get_lab_session_id(experiment_instance_id)
                self._free_experiment(old_lab_sess_id)
            except Exception as e:
                # If there is an error freeing the experiment, we don't want to propagate it to the User Processing Server:
                # our focus is to reserve the new session.
                log.log( LaboratoryServer, log.LogLevel.Warning, "Exception freeing already reserved experiment: %s" % e )
                log.log_exc(LaboratoryServer, log.LogLevel.Info)

            try:
                experiment_coord_address = self._assigned_experiments.reserve_experiment(experiment_instance_id, lab_sess_id)
            except LaboratoryExceptions.BusyExperimentException:
                # The session might have expired and that's why this experiment is still reserved. Free it directly from
                # assigned_experiments.
                self._free_experiment_from_assigned_experiments(experiment_instance_id)
                experiment_coord_address = self._assigned_experiments.reserve_experiment(experiment_instance_id, lab_sess_id)

        self._session_manager.modify_session(lab_sess_id, {
                'experiment_instance_id'   : experiment_instance_id,
                'experiment_coord_address' : experiment_coord_address,
                'session_id' : lab_sess_id
            })

        api = self._assigned_experiments.get_api(experiment_instance_id)

        experiment_server = self._locator.get_server_from_coordaddr(experiment_coord_address, ServerType.Experiment)

        if api == ExperimentApiLevel.level_1:
            experiment_server.start_experiment()
            experiment_server_response = "ok"
        else:
            experiment_server_response = experiment_server.start_experiment(client_initial_data, server_initial_data)

        return lab_sess_id, experiment_server_response, experiment_coord_address.address

    @logged(LogLevel.Info)
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
            if( self._async_requests.has_key(session_id) ):
                del self._async_requests[session_id]
            
            experiment_instance_id = session['experiment_instance_id']
            experiment_response = self._free_experiment_from_assigned_experiments(experiment_instance_id)
            if experiment_response is not None and experiment_response != 'ok' and experiment_response != '':
                try:
                    response = json.loads(experiment_response)
                    finished = response.get(Coordinator.FINISH_FINISHED_MESSAGE)
                except:
                    import traceback
                    traceback.print_exc()
        finally:
            if finished:
                self._session_manager.delete_session_unlocking(lab_session_id)
            else:
                self._session_manager.modify_session_unlocking(lab_session_id, session)
            return experiment_response

    def _free_experiment_from_assigned_experiments(self, experiment_instance_id):
        experiment_coord_address = self._assigned_experiments.get_coord_address(experiment_instance_id)
        experiment_server = self._locator.get_server_from_coordaddr(experiment_coord_address, ServerType.Experiment)
        api = self._assigned_experiments.get_api(experiment_instance_id)
        return_value = experiment_server.dispose()
        if api == ExperimentApiLevel.level_1:
            return "ok"
        else:
            return return_value


    @logged(LogLevel.Info)
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
        
        for experiment_instance_id in experiment_instance_ids:
            if experiment_instance_id.to_weblab_str() in exclude_checking:
                continue # Exclude experiment

            handlers = self._assigned_experiments.get_is_up_and_running_handlers(experiment_instance_id)
            error_messages = []
            for h in handlers:
                handler_messages = h.run_times()
                error_messages.extend(handler_messages)

            if len(error_messages) > 0:
                error_message = '; '.join(error_messages)
                failing_experiment_instance_ids[experiment_instance_id] = error_message
                self.log_error(experiment_instance_id, error_message)
            else: 
                # No error yet, so probably the host is up and running; try to call the WebLab service
                experiment_coord_address = self._assigned_experiments.get_coord_address(experiment_instance_id)
                try:
                    self._locator.check_server_at_coordaddr(experiment_coord_address, ServerType.Experiment)
                except Exception as e:
                    failing_experiment_instance_ids[experiment_instance_id] = str(e)
                    self.log_error(experiment_instance_id, str(e))

        return failing_experiment_instance_ids

    def log_error(self, experiment_instance_id, error_message):
        log.log(
            LaboratoryServer,
            LogLevel.Warning,
            "Exception testing experiment %s: %s" % (experiment_instance_id, error_message)
        )

    @logged(LogLevel.Info)
    @caller_check(ServerType.UserProcessing)
    def do_experiment_is_up_and_running(self, experiment_instance_id):
        """Does the experiment server consider that the experiment is up and running? This method will only
        be called by teh coordinator whenever there is an available slot, so the experiment server can 
        perform a test knowing that it is not going to be interrupted."""
        experiment_coord_address = self._assigned_experiments.get_coord_address(experiment_instance_id)
        self._locator.get_server_from_coordaddr(experiment_coord_address, ServerType.Experiment)

    # 
    # TODO
    # If an experiment can handle multiple users, then
    # we'll have a coord_address with multiple uses,
    # so this method might not actually be not be useful
    # 
    @logged(LogLevel.Info)
    @check_session(*check_session_params)
    @caller_check(ServerType.UserProcessing)
    def do_resolve_experiment_address(self, session):
        experiment_instance_id = session['experiment_instance_id']
        return self._assigned_experiments.get_coord_address(experiment_instance_id)

    #####################################################
    # 
    # Experiments interaction
    # 

    @logged(LogLevel.Info,except_for=(('file_content',2),))
    @check_session(*check_session_params)
    @caller_check(ServerType.UserProcessing)
    def do_send_file(self, session, file_content, file_info):
        experiment_coord_address = session['experiment_coord_address']
        experiment_server = self._locator.get_server_from_coordaddr(experiment_coord_address, ServerType.Experiment)
        
        try:
            response = experiment_server.send_file_to_device(file_content, file_info)
        except Exception as e:
            log.log( LaboratoryServer, log.LogLevel.Warning, "Exception sending file to experiment: %s" % e )
            log.log_exc(LaboratoryServer, log.LogLevel.Info)
            raise LaboratoryExceptions.FailedToSendFileException("Couldn't send file: %s" % str(e))

        return Command.Command(str(response))

    @logged(LogLevel.Info)
    @check_session(*check_session_params)
    @caller_check(ServerType.UserProcessing)
    def do_send_command(self, session, command):
        experiment_coord_address = session['experiment_coord_address']
        experiment_server = self._locator.get_server_from_coordaddr(experiment_coord_address, ServerType.Experiment)
        
        try:
            response = experiment_server.send_command_to_device(command.get_command_string())
        except Exception as e:
            log.log( LaboratoryServer, log.LogLevel.Warning, "Exception sending command to experiment: %s" % e )
            log.log_exc(LaboratoryServer, log.LogLevel.Info)
            raise LaboratoryExceptions.FailedToSendCommandException("Couldn't send command: %s" % str(e))

        return Command.Command(str(response))
    
    
    @logged(LogLevel.Info)
    @threaded()
    def _send_async_file_t(self, session, file_content, file_info):
        """
        This method is used for asynchronously calling the experiment server's 
        send_file_to_device, and for that purpose runs on its own thread.
        This implies that its response will arrive asynchronously to the client.
        """
        experiment_coord_address = session['experiment_coord_address']
        experiment_server = self._locator.get_server_from_coordaddr(experiment_coord_address, ServerType.Experiment)
        
        try:
            response = experiment_server.send_file_to_device(file_content, file_info)
        except Exception as e:
            log.log( LaboratoryServer, log.LogLevel.Warning, "Exception sending async file to experiment: %s" % e )
            log.log_exc(LaboratoryServer, log.LogLevel.Info)
            raise LaboratoryExceptions.FailedToSendFileException("Couldn't send async file: %s" % str(e))

        return Command.Command(str(response))
    

    @logged(LogLevel.Info,except_for=(('file_content',2),))
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


    @logged(LogLevel.Info)
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
    
    @logged(LogLevel.Info)
    @threaded()
    def _send_async_command_t(self, session, command):
        """
        This method is used for asynchronously calling the experiment server's 
        send_command_to_device, and for that purpose runs on its own thread.
        This implies that its response will arrive asynchronously to the client.
        """
        experiment_coord_address = session['experiment_coord_address']
        experiment_server = self._locator.get_server_from_coordaddr(experiment_coord_address, ServerType.Experiment)
        
        try:
            response = experiment_server.send_command_to_device(command.get_command_string())
        except Exception as e:
            log.log( LaboratoryServer, log.LogLevel.Warning, "Exception sending async command to experiment: %s" % e )
            log.log_exc(LaboratoryServer, log.LogLevel.Info)
            raise LaboratoryExceptions.FailedToSendCommandException("Couldn't send async command: %s" % str(e))

        return Command.Command(str(response))

    @logged(LogLevel.Info)
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
