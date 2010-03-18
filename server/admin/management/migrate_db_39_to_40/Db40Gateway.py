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

import sys, os
sys.path.append(os.sep.join(("..","..","..","src")))

import libraries

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
        engine = create_engine(connection_url, echo=False)
        metadata = Model.Base.metadata
        metadata.drop_all(engine)
        metadata.create_all(engine)         
        self.Session = sessionmaker(bind=engine)
        self.session = self.Session()
            
    def insert_experiment_category(self, id, name):
        experiment_category = Model.DbExperimentCategory(name=name)
        self.session.add(experiment_category)
        self.session.commit()
        return experiment_category
            
    def insert_experiment(self, id, category_id, start_date, end_date, name):
        category = self.session.query(Model.DbExperimentCategory).filter_by(id=category_id).one()
        experiment = Model.DbExperiment(name, category, start_date, end_date)
        experiment.id = id
        self.session.add(experiment)
        self.session.commit()
        return experiment
            
    def insert_role(self, id, name):
        o = Model.DbRole(name)
        o.id = id
        self.session.add(o)
        self.session.commit()
        return o
            
    def insert_group(self, id, name):
        o = Model.DbGroup(name)
        o.id = id
        self.session.add(o)
        self.session.commit()
        return o
            
    def insert_permission_type(self, id, name, description):
        # Attention! user_applicable, group_applicable, etc, are being forced since we don't have
        # any other permission_type than 'experiment_allowed' and this script is only for us.
        o = Model.DbPermissionType(name, description, user_applicable=True, role_applicable=False, group_applicable=True, ee_applicable=True)
        o.id = id
        self.session.add(o)
        self.session.commit()
        return o
            
    def insert_permission_type_parameter(self, id, name, datatype, description, permission_type_id):
        permission_type = self.session.query(Model.DbPermissionType).filter_by(id=permission_type_id).one()
        o = Model.DbPermissionTypeParameter(permission_type, name, datatype, description)
        o.id = id
        self.session.add(o)
        self.session.commit()
        return o
            
    def insert_group_permission(self, id, group_id, permission_type_id, date, name, comments):
        group = self.session.query(Model.DbGroup).filter_by(id=group_id).one()
        permission_type = self.session.query(Model.DbPermissionType).filter_by(id=permission_type_id).one()
        o = Model.DbGroupPermission(group, permission_type.group_applicable, name, date, comments)
        o.id = id
        self.session.add(o)
        self.session.commit()
        return o
            
    def insert_group_permission_parameter(self, id, group_permission_id, permission_type_parameter_id, value):
        group_permission = self.session.query(Model.DbGroupPermission).filter_by(id=group_permission_id).one()
        permission_type_parameter = self.session.query(Model.DbPermissionTypeParameter).filter_by(id=permission_type_parameter_id).one()
        o = Model.DbGroupPermissionParameter(group_permission, permission_type_parameter, value)
        o.id = id
        self.session.add(o)
        self.session.commit()
        return o
            
    def insert_auth_type(self, id, name):
        o = Model.DbAuthType(name)
        o.id = id
        self.session.add(o)
        self.session.commit()
        return o
            
    def insert_auth(self, id, auth_type_id, name, configuration, priority):
        auth_type = self.session.query(Model.DbAuthType).filter_by(id=auth_type_id).one()
        o = Model.DbAuth(auth_type, name, priority, configuration)
        o.id = id
        self.session.add(o)
        self.session.commit()
        return o
            
    def insert_user_auth(self, user_id, auth_id, configuration):
        user = self.session.query(Model.DbUser).filter_by(id=user_id).one()
        auth = self.session.query(Model.DbAuth).filter_by(id=auth_id).one()
        o = Model.DbUserAuth(user, auth, configuration)
        self.session.add(o)
        self.session.commit()
        return o
            
    def insert_user(self, id, login, full_name, email, role_id):
        role = self.session.query(Model.DbRole).filter_by(id=role_id).one()
        o = Model.DbUser(login, full_name, email, None, role=role)
        o.id = id
        self.session.add(o)
        self.session.commit()
        return o
            
    def insert_user_permission(self, id, user_id, permission_type_id, date, name, comments):
        user = self.session.query(Model.DbUser).filter_by(id=user_id).one()
        permission_type = self.session.query(Model.DbPermissionType).filter_by(id=permission_type_id).one()
        o = Model.DbUserPermission(user, permission_type.user_applicable, name, date, comments)
        o.id = id
        self.session.add(o)
        self.session.commit()
        return o
            
    def insert_user_permission_parameter(self, id, user_permission_id, permission_type_parameter_id, value):
        user_permission = self.session.query(Model.DbUserPermission).filter_by(id=user_permission_id).one()
        permission_type_parameter = self.session.query(Model.DbPermissionTypeParameter).filter_by(id=permission_type_parameter_id).one()
        o = Model.DbUserPermissionParameter(user_permission, permission_type_parameter, value)
        o.id = id
        self.session.add(o)
        self.session.commit()
        return o    
            
    def insert_user_is_member_of(self, user_id, group_id):
        user = self.session.query(Model.DbUser).filter_by(id=user_id).one()
        group = self.session.query(Model.DbGroup).filter_by(id=group_id).one()
        group.users.append(user)
        self.session.commit()
        return group, user
            
    def insert_user_used_experiment(self, id, user_id, start_date, start_date_micro, end_date, end_date_micro, origin, experiment_id, coord_address):
        user = self.session.query(Model.DbUser).filter_by(id=user_id).one()
        experiment = self.session.query(Model.DbExperiment).filter_by(id=experiment_id).one()
        o = Model.DbUserUsedExperiment(user,
                         experiment,
                         Model._splitted_utc_datetime_to_timestamp(start_date, start_date_micro),
                         origin,
                         coord_address,
                         Model._splitted_utc_datetime_to_timestamp(end_date, end_date_micro)
                         )
        o.id = id
        self.session.add(o)
        self.session.commit()
        return o
            
    def insert_user_command(self, id, user_used_experiment_id, command, response, timestamp_before, timestamp_before_micro, timestamp_after, timestamp_after_micro):
        user_used_experiment = self.session.query(Model.DbUserUsedExperiment).filter_by(id=user_used_experiment_id).one()
        o = Model.DbUserCommand(user_used_experiment,
                                command,
                                Model._splitted_utc_datetime_to_timestamp(timestamp_before, timestamp_before_micro),
                                response,
                                Model._splitted_utc_datetime_to_timestamp(timestamp_after, timestamp_after_micro)
                                )
        o.id = id
        self.session.add(o)
        self.session.commit()
        return o
            
    def insert_user_file(self, id, user_used_experiment_id, file_sent, file_hash, response, timestamp_before, timestamp_before_micro, timestamp_after, timestamp_after_micro, file_info):
        user_used_experiment = self.session.query(Model.DbUserUsedExperiment).filter_by(id=user_used_experiment_id).one()
        o = Model.DbUserFile(user_used_experiment,
                             file_sent,
                             file_hash,
                             Model._splitted_utc_datetime_to_timestamp(timestamp_before, timestamp_before_micro),
                             file_info,
                             response,
                             Model._splitted_utc_datetime_to_timestamp(timestamp_after, timestamp_after_micro)
                             )
        o.id = id
        self.session.add(o)
        self.session.commit()
        return o
    
    def update_auth_config_field(self, old_config, new_config):
        auth = self.session.query(Model.DbAuth).filter_by(configuration=old_config).one()
        auth.configuration = new_config
        self.session.commit()
        return auth