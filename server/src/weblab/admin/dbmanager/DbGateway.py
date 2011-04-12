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

from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

import weblab.database.Model as Model


class DbGateway(object):
    
    def __init__(self, host, db, username, password):
        super(DbGateway, self).__init__()
        connection_url = "mysql://%(USER)s:%(PASS)s@%(HOST)s/%(NAME)s" % {
                                "USER": username,
                                "PASS": password,
                                "HOST": host,
                                "NAME": db }
        self.Session = sessionmaker(bind=create_engine(connection_url, echo=False))
        self.session = self.Session()
    
    def get_experiment_category(self, experiment_category_name):
        try:       
            return self.session.query(Model.DbExperimentCategory).filter_by(name=experiment_category_name).one()
        except NoResultFound:
            return None

    def get_group(self, group_name):
        try:       
            return self.session.query(Model.DbGroup).filter_by(name=group_name).one()
        except NoResultFound:
            return None

    def get_permission_type(self, permission_type_name):
        try:       
            return self.session.query(Model.DbPermissionType).filter_by(name=permission_type_name).one()
        except NoResultFound:
            return None
                
    def get_groups(self):
        try:
            return self.session.query(Model.DbGroup).order_by('id').all()
        except NoResultFound:
            return []
                
    def get_users(self, users_logins=None):
        try:
            if users_logins is None:
                return self.session.query(Model.DbUser).order_by('id').all()
            else:
                return self.session.query(Model.DbUser).filter(Model.DbUser.login.in_(users_logins)).all()
        except NoResultFound:
            return []
        
    def get_experiment_categories(self):
        try:
            return self.session.query(Model.DbExperimentCategory).order_by('id').all()
        except NoResultFound:
            return []
        
    def get_experiments(self):
        try:
            return self.session.query(Model.DbExperiment).order_by('id').all()
        except NoResultFound:
            return []
                
    def get_roles(self):
        try:
            return self.session.query(Model.DbRole).order_by('id').all()
        except NoResultFound:
            return []

    def get_auths(self, authtype_name):
        auth_type = self.session.query(Model.DbAuthType).filter_by(name=authtype_name).order_by('id').one()
        try:
            return self.session.query(Model.DbAuth).filter_by(auth_type=auth_type).order_by('id').all()
        except NoResultFound:
            return []

    def insert_group(self, group_name, parent_group):
        try:
            group = Model.DbGroup(group_name, parent_group)
            self.session.add(group)
            self.session.commit()
            return group
        except IntegrityError:
            return None   
            
    def insert_experiment_category(self, experiment_category_name):
        try:
            experiment_category = Model.DbExperimentCategory(name=experiment_category_name)
            self.session.add(experiment_category)
            self.session.commit()
            return experiment_category
        except IntegrityError:
            return None
            
    def insert_experiment(self, experiment_name, experiment_category, start_date, end_date):
        try:
            experiment = Model.DbExperiment(experiment_name, experiment_category, start_date, end_date)
            self.session.add(experiment)
            self.session.commit()
            return experiment
        except IntegrityError:
            return None

    def insert_user(self, login, full_name, email, avatar, role):
        try:
            user = Model.DbUser(login, full_name, email, avatar, role)
            self.session.add(user)
            self.session.commit()
            return user
        except IntegrityError:
            return None
                
    def insert_user_auth(self, user, auth, configuration):
        try:
            user_auth = Model.DbUserAuth(user, auth, configuration)
            self.session.add(user_auth)
            self.session.commit()
            return user_auth
        except IntegrityError:
            return None
                
    def add_user_to_group(self, user, group):
        try:
            group.users.append(user)
            self.session.commit()
            return user, group
        except IntegrityError:
            return None, None
                
    def grant_on_experiment_to_group(self, group, permission_type, permanent_id, date, comments, experiment, time_allowed, priority):
        try:
            group_permission = Model.DbGroupPermission(
                                    group,
                                    permission_type.group_applicable,
                                    permanent_id,
                                    date,
                                    comments
                                )
            self.session.add(group_permission)
            group_permission_p1 = Model.DbGroupPermissionParameter(
                                        group_permission,
                                        permission_type.get_parameter("experiment_permanent_id"),
                                        experiment.name
                                  )
            self.session.add(group_permission_p1)
            group_permission_p2 = Model.DbGroupPermissionParameter(
                                        group_permission,
                                        permission_type.get_parameter("experiment_category_id"),
                                        experiment.category.name
                                  )
            self.session.add(group_permission_p2)
            group_permission_p3 = Model.DbGroupPermissionParameter(
                                        group_permission,
                                        permission_type.get_parameter("time_allowed"),
                                        time_allowed
                                  )
            self.session.add(group_permission_p3)
            group_permission_p4 = Model.DbGroupPermissionParameter(
                                        group_permission,
                                        permission_type.get_parameter("priority"),
                                        priority
                                  )
            self.session.add(group_permission_p4)

            self.session.commit()
            return group_permission
        except IntegrityError:
            return None
                
    def grant_on_experiment_to_user(self, user, permission_type, permanent_id, date, comments, experiment, time_allowed, priority):
        try:
            user_permission = Model.DbUserPermission(
                                    user,
                                    permission_type.user_applicable,
                                    permanent_id,
                                    date,
                                    comments
                                )
            self.session.add(user_permission)
            user_permission_p1 = Model.DbUserPermissionParameter(
                                        user_permission,
                                        permission_type.get_parameter("experiment_permanent_id"),
                                        experiment.name
                                  )
            self.session.add(user_permission_p1)
            user_permission_p2 = Model.DbUserPermissionParameter(
                                        user_permission,
                                        permission_type.get_parameter("experiment_category_id"),
                                        experiment.category.name
                                  )
            self.session.add(user_permission_p2)
            user_permission_p3 = Model.DbUserPermissionParameter(
                                        user_permission,
                                        permission_type.get_parameter("time_allowed"),
                                        time_allowed
                                  )
            self.session.add(user_permission_p3)
            user_permission_p4 = Model.DbUserPermissionParameter(
                                        user_permission,
                                        permission_type.get_parameter("priority"),
                                        priority
                                  )
            self.session.add(user_permission_p4)

            self.session.commit()
            return user_permission
        except IntegrityError:
            return None
