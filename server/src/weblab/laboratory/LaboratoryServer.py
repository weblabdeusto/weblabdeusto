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
# 

import re

import voodoo.log as log
import voodoo.LogLevel as LogLevel
from voodoo.log import logged
from voodoo.sessions.SessionChecker import check_session
import voodoo.sessions.SessionType as SessionType
import voodoo.gen.coordinator.CoordAddress as CoordAddress
import voodoo.gen.exceptions.exceptions as GeneratorExceptions

import weblab.exceptions.laboratory.LaboratoryExceptions as LaboratoryExceptions

from voodoo.gen.caller_checker import caller_check

import weblab.data.ServerType as ServerType
import weblab.data.experiments.ExperimentInstanceId as ExperimentInstanceId
import weblab.data.Command as Command

import weblab.laboratory.AssignedExperiments as AssignedExperiments
import weblab.laboratory.IsUpAndRunningHandler as IsUpAndRunningHandler

import voodoo.sessions.SessionManager as SessionManager

check_session_params = (
        LaboratoryExceptions.SessionNotFoundInLaboratoryServerException,
        "Laboratory Server"
    )


WEBLAB_LABORATORY_SERVER_SESSION_TYPE            = "laboratory_session_type"
DEFAULT_WEBLAB_LABORATORY_SERVER_SESSION_TYPE    = SessionType.Memory.name
WEBLAB_LABORATORY_SERVER_SESSION_POOL_ID         = "laboratory_session_pool_id"
DEFAULT_WEBLAB_LABORATORY_SERVER_SESSION_POOL_ID = "LaboratoryServer"
WEBLAB_LABORATORY_SERVER_ASSIGNED_EXPERIMENTS    = "laboratory_assigned_experiments"

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
    
    EXPERIMENT_IS_UP_AND_RUNNING_RESPONSE_CODE_OK    = 'OK'
    EXPERIMENT_IS_UP_AND_RUNNING_RESPONSE_CODE_ERROR = 'ER'
    EXPERIMENT_IS_UP_AND_RUNNING_RESPONSE_REGEX      = r"^(%s|%s) ?(.*)$" % (EXPERIMENT_IS_UP_AND_RUNNING_RESPONSE_CODE_OK, EXPERIMENT_IS_UP_AND_RUNNING_RESPONSE_CODE_ERROR)

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
                parsed_experiments.append( (experiment_instance_id, coord_address, checking_handlers) )
        return parsed_experiments

    def _load_assigned_experiments(self):
        self._assigned_experiments = AssignedExperiments.AssignedExperiments()
        parsed_experiments         = self._parse_assigned_experiments()
        for exp_inst_id, coord_address, checking_handlers in parsed_experiments:
            self._assigned_experiments.add_server(exp_inst_id, coord_address, checking_handlers)


    #####################################################
    # 
    # Experiments management
    # 

    @logged(LogLevel.Info)
    @caller_check(ServerType.UserProcessing)
    def do_reserve_experiment(self, experiment_instance_id):
        lab_sess_id = self._session_manager.create_session()
        try:
            experiment_coord_address = self._assigned_experiments.reserve_experiment(experiment_instance_id, lab_sess_id)
        except LaboratoryExceptions.BusyExperimentException, bee:
            # If it was already busy, free it and reserve it again
            try:
                old_lab_sess_id = self._assigned_experiments.get_lab_session_id(experiment_instance_id)
                self._free_experiment(old_lab_sess_id)
            except Exception, e:
                # If there is an error freeing the experiment, we don't want to propagate it to the User Processing Server:
                # our focus is to reserve the new session.
                log.log( LaboratoryServer, log.LogLevel.Warning, "Exception freeing already reserved experiment: %s" % e )
                log.log_exc(LaboratoryServer, log.LogLevel.Info)

            try:
                experiment_coord_address = self._assigned_experiments.reserve_experiment(experiment_instance_id, lab_sess_id)
            except LaboratoryExceptions.BusyExperimentException, bee:
                # The session might have expired and that's why this experiment is still reserved. Free it directly from
                # assigned_experiments.
                self._free_experiment_from_assigned_experiments(experiment_instance_id)
                experiment_coord_address = self._assigned_experiments.reserve_experiment(experiment_instance_id, lab_sess_id)

        self._session_manager.modify_session(lab_sess_id, {
                'experiment_instance_id'   : experiment_instance_id,
                'experiment_coord_address' : experiment_coord_address,
                'session_id' : lab_sess_id
            })

        experiment_server = self._locator.get_server_from_coordaddr(experiment_coord_address, ServerType.Experiment)
        experiment_server.start_experiment()

        return lab_sess_id

    @logged(LogLevel.Info)
    @caller_check(ServerType.UserProcessing)
    def do_free_experiment(self, lab_session_id):
        self._free_experiment(lab_session_id)

    def _free_experiment(self, lab_session_id):
        if not self._session_manager.has_session(lab_session_id):
            return

        session = self._session_manager.get_session_locking(lab_session_id)
        try:
            experiment_instance_id = session['experiment_instance_id']
            self._free_experiment_from_assigned_experiments(experiment_instance_id)
        finally:
            self._session_manager.delete_session_unlocking(lab_session_id)

    def _free_experiment_from_assigned_experiments(self, experiment_instance_id):
        try:
            self._assigned_experiments.free_experiment(experiment_instance_id)
        except LaboratoryExceptions.AlreadyFreedExperimentException, afee:
            return # Not a problem

        experiment_coord_address = self._assigned_experiments.get_coord_address(experiment_instance_id)
        experiment_server = self._locator.get_server_from_coordaddr(experiment_coord_address, ServerType.Experiment)
        experiment_server.dispose()

    @logged(LogLevel.Info)
    @caller_check(ServerType.UserProcessing)
    def do_experiment_is_up_and_running(self, experiment_instance_id):
        # Run the generic IsUpAndRunningHandlers
        handlers = self._assigned_experiments.get_is_up_and_running_handlers(experiment_instance_id)
        for h in handlers:
            h.run()
        # Run the Experiment's is_up_and_running() method, if exists
        experiment_coord_address = self._assigned_experiments.get_coord_address(experiment_instance_id)
        experiment_server = self._locator.get_server_from_coordaddr(experiment_coord_address, ServerType.Experiment)
        response = experiment_server.is_up_and_running()
        if response is not None:
            mo = re.match(self.EXPERIMENT_IS_UP_AND_RUNNING_RESPONSE_REGEX, response)
            if mo == None:
                raise LaboratoryExceptions.InvalidIsUpAndRunningResponseFormatException(
                            "Invalid response format from experiment's is_up_and_running() method. Expected: %s. Received: %s" %
                            ( self.EXPERIMENT_IS_UP_AND_RUNNING_RESPONSE_REGEX, response ) )
            else:
                code, details = mo.groups()
                if code == self.EXPERIMENT_IS_UP_AND_RUNNING_RESPONSE_CODE_OK:
                    pass
                elif code == self.EXPERIMENT_IS_UP_AND_RUNNING_RESPONSE_CODE_ERROR:
                    raise LaboratoryExceptions.ExperimentIsUpAndRunningErrorException("Reason: %s" % details)
                else:
                    raise RuntimeError("What? This just can't happen if re module works!")

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
        except Exception, e:
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
        except Exception, e:
            log.log( LaboratoryServer, log.LogLevel.Warning, "Exception sending command to experiment: %s" % e )
            log.log_exc(LaboratoryServer, log.LogLevel.Info)
            raise LaboratoryExceptions.FailedToSendCommandException("Couldn't send command: %s" % str(e))

        return Command.Command(str(response))