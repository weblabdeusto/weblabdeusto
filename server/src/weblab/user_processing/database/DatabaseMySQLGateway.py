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

import datetime
import calendar

from voodoo.log import logged

import voodoo.gen.coordinator.CoordAddress as CoordAddress

from weblab.database.DatabaseConstants import READ, WRITE, NAME
from weblab.database.DatabaseConstants import SELECT, INSERT

import weblab.exceptions.database.DatabaseExceptions as DbExceptions

import weblab.user_processing.database.dao.User as dao_User
import weblab.user_processing.database.dao.Group as dao_Group
import weblab.user_processing.database.dao.Permission as dao_Permission

import weblab.data.Command as Command
import weblab.data.experiments.Experiment as Experiment
import weblab.data.experiments.ExperimentAllowed as ExperimentAllowed
import weblab.data.experiments.Category as ExperimentCategory
import weblab.data.experiments.Usage as Usage
import weblab.data.experiments.ExperimentId as ExperimentId
import weblab.database.DatabaseMySQLGateway as dbMySQLGateway
from weblab.database.DatabaseMySQLGateway import _db_credentials_checker

#TODO: where should this class be placed?
class Permissions:
    experiment_allowed = 'experiment_allowed'

#TODO: capture MySQL Exceptions!!!

MAX_VALUES_PER_USER_USED_EXPERIMENT_QUERY_NAME    = 'core_db_max_values_per_user_used_experiment_query'
DEFAULT_MAX_VALUES_PER_USER_USED_EXPERIMENT_QUERY = 30

WEBLAB_DATABASE_CONNECTION_POOL_SIZE = 'db_connection_pool_size'
DEFAULT_WEBLAB_DATABASE_CONNECTION_POOL_SIZE = 25
WEBLAB_DATABASE_CONNECTION_TIMEOUT   = 'weblab_database_connection_timeout'
DEFAULT_WEBLAB_DATABASE_CONNECTION_TIMEOUT   = 60 # seconds

class DatabaseGateway(dbMySQLGateway.AbstractDatabaseGateway):

    def __init__(self, cfg_manager):
        super(DatabaseGateway, self).__init__(cfg_manager)

    #########################################################################
    #########################################################################
    ##################   E X T E R N A L    A P I   #########################
    #########################################################################
    #########################################################################

    ###################################################################
    ##################   get_groups_of_user   #########################
    ###################################################################
    @_db_credentials_checker
    @logged()
    def get_groups_of_user(self,cursors,user_id):
        """
            Given a user_id, it returns the groups where this user is integrated in
        """
        return self._get_groups_of_user(cursors,user_id)

    ####################################################################
    ##################   get_groups_of_group   #########################
    ####################################################################
    @_db_credentials_checker
    @logged()
    def get_groups_of_group(self,cursors,group_id):
        """
            Given a user_id, it returns the groups where this group is integrated in
        """
        return self._get_groups_of_group(cursors,group_id)

    #################################################################
    ##################   get_user_by_name   #########################
    #################################################################
    @_db_credentials_checker
    @logged()
    def get_user_by_name(self, cursors, user_login):
        return self._get_user_by_name(cursors,user_login)

    #################################################################
    ##################   list_experiments   #########################
    #################################################################
    @_db_credentials_checker
    @logged()
    def list_experiments(self, cursors, user_id):
        permissions = self._retrieve_all_user_permissions(
                cursors, 
                user_id, 
                Permissions.experiment_allowed
            )
        
        grouped_experiments = {}
        for i in permissions:
            # Retrieve parameters
            experiment_permanent_id = self._get_parameter_from_permission(
                    i,
                    'experiment_permanent_id'
                )
            time_allowed            = self._get_float_parameter_from_permission(
                    i,
                    'time_allowed'
                )
            category_id             = self._get_parameter_from_permission(
                    i,
                    'experiment_category_id'
                )
            
            experiment = self._retrieve_experiment(
                    cursors,
                    category_id,
                    experiment_permanent_id
                )

            experiment_allowed = ExperimentAllowed.ExperimentAllowed(
                    experiment,
                    time_allowed
                )
            
            experiment_unique_id = experiment_permanent_id+"@"+category_id
            if grouped_experiments.has_key(experiment_unique_id):
                grouped_experiments[experiment_unique_id].append(experiment_allowed)
            else:
                grouped_experiments[experiment_unique_id] = [experiment_allowed]
            
        # If any experiment is duplicated, only the less restrictive one is given
        experiments = []
        for experiment_unique_id in grouped_experiments:
            less_restrictive_experiment_allowed = grouped_experiments[experiment_unique_id][0]
            for experiment_allowed in grouped_experiments[experiment_unique_id]:
                if experiment_allowed.time_allowed > less_restrictive_experiment_allowed.time_allowed:
                    less_restrictive_experiment_allowed = experiment_allowed
            experiments.append(less_restrictive_experiment_allowed)

        experiments.sort(lambda x,y: cmp(x.experiment.category.name, y.experiment.category.name))
        return tuple(experiments)

    #####################################################################
    ##################   list_usages_per_user   #########################
    #####################################################################
    @_db_credentials_checker
    @logged()
    def list_usages_per_user(self, cursors, user_id, starting):
        sentence_count = """ SELECT COUNT(uue_user_experiment_use_id) 
                FROM %(UserUsedExperiment)s 
                WHERE
                    uue_user_id = %(provided_user_id)s
                    """ % {
            'UserUsedExperiment'    :   self._get_table('UserUsedExperiment',cursors[NAME],SELECT),
            'provided_user_id'  :   '%s', # a parameter
        }
        cursors[READ].execute(sentence_count, user_id)
        lines = cursors[READ].fetchall()
        count = lines[0][0]
        sentence = """SELECT 
                    uue_user_experiment_use_id,
                    uue_start_date,
                    uue_start_date_micro,
                    uue_finish_date,
                    uue_finish_date_micro,
                    uue_from,
                    uue_experiment_id,
                    uue_coord_address
                FROM %(UserUsedExperiment)s
                WHERE 
                    uue_user_id = %(provided_user_id)s
                LIMIT
                    %(lower_limit)s, %(higher_limit)s
            """ % {
            'UserUsedExperiment'    :   self._get_table('UserUsedExperiment',cursors[NAME],SELECT),
            'provided_user_id'  :   '%s', # a parameter
            'lower_limit'       :   '%s', # another parameter
            'higher_limit'      :   '%s'  # yet another parameter
        }
        max_elements = self._cfg_manager.get_value( MAX_VALUES_PER_USER_USED_EXPERIMENT_QUERY_NAME, DEFAULT_MAX_VALUES_PER_USER_USED_EXPERIMENT_QUERY )
        cursors[READ].execute(sentence, (user_id, starting, starting + max_elements) )
        lines = cursors[READ].fetchall()
        usages = []
        for line in lines:
            usage = Usage.ExperimentUsage()
            usage.experiment_usage_id = line[0]

            start_date                = line[1]
            start_date_micro          = line[2]
            end_date                  = line[3]
            end_date_micro            = line[4]
            
            usage.start_date          = calendar.timegm(start_date.timetuple()) + (1.0 * start_date_micro / (1000 * 1000))
            usage.end_date            = calendar.timegm(end_date.timetuple())   + (1.0 * end_date_micro   / (1000 * 1000))

            usage.from_ip             = line[5]
            usage.experiment_id       = self._retrieve_experiment_id_by_id(cursors, line[6])
            usage.coord_address       = CoordAddress.CoordAddress.translate_address(line[7])
            usages.append(usage)
        return count, usages
    
    ###############################################################
    ##################   retrieve_usage   #########################
    ###############################################################
    @_db_credentials_checker
    @logged()
    def retrieve_usage(self, cursors, user_id, usage_id):
        sentence = """SELECT 
                    uue_user_experiment_use_id,
                    uue_start_date,
                    uue_start_date_micro,
                    uue_finish_date,
                    uue_finish_date_micro,
                    uue_from,
                    uue_experiment_id,
                    uue_coord_address
                FROM %(UserUsedExperiment)s
                WHERE 
                    uue_user_id = %(provided_user_id)s
                    AND uue_user_experiment_use_id = %(provided_usage_id)s
            """ % {
            'UserUsedExperiment'    :   self._get_table('UserUsedExperiment',cursors[NAME],SELECT),
            'provided_user_id'  :   '%s', # a parameter
            'provided_usage_id' :   '%s'  # yet another parameter
        }
        cursors[READ].execute(sentence, (user_id, usage_id) )
        lines = cursors[READ].fetchall()
        if len(lines) != 1:
            #TODO: Improve this
            raise Exception("1 line expected, %s found" % len(lines))

        line = lines[0]

        usage = Usage.ExperimentUsage()
        usage.experiment_usage_id = line[0]

        start_date                = line[1]
        start_date_micro          = line[2]
        end_date                  = line[3]
        end_date_micro            = line[4]
        
        usage.start_date          = calendar.timegm(start_date.timetuple()) + (1.0 * start_date_micro / (1000 * 1000))
        usage.end_date            = calendar.timegm(end_date.timetuple())   + (1.0 * end_date_micro   / (1000 * 1000))

        usage.from_ip             = line[5]
        usage.experiment_id       = self._retrieve_experiment_id_by_id(cursors, line[6])
        usage.coord_address       = CoordAddress.CoordAddress.translate_address(line[7])

        sentence = """SELECT
                    command,
                    response,
                    timestamp_before,
                    timestamp_before_micro,
                    timestamp_after,
                    timestamp_after_micro
                FROM %(UserCommand)s, %(UserUsedExperiment)s
                WHERE 
                    experiment_use_id = %(provided_usage_id)s
                    AND uue_user_experiment_use_id = experiment_use_id
                    AND uue_user_id = %(provided_user_id)s
            """ % {
            'UserCommand'           :  self._get_table('UserCommand',cursors[NAME],SELECT),
            'UserUsedExperiment'    :  self._get_table('UserUsedExperiment',cursors[NAME],SELECT),
            'provided_usage_id' :  '%s', # a parameter
            'provided_user_id'  :  '%s' # a parameter
        }
        cursors[READ].execute(sentence, (usage_id, user_id) )
        lines = cursors[READ].fetchall()
        for line in lines:
            command                = line[0]
            response               = line[1]
            dtimestamp_before      = line[2]
            dtimestamp_beforemicro = line[3]
            dtimestamp_after       = line[4]
            dtimestamp_aftermicro  = line[5]
            
            timestamp_before       = calendar.timegm(dtimestamp_before.timetuple()) + dtimestamp_beforemicro / 1e6
            if dtimestamp_after != None and dtimestamp_aftermicro != None:
                timestamp_after = calendar.timegm(dtimestamp_after.timetuple()) + dtimestamp_aftermicro / 1e6
            else:
                timestamp_after = None
            if response == None:
                response_command = Command.NullCommand()
            else:
                response_command = Command.Command(response)


            command_sent     = Usage.CommandSent(
                    Command.Command(command), 
                    timestamp_before,
                    response_command,
                    timestamp_after
                )
            usage.append_command(command_sent)

        sentence = """SELECT
                    file_sent,
                    file_hash,
                    response,
                    timestamp_before,
                    timestamp_before_micro,
                    timestamp_after,
                    timestamp_after_micro,
                    file_info
                FROM %(UserFile)s, %(UserUsedExperiment)s
                WHERE 
                    experiment_use_id = %(provided_usage_id)s
                    AND uue_user_experiment_use_id = experiment_use_id
                    AND uue_user_id = %(provided_user_id)s
            """ % {
            'UserFile'              :  self._get_table('UserFile',cursors[NAME],SELECT),
            'UserUsedExperiment'    :  self._get_table('UserUsedExperiment',cursors[NAME],SELECT),
            'provided_usage_id' :  '%s', # a parameter
            'provided_user_id'  :  '%s' # a parameter
        }
        cursors[READ].execute(sentence, (usage_id, user_id) )
        lines = cursors[READ].fetchall()
        for line in lines:
            file_sent               = line[0]
            file_hash               = line[1]
            response                = line[2]
            dtimestamp_before       = line[3]
            dtimestamp_before_micro = line[4]
            dtimestamp_after        = line[5]
            dtimestamp_after_micro  = line[6]
            file_info               = line[7]
            
            timestamp_before        = calendar.timegm(dtimestamp_before.timetuple()) + (1.0 * dtimestamp_before_micro / (1000 * 1000))
            if dtimestamp_after != None and dtimestamp_after_micro != None:
                timestamp_after = calendar.timegm(dtimestamp_after.timetuple())  + (1.0 * dtimestamp_after_micro  / (1000 * 1000))
            else:
                timestamp_after = None

            if response == None:
                response_command = Command.NullCommand()
            else:
                response_command = Command.Command(response)

            file_sent              = Usage.FileSent(
                    file_sent,
                    file_hash,
                    timestamp_before,
                    response_command,
                    timestamp_after,
                    file_info = file_info
                )
            usage.append_file(file_sent)

        return usage

    #######################################################################
    ##################   store_experiment_usage   #########################
    #######################################################################
    @_db_credentials_checker
    @logged()
    def store_experiment_usage(self, cursors, user_id, experiment_usage):
        # experiment_usage is an instance of weblab.data.experiments.Usage.ExperimentUsage
        sentence = """INSERT INTO %(UserUsedExperiment)s 
                (
                    uue_user_id,
                    uue_start_date,
                    uue_start_date_micro,
                    uue_finish_date,
                    uue_finish_date_micro,
                    uue_from,
                    uue_experiment_id,
                    uue_coord_address
                ) VALUES (
                    %(uue_user_id)s,
                    %(uue_start_date)s,
                    %(uue_start_date_micro)s,
                    %(uue_finish_date)s,
                    %(uue_finish_date_micro)s,
                    %(uue_from)s,
                    %(uue_experiment_id)s,
                    %(uue_coord_address)s
                );
            """ % {
            'UserUsedExperiment':       self._get_table('UserUsedExperiment',cursors[NAME],INSERT),
            'uue_user_id':          '%s', #a parameter
            'uue_start_date':       '%s', #a parameter
            'uue_start_date_micro':     '%s', #a parameter
            'uue_finish_date':      '%s', #a parameter
            'uue_finish_date_micro':    '%s', #a parameter
            'uue_from':             '%s', #a parameter
            'uue_experiment_id':        '%s', #a parameter
            'uue_coord_address':        '%s'  #a parameter
        }
        start_date       = datetime.datetime.utcfromtimestamp(experiment_usage.start_date)
        start_date_micro = start_date.microsecond
        end_date         = datetime.datetime.utcfromtimestamp(experiment_usage.end_date)
        end_date_micro   = end_date.microsecond
        cursors[WRITE].execute(
                sentence,
                (
                    user_id,
                    start_date,
                    start_date_micro,
                    end_date,
                    end_date_micro,
                    experiment_usage.from_ip,
                    self._retrieve_experiment_id(
                        cursors,
                        experiment_usage.experiment_id.cat_name,
                        experiment_usage.experiment_id.exp_name
                    ),
                    experiment_usage.coord_address.address
                )
            )
        usage_id = cursors[WRITE].lastrowid
        for command in experiment_usage.commands:
            command_sentence = """INSERT INTO %(UserCommand)s 
                (
                    experiment_use_id,
                    command,
                    response,
                    timestamp_before,
                    timestamp_before_micro,
                    timestamp_after,
                    timestamp_after_micro
                ) VALUES (
                    %(experiment_use_id)s,
                    %(command)s,
                    %(response)s,
                    %(timestamp_before)s,
                    %(timestamp_before_micro)s,
                    %(timestamp_after)s,
                    %(timestamp_after_micro)s
                );
            """ % {
                'UserCommand'            :  self._get_table('UserCommand',cursors[NAME],INSERT),
                'experiment_use_id'      :  '%s', #a parameter
                'command'                :  '%s', #a parameter
                'response'               :  '%s', #a parameter
                'timestamp_before'       :  '%s', #a parameter
                'timestamp_before_micro' :  '%s', #a parameter
                'timestamp_after'        :  '%s', #a parameter
                'timestamp_after_micro'  :  '%s'  #a parameter
            }
            command_timestamp_before       = datetime.datetime.utcfromtimestamp(command.timestamp_before)
            command_timestamp_before_micro = command_timestamp_before.microsecond

            if command.timestamp_after != None:
                command_timestamp_after       = datetime.datetime.utcfromtimestamp(command.timestamp_after)
                command_timestamp_after_micro = command_timestamp_after.microsecond
            else:
                command_timestamp_after       = None
                command_timestamp_after_micro = None

            cursors[WRITE].execute(
                    command_sentence,
                    (
                        usage_id,
                        command.command.get_command_string(),
                        command.response.get_command_string(),
                        command_timestamp_before,
                        command_timestamp_before_micro,
                        command_timestamp_after,
                        command_timestamp_after_micro
                    )
                )
        for file_sent in experiment_usage.sent_files:
            file_sentence = """INSERT INTO %(UserFile)s 
                (
                    experiment_use_id,
                    file_sent,
                    file_hash,
                    file_info,
                    response,
                    timestamp_before,
                    timestamp_before_micro,
                    timestamp_after,
                    timestamp_after_micro
                ) VALUES (
                    %(experiment_use_id)s,
                    %(file_sent)s,
                    %(file_hash)s,
                    %(file_info)s,
                    %(response)s,
                    %(timestamp_before)s,
                    %(timestamp_before_micro)s,
                    %(timestamp_after)s,
                    %(timestamp_after_micro)s
                );
            """ % {
                'UserFile':         self._get_table('UserFile',cursors[NAME],INSERT),
                'experiment_use_id':        '%s', #a parameter
                'file_sent':            '%s', #a parameter
                'file_hash':            '%s', #a parameter
                'file_info':            '%s', #a parameter
                'response':             '%s', #a parameter
                'timestamp_before':         '%s', #a parameter
                'timestamp_before_micro':   '%s', #a parameter
                'timestamp_after':      '%s', #a parameter
                'timestamp_after_micro':        '%s'
            }
            file_timestamp_before       = datetime.datetime.utcfromtimestamp(file_sent.timestamp_before)
            file_timestamp_before_micro = file_timestamp_before.microsecond
            if file_sent.timestamp_after != None:
                file_timestamp_after        = datetime.datetime.utcfromtimestamp(file_sent.timestamp_after)
                file_timestamp_after_micro  = file_timestamp_after.microsecond
            else:
                file_timestamp_after        = None
                file_timestamp_after_micro  = None

            cursors[WRITE].execute(
                    file_sentence,
                    (
                        usage_id,
                        file_sent.file_sent,
                        file_sent.file_hash,
                        file_sent.file_info,
                        file_sent.response.get_command_string(),
                        file_timestamp_before,
                        file_timestamp_before_micro,
                        file_timestamp_after,
                        file_timestamp_after_micro
                    )
                )

    #########################################################################################
    #########################################################################################
    ##################   A U X I L I A R        F U N C T I O N S   #########################
    #########################################################################################
    #########################################################################################

    ##############################################################
    ##################   T E S T I N G   #########################
    ##############################################################

    @_db_credentials_checker
    def _execute(self, cursors, sentence):
        """ IMPORTANT: SHOULD NEVER BE USED IN PRODUCTION, IT'S HERE ONLY FOR TESTS """
        cursors[WRITE].execute(sentence)

    #########################################################################
    ##################   S Q L      H E L P E R S   #########################
    #########################################################################

            
    ##########################################################
    ##################   U S E R S   #########################
    ##########################################################

    def _get_user_by_name(self, cursors, user_login):
        sentence = """SELECT  user_id, user_full_name, user_email, user_role_id
                FROM  %(table_users)s
                WHERE user_login = %(provided_user_login)s
                """ % {
                        'table_users'           : self._get_table('User',           cursors[NAME],SELECT),
                        'provided_user_login'   : '%s' #a parameter
                    }
        cursors[READ].execute(sentence,user_login)
        user_result = cursors[READ].fetchone()

        if user_result == None:
            raise DbExceptions.DbProvidedUserNotFoundException(
                    "Couldn't find user %s" % user_login
                )
        else:
            user_id         = int(user_result[0])
            user_full_name  = user_result[1]
            user_email      = user_result[2]
            user_role_id    = int(user_result[3])
            return dao_User.create_user(
                    user_id,
                    str(user_login), 
                    user_full_name, 
                    user_email,
                    self._get_user_role(cursors,user_role_id)
                )

    ############################################################
    ##################   G R O U P S   #########################
    ############################################################

    def _get_groups_of_user(self,cursors,user_id):
        sentence = """SELECT  %(table_groups)s.group_id, group_name, group_owner_id, user_login, user_full_name, user_email, user_role_id
                FROM  %(table_groups)s, %(table_users)s, %(table_user_member_of)s 
                WHERE %(table_user_member_of)s.user_id = %(provided_user_id)s 
                AND   %(table_user_member_of)s.group_id = %(table_groups)s.group_id 
                AND   %(table_groups)s.group_owner_id = %(table_users)s.user_id 
                """ % {
                        'table_users'           : self._get_table('User',           cursors[NAME],SELECT),
                        'table_groups'          : self._get_table('Group',          cursors[NAME],SELECT),
                        'table_user_member_of'  : self._get_table('UserIsMemberOf', cursors[NAME],SELECT),
                        'provided_user_id'  : '%s' #a parameter
                    }
        cursors[READ].execute(sentence,user_id)
        groups = cursors[READ].fetchall()
        return_value = ()
        for group in groups:
            group_id        = group[0]
            group_name      = group[1]
            owner_id        = group[2]
            owner_login     = group[3]
            owner_full_name = group[4]
            owner_email     = group[5]
            owner_role_id   = group[6]
            p = dao_User.create_user(
                    owner_id,
                    owner_login, 
                    owner_full_name, 
                    owner_email,
                    self._get_user_role(cursors,owner_role_id)
                )
            g = dao_Group.Group(group_id,group_name,p)
            return_value += (g,)
        return return_value

    def _get_groups_of_group(self, cursors, group_id):
        sentence = """SELECT %(table_is_member_of)s.group_owner_id, group_name, 
                     %(table_group)s.group_owner_id owner_id, user_login, user_full_name, user_email, user_role_id
                FROM %(table_group)s, %(table_is_member_of)s, %(table_users)s
                WHERE %(table_is_member_of)s.group_id = %(provided_group_id)s
                AND %(table_group)s.group_id          = %(table_is_member_of)s.group_owner_id
                AND %(table_users)s.user_id           = %(table_group)s.group_owner_id
                """ % {
                    'table_group'           : self._get_table('Group',           cursors[NAME],SELECT),
                    'table_users'           : self._get_table('User',           cursors[NAME],SELECT),
                    'table_is_member_of'    : self._get_table('GroupIsMemberOf', cursors[NAME],SELECT),
                    'provided_group_id' : '%s'
                }
        cursors[READ].execute(sentence,group_id)
        groups = cursors[READ].fetchall()
        return_value = ()
        for group in groups:
            group_id        = int(group[0])
            group_name      = group[1]
            owner_id        = int(group[2])
            owner_login     = group[3]
            owner_full_name = group[4]
            owner_email     = group[5]
            owner_role_id   = int(group[6])
            p = dao_User.create_user(
                    owner_id,
                    owner_login, 
                    owner_full_name, 
                    owner_email,
                    self._get_user_role(cursors,owner_role_id)
                )
            g = dao_Group.Group(group_id,group_name,p)
            return_value += (g,)
        return return_value
    
    def _get_all_groups_of_group(self, cursors, group_id):
        all_groups = {}

        def get_all_groups_recursively(group_id):
            for i in self._get_groups_of_group(cursors,group_id):
                if not all_groups.has_key(i.id):
                    all_groups[i.id] = i
                    get_all_groups_recursively(i.id)

        get_all_groups_recursively(group_id)
        return all_groups.values()

    def _get_all_groups_of_user(self, cursors, user_id):
        all_groups = {}

        for i in self._get_groups_of_user(cursors, user_id):
            if not all_groups.has_key(i.id):
                all_groups[i.id] = i
                for j in self._get_all_groups_of_group(cursors,i.id):
                    if not all_groups.has_key(j.id):
                        all_groups[j.id] = j

        return all_groups.values()

    ######################################################################
    ##################   E X P E R I M E N T S   #########################
    ######################################################################

    def _retrieve_experiment(self, cursors, experiment_category_name,experiment_name):
        sentence = """SELECT experiment_start_date, experiment_end_date, user_login
                FROM %(table_experiment)s, %(table_experiment_category)s, %(table_user)s
                WHERE user_id = experiment_owner_id 
                AND experiment_category_name = %(provided_experiment_category)s
                AND %(table_experiment)s.experiment_category_id = %(table_experiment_category)s.experiment_category_id
                AND experiment_name = %(provided_experiment_name)s
            """ % {
                'table_experiment' :           self._get_table('Experiment',         cursors[NAME],SELECT),
                'table_experiment_category' :  self._get_table('ExperimentCategory', cursors[NAME],SELECT),
                'table_user' :                 self._get_table('User',               cursors[NAME],SELECT),
                'provided_experiment_category' : '%s',
                'provided_experiment_name' : '%s'
            }
        cursors[READ].execute(sentence,(experiment_category_name,experiment_name))
        experiment = cursors[READ].fetchone()
        if experiment == None:
            raise DbExceptions.DbProvidedExperimentNotFoundException(
                "No experiment found with category name '%s' and name '%s'" % (
                    experiment_category_name,
                    experiment_name
                )
            )
        else:
            start_date = experiment[0]
            end_date   = experiment[1]
            user_login = experiment[2]
            
            owner      = self._get_user_by_name(cursors,user_login).to_business()
            category   = ExperimentCategory.ExperimentCategory(experiment_category_name)
            
            experiment = Experiment.Experiment(
                    experiment_name,
                    owner,
                    category,
                    start_date,
                    end_date
                )
            return experiment

    def _retrieve_experiment_id(self, cursors, experiment_category_name, experiment_name):
        sentence = """SELECT experiment_id
                FROM %(table_experiment)s, %(table_experiment_category)s
                WHERE 
                    experiment_category_name = %(provided_experiment_category)s
                    AND %(table_experiment)s.experiment_category_id = %(table_experiment_category)s.experiment_category_id
                    AND experiment_name = %(provided_experiment_name)s
            """ % {
                'table_experiment' :           self._get_table('Experiment',         cursors[NAME],SELECT),
                'table_experiment_category' :  self._get_table('ExperimentCategory', cursors[NAME],SELECT),
                'provided_experiment_category' : '%s',
                'provided_experiment_name' : '%s'
            }
        cursors[READ].execute(sentence,(experiment_category_name,experiment_name))
        experiment = cursors[READ].fetchone()
        if experiment == None:
            raise DbExceptions.DbProvidedExperimentNotFoundException(
                "No experiment found with category name '%s' and name '%s'" % (
                    experiment_category_name,
                    experiment_name
                )
            )
        else:
            experiment_id = experiment[0]
            return experiment_id

    def _retrieve_experiment_id_by_id(self, cursors, experiment_id):
        sentence = """SELECT experiment_name, experiment_category_name
                FROM %(table_experiment)s, %(table_experiment_category)s
                WHERE 
                    %(table_experiment)s.experiment_category_id = %(table_experiment_category)s.experiment_category_id
                    AND experiment_id = %(provided_experiment_id)s
            """ % {
                'table_experiment' :           self._get_table('Experiment',         cursors[NAME],SELECT),
                'table_experiment_category' :  self._get_table('ExperimentCategory', cursors[NAME],SELECT),
                'provided_experiment_id' : '%s'
            }
        cursors[READ].execute(sentence,experiment_id)
        experiment = cursors[READ].fetchone()
        if experiment == None:
            raise DbExceptions.DbProvidedExperimentNotFoundException(
                "No experiment found with ID %s" % (
                    experiment_id
                )
            )
        else:
            experiment_name          = experiment[0]
            experiment_category_name = experiment[1]
            return ExperimentId.ExperimentId(
                    experiment_name,
                    experiment_category_name
                )

    ######################################################################
    ##################   P E R M I S S I O N S   #########################
    ######################################################################

    def _retrieve_all_user_permissions(self, cursors, user_id, permission_name):
        permissions = []
        # retrieve the permissions of the user itself
        for user_permission in self._retrieve_user_permissions(cursors,user_id, permission_name):
            permissions.append(user_permission)
        for group in self._get_all_groups_of_user(cursors,user_id):
            for group_permission in self._retrieve_group_permissions(cursors, group.id, permission_name):
                permissions.append(group_permission)
        return permissions

    def _retrieve_user_permissions(self, cursors, user_id, permission_name):
        # First, get the permissions themselves
        sentence = """SELECT upi_id, upi_user_permission_type_id, upi_date, upi_name, upi_comments, upt_description, 
                     upi_owner_id, user_login, user_full_name, user_email, user_role_id
                FROM %(table_user_permission_instance)s, %(table_user_permission_type)s, %(table_users)s
                WHERE upi_user_id = %(provided_user_id)s 
                AND upi_user_permission_type_id = upt_id 
                AND upt_name = %(provided_permission_name)s
                AND upi_owner_id = user_id
            """ % {
                    'table_user_permission_instance' : self._get_table('UserPermissionInstance', cursors[NAME],SELECT),
                    'table_user_permission_type'     : self._get_table('UserPermissionType',     cursors[NAME],SELECT),
                    'table_users'                    : self._get_table('User',                   cursors[NAME],SELECT),
                    'provided_user_id'               : '%s',
                    'provided_permission_name'       : '%s'
            }
        cursors[READ].execute(sentence,(user_id,permission_name))
        permissions = cursors[READ].fetchall()
        # Then, get the parameters of these permissions
        sentence = """SELECT upp_id, upp_user_permission_instance_id, upp_value, 
                     uppt_id, uppt_name, uppt_type, uppt_description
                FROM %(table_user_permission_type)s, %(table_user_permission_instance)s, 
                     %(table_user_permission_parameter)s, %(table_user_permission_parameter_type)s
                WHERE upt_name    = %(provided_permission_name)s
                AND   upt_id      = uppt_user_permission_type_id
                AND   uppt_id     = upp_user_permission_param_id
                AND   upi_id      = upp_user_permission_instance_id
                AND   upi_user_id = %(provided_user_id)s
            """ % {
                    'table_user_permission_parameter_type' : self._get_table('UserPermissionParameterType', cursors[NAME],SELECT),
                    'table_user_permission_instance'       : self._get_table('UserPermissionInstance', cursors[NAME],SELECT),
                    'table_user_permission_parameter'      : self._get_table('UserPermissionParameter', cursors[NAME],SELECT),
                    'table_user_permission_type'           : self._get_table('UserPermissionType',     cursors[NAME],SELECT),
                    'provided_permission_name'             : '%s',
                    'provided_user_id'                     : '%s'
            }
        cursors[READ].execute(sentence,(permission_name,user_id))
        permission_parameters = cursors[READ].fetchall()

        # Process the information gathered
        user_permission_type = None
        permission_instances = {}
        for permission in permissions:
            # Make the variables more readable
            upi_id                      = int(permission[0])
            upi_user_permission_type_id = int(permission[1])
            upi_date                    = permission[2]
            upi_name                    = permission[3]
            upi_comments                = permission[4]
            upt_description             = permission[5]
            owner_id                    = int(permission[6])
            owner_login                 = permission[7]
            owner_full_name             = permission[8]
            owner_email                 = permission[9]
            owner_role_id               = int(permission[10])
        
            # Create the UserPermissionType
            if user_permission_type == None:
                user_permission_type = dao_Permission.UserPermissionType(
                    upi_user_permission_type_id,
                    permission_name,
                    upt_description
                )
            else:   # There should be only one, but just in case
                if ( user_permission_type.id != upi_user_permission_type_id
                    or user_permission_type.description != upt_description):
                    raise DbExceptions.DbIllegalStatusException(
                            "Two different user permissions found for the same name %s !" % permission_name
                    )

            # Create the owner User
            owner = dao_User.create_user(
                owner_id,
                owner_login, 
                owner_full_name, 
                owner_email,
                self._get_user_role(cursors,owner_role_id)
            )
        
            permission_instance = dao_Permission.UserPermissionInstance(
                    upi_id,
                    user_permission_type,
                    owner,
                    upi_date,
                    upi_name,
                    upi_comments
                )
            permission_instances[upi_id] = permission_instance

        permission_parameter_types = {}
        for permission_parameter in permission_parameters:
            upp_id             = int(permission_parameter[0])
            upp_upi_id         = int(permission_parameter[1])
            upp_value          = permission_parameter[2]
            uppt_id            = int(permission_parameter[3])
            uppt_name          = permission_parameter[4]
            uppt_type          = permission_parameter[5]
            uppt_description   = permission_parameter[6]
            
            if not permission_parameter_types.has_key(uppt_id):
                uppt = dao_Permission.UserPermissionParameterType(
                    uppt_id,
                    uppt_name,
                    uppt_type,
                    uppt_description,
                    user_permission_type
                )
                permission_parameter_types[uppt_id] = uppt
            else:
                uppt = permission_parameter_types[uppt_id]
                if ( uppt.name != uppt_name
                    or uppt.type != uppt_type
                    or uppt.description != uppt_description ):
                    raise DbExceptions.DbIllegalStatusException(
                            "Two different user permission parameter types found for the same name %s and parameter id %s !" % (permission_name,uppt_id)
                    )
            
            upp = dao_Permission.UserPermissionParameter(
                    upp_id,
                    uppt,
                    upp_value
                )
            if permission_instances.has_key(upp_upi_id):
                pi = permission_instances[upp_upi_id]
                if pi.parameters.has_key(uppt.name):
                    raise DbExceptions.DbIllegalStatusException(
                            "%s parameter already found! " % uppt.name
                        )
                pi.parameters[uppt.name] = upp
            else:
                raise DbExceptions.DbIllegalStatusException(
                    "Didn't find permission instance for this permission parameter" % permission_name
                )
        return permission_instances.values()

    # TODO: this method is *really* similar to _retrieve_group_permissions, and is probably be very similar to _retrieve_external_permissions. Refactor it
    def _retrieve_group_permissions(self, cursors, group_id, permission_name):
        # First, get the permissions themselves
        sentence = """SELECT gpi_id, gpi_group_permission_type_id, gpi_date, gpi_name, gpi_comments, gpt_description, 
                     gpi_owner_id, user_login, user_full_name, user_email, user_role_id
                FROM %(table_group_permission_instance)s, %(table_group_permission_type)s, %(table_users)s
                WHERE gpi_group_id = %(provided_group_id)s 
                AND gpi_group_permission_type_id = gpt_id 
                AND gpt_name = %(provided_permission_name)s
                AND gpi_owner_id = user_id
            """ % {
                    'table_group_permission_instance' : self._get_table('GroupPermissionInstance', cursors[NAME],SELECT),
                    'table_group_permission_type'     : self._get_table('GroupPermissionType',     cursors[NAME],SELECT),
                    'table_groups'                    : self._get_table('Group',                   cursors[NAME],SELECT),
                    'table_users'                     : self._get_table('User',                    cursors[NAME],SELECT),
                    'provided_group_id'               : '%s',
                    'provided_permission_name'        : '%s'
            }
        cursors[READ].execute(sentence,(group_id,permission_name))
        permissions = cursors[READ].fetchall()
        # Then, get the parameters of these permissions
        sentence = """SELECT gpp_id, gpp_group_permission_instance_id, gpp_value, 
                     gppt_id, gppt_name, gppt_type, gppt_description
                FROM %(table_group_permission_type)s, %(table_group_permission_instance)s, 
                     %(table_group_permission_parameter)s, %(table_group_permission_parameter_type)s
                WHERE gpt_name    = %(provided_permission_name)s
                AND   gpt_id      = gppt_group_permission_type_id
                AND   gppt_id     = gpp_group_permission_param_id
                AND   gpi_id      = gpp_group_permission_instance_id
                AND   gpi_group_id = %(provided_group_id)s
            """ % {
                    'table_group_permission_parameter_type' : self._get_table('GroupPermissionParameterType', cursors[NAME],SELECT),
                    'table_group_permission_instance'       : self._get_table('GroupPermissionInstance', cursors[NAME],SELECT),
                    'table_group_permission_parameter'      : self._get_table('GroupPermissionParameter', cursors[NAME],SELECT),
                    'table_group_permission_type'           : self._get_table('GroupPermissionType',     cursors[NAME],SELECT),
                    'provided_permission_name'             : '%s',
                    'provided_group_id'                     : '%s'
            }
        cursors[READ].execute(sentence,(permission_name,group_id))
        permission_parameters = cursors[READ].fetchall()

        # Process the information gathered
        group_permission_type = None
        permission_instances = {}
        for permission in permissions:
            # Make the variables more readable
            gpi_id                       = int(permission[0])
            gpi_group_permission_type_id = int(permission[1])
            gpi_date                     = permission[2]
            gpi_name                     = permission[3]
            gpi_comments                 = permission[4]
            gpt_description              = permission[5]
            owner_id                     = int(permission[6])
            owner_login                  = permission[7]
            owner_full_name              = permission[8]
            owner_email                  = permission[9]
            owner_role_id                = int(permission[10])
        
            # Create the groupPermissionType
            if group_permission_type == None:
                group_permission_type = dao_Permission.GroupPermissionType(
                    gpi_group_permission_type_id,
                    permission_name,
                    gpt_description
                )
            else:   # There should be only one, but just in case
                if ( group_permission_type.id != gpi_group_permission_type_id
                    or group_permission_type.description != gpt_description):
                    raise DbExceptions.DbIllegalStatusException(
                            "Two different group permissions found for the same name %s !" % permission_name
                    )

            # Create the owner group
            owner = dao_User.create_user(
                owner_id,
                owner_login, 
                owner_full_name, 
                owner_email,
                self._get_user_role(cursors,owner_role_id)
            )
        
            permission_instance = dao_Permission.GroupPermissionInstance(
                    gpi_id,
                    group_permission_type,
                    owner,
                    gpi_date,
                    gpi_name,
                    gpi_comments
                )
            permission_instances[gpi_id] = permission_instance

        permission_parameter_types = {}
        for permission_parameter in permission_parameters:
            gpp_id             = int(permission_parameter[0])
            gpp_gpi_id         = int(permission_parameter[1])
            gpp_value          = permission_parameter[2]
            gppt_id            = int(permission_parameter[3])
            gppt_name          = permission_parameter[4]
            gppt_type          = permission_parameter[5]
            gppt_description   = permission_parameter[6]
            
            if not permission_parameter_types.has_key(gppt_id):
                gppt = dao_Permission.GroupPermissionParameterType(
                    gppt_id,
                    gppt_name,
                    gppt_type,
                    gppt_description,
                    group_permission_type
                )
                permission_parameter_types[gppt_id] = gppt
            else:
                gppt = permission_parameter_types[gppt_id]
                if ( gppt.name != gppt_name
                    or gppt.type != gppt_type
                    or gppt.description != gppt_description ):
                    raise DbExceptions.DbIllegalStatusException(
                            "Two different group permission parameter types found for the same name %s and parameter id %s !" % (permission_name,gppt_id)
                    )
            
            gpp = dao_Permission.GroupPermissionParameter(
                    gpp_id,
                    gppt,
                    gpp_value
                )
            if permission_instances.has_key(gpp_gpi_id):
                pi = permission_instances[gpp_gpi_id]
                if pi.parameters.has_key(gppt.name):
                    raise DbExceptions.DbIllegalStatusException(
                            "%s parameter already found! " % gppt.name
                        )
                pi.parameters[gppt.name] = gpp
            else:
                raise DbExceptions.DbIllegalStatusException(
                    "Didn't find permission instance for this permission parameter" % permission_name
                )
        return permission_instances.values()

    def _get_parameter_from_permission(self, permission, parameter_name):
        parameter_value = permission.parameters.get(parameter_name)
        if parameter_value == None:
            raise DbExceptions.DbIllegalStatusException(
                    permission.permission_type.name + " permission without " + parameter_name
                )
        return parameter_value.value

    def _get_float_parameter_from_permission(self, permission, parameter_name):
        ret_value = self._get_parameter_from_permission(permission,parameter_name)
        try:
            return float(ret_value)
        except ValueError:
            raise DbExceptions.InvalidPermissionParameterFormatException(
                "Expected float as parameter '%s' of '%s', found: '%s'" % (
                    parameter_name,
                    permission.permission_type.name,
                    ret_value
                )
            )

