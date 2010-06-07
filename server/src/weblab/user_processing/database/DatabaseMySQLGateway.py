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
# Author: Jaime Irurzun <jaime.irurzun@gmail.com>
# 

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

from voodoo.log import logged

import weblab.database.Model as Model

import weblab.database.DatabaseMySQLGateway as dbMySQLGateway

from weblab.data.experiments.ExperimentAllowed import ExperimentAllowed

import weblab.exceptions.database.DatabaseExceptions as DbExceptions

WEBLAB_DB_USERNAME_PROPERTY = 'weblab_db_username'
DEFAULT_WEBLAB_DB_USERNAME  = 'weblab'

WEBLAB_DB_PASSWORD_PROPERTY = 'weblab_db_password'

def getconn():
    import MySQLdb as dbi
    return dbi.connect(user = DatabaseGateway.user, passwd = DatabaseGateway.password,
            host = DatabaseGateway.host, db = DatabaseGateway.dbname, client_flag = 2)


class DatabaseGateway(dbMySQLGateway.AbstractDatabaseGateway):

    user     = None
    password = None
    host     = None
    dbname   = None

    pool = sqlalchemy.pool.QueuePool(getconn, pool_size=15, max_overflow=20)

    def __init__(self, cfg_manager):
        super(DatabaseGateway, self).__init__(cfg_manager)
       
        DatabaseGateway.user     = cfg_manager.get_value(WEBLAB_DB_USERNAME_PROPERTY, DEFAULT_WEBLAB_DB_USERNAME)
        DatabaseGateway.password = cfg_manager.get_value(WEBLAB_DB_PASSWORD_PROPERTY)
        DatabaseGateway.host     = self.host
        DatabaseGateway.dbname   = self.database_name

        connection_url = "mysql://%(USER)s:%(PASSWORD)s@%(HOST)s/%(DATABASE)s" % \
                            { "USER":     self.user,
                              "PASSWORD": self.password,
                              "HOST":     self.host,
                              "DATABASE": self.dbname  }
        self.Session = sessionmaker(bind=create_engine(connection_url, echo=False, pool = self.pool))

    @logged()
    def get_user_by_name(self, user_login):
        session = self.Session()
        try:
            return self._get_user(session, user_login).to_business()
        finally:
            session.close()

    @logged()
    def list_experiments(self, user_login):
        session = self.Session()
        try:
            user = self._get_user(session, user_login)
            permissions = self._gather_permissions(session, user, 'experiment_allowed')
            
            grouped_experiments = {}
            for permission in permissions:
                p_permanent_id = self._get_parameter_from_permission(session, permission, 'experiment_permanent_id')
                p_category_id = self._get_parameter_from_permission(session, permission, 'experiment_category_id')
                p_time_allowed = self._get_float_parameter_from_permission(session, permission, 'time_allowed')
                
                experiment = session.query(Model.DbExperiment).filter_by(name=p_permanent_id).filter(Model.DbExperimentCategory.name==p_category_id).one() 
                experiment_allowed = ExperimentAllowed(experiment.to_business(), p_time_allowed)
                
                experiment_unique_id = p_permanent_id+"@"+p_category_id
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
        finally:
            session.close()

    @logged()
    def store_experiment_usage(self, user_login, experiment_usage):
        session = self.Session()
        try:
            use = Model.DbUserUsedExperiment(
                        self._get_user(session, user_login),
                        self._get_experiment(session, experiment_usage.experiment_id.exp_name, experiment_usage.experiment_id.cat_name),
                        experiment_usage.start_date,
                        experiment_usage.from_ip,
                        experiment_usage.coord_address.address,
                        experiment_usage.end_date
                )
            session.add(use)
            for c in experiment_usage.commands:
                session.add(Model.DbUserCommand(
                                use,
                                c.command.commandstring,
                                c.timestamp_before,
                                c.response.commandstring,
                                c.timestamp_after
                            ))
            for f in experiment_usage.sent_files:
                session.add(Model.DbUserFile(
                                use,
                                f.file_sent,
                                f.file_hash,
                                f.timestamp_before,
                                f.file_info,
                                f.response.commandstring,
                                f.timestamp_after
                            ))
            session.commit()
        finally:
            session.close()
    
    @logged()
    def list_usages_per_user(self, user_login, first=0, limit=20):
        session = self.Session()
        try:
            user = self._get_user(session, user_login)
            uses = session.query(Model.DbUserUsedExperiment).filter_by(user=user).offset(first).limit(limit).all()
            return [ use.to_business_light() for use in uses ]
        finally:
            session.close()
    
    @logged()
    def retrieve_usage(self, usage_id):
        session = self.Session()
        try:
            use = session.query(Model.DbUserUsedExperiment).filter_by(id=usage_id).one()
            return use.to_business()
        finally:
            session.close()

    @logged()
    def get_groups(self, user_login):
        """ All the groups are returned by the moment """
        
        def get_business_children_recursively(groups):
            business_groups = []
            for group in groups:
                business_group = group.to_business_light()
                if len(group.children) > 0:
                    business_group.set_children(get_business_children_recursively(group.children))
                business_groups.append(business_group)
            return business_groups
        
        session = self.Session()
        try:
            user = self._get_user(session, user_login)
            groups = session.query(Model.DbGroup).filter_by(parent=None).all()
            business_groups = get_business_children_recursively(groups)
            return tuple(business_groups)
        finally:
            session.close()

    @logged()
    def get_experiments(self, user_login):
        """ All the experiments are returned by the moment """
        
        session = self.Session()
        try:
            user = self._get_user(session, user_login)
            experiments = session.query(Model.DbExperiment).all()
            business_experiments = [ experiment.to_business() for experiment in experiments ]
            return tuple(business_experiments)
        finally:
            session.close()
    
    def _get_user(self, session, user_login):
        try:
            return session.query(Model.DbUser).filter_by(login=user_login).one()
        except NoResultFound:
            raise DbExceptions.DbProvidedUserNotFoundException("Unable to find a User with the provided login: '%s'" % user_login)
    
    def _get_experiment(self, session, exp_name, cat_name):
        try:
            return session.query(Model.DbExperiment) \
                        .filter(Model.DbExperimentCategory.name == cat_name) \
                        .filter_by(name=exp_name).one()
        except NoResultFound:
            raise DbExceptions.DbProvidedExperimentNotFoundException("Unable to find an Experiment with the provided unique id: '%s@%s'" % (exp_name, cat_name))
    
    def _gather_permissions(self, session, user, permission_type_name):
        permissions = []
        self._add_or_replace_permissions(permissions, self._get_permissions(session, user.role, permission_type_name))
        for group in user.groups:
            self._add_or_replace_permissions(permissions, self._get_permissions(session, group, permission_type_name))
        self._add_or_replace_permissions(permissions, self._get_permissions(session, user, permission_type_name))
        return permissions

    def _add_or_replace_permissions(self, permissions, permissions_to_add):
        permissions.extend(permissions_to_add)
        
    def _get_permissions(self, session, user_or_role_or_group_or_ee, permission_type_name):
        return [ pi for pi in user_or_role_or_group_or_ee.permissions if pi.get_permission_type().name == permission_type_name ]
    
    def _get_parameter_from_permission(self, session, permission, parameter_name):
        try:
            param = [ p for p in permission.parameters if p.get_name() == parameter_name ][0]
        except IndexError:
            raise DbExceptions.DbIllegalStatusException(
                    permission.get_permission_type().name + " permission without " + parameter_name
                )
        return param.value
    
    def _get_float_parameter_from_permission(self, session, permission, parameter_name):
        value = self._get_parameter_from_permission(session, permission, parameter_name)
        try:
            return float(value)
        except ValueError:
            raise DbExceptions.InvalidPermissionParameterFormatException(
                "Expected float as parameter '%s' of '%s', found: '%s'" % (
                    parameter_name,
                    permission.get_permission_type().name,
                    value
                )
            )       
    
    def _delete_all_uses(self):
        """ IMPORTANT: SHOULD NEVER BE USED IN PRODUCTION, IT'S HERE ONLY FOR TESTS """
        session = self.Session()
        try:
            uu = session.query(Model.DbUserUsedExperiment).all()
            for i in uu:
                session.delete(i)
                session.commit()
            eu = session.query(Model.DbExternalEntityUsedExperiment).all()
            for i in eu:
                session.delete(i)
                session.commit()               
        finally:
            session.close()
