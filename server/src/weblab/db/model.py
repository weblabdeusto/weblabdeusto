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
# Author: Jaime Irurzun <jaime.irurzun@gmail.com>
#

import datetime
import calendar

from voodoo.dbutil import get_table_kwargs

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, UniqueConstraint, Table
from sqlalchemy.orm import relation, backref
from sqlalchemy.ext.declarative import declarative_base

import voodoo.gen.coordinator.CoordAddress as CoordAddress

import weblab.login.db.dao.user as UserAuth

from weblab.data.dto.experiments import Experiment
from weblab.data.dto.experiments import ExperimentCategory
from weblab.data.dto.permissions import Permission, PermissionParameter, PermissionType
from weblab.data.experiments import ExperimentId, ExperimentUsage, FileSent, CommandSent
from weblab.data.command import Command, NullCommand
from weblab.data.dto.users import User
from weblab.data.dto.users import Role
from weblab.data.dto.users import Group
from weblab.data.dto.users import ExternalEntity
from weblab.data.dto.experiments import ExperimentUse


Base = declarative_base()

TABLE_KWARGS = get_table_kwargs()

def link_relation(entity, object_to_link, relation_attr, fk_field=None):
    """
    Links a ForeignKey field with an object.
    If the object has already been inserted, only the ForeignKey field is linked.
    If the object has not already been inserted, the relation is linked so as to force the insert.
    Convention: if no fk_field is provided, its name will be suposed to be exactly as the relation_attr followed by '_id'.
    """
    if ( object_to_link is not None ) and ( object_to_link.id is not None ):
        if fk_field is not None:
            setattr(entity, fk_field, object_to_link.id)
        else:
            setattr(entity, relation_attr+"_id", object_to_link.id)
    else:
        setattr(entity, relation_attr, object_to_link)


##############################################################################
# N<->M RELATIONAL TABLES
#

t_user_is_member_of = Table('UserIsMemberOf', Base.metadata,
    Column('user_id', Integer, ForeignKey('User.id'), primary_key=True),
    Column('group_id', Integer, ForeignKey('Group.id'), primary_key=True)
    )

t_ee_is_member_of = Table('ExternalEntityIsMemberOf', Base.metadata,
    Column('ee_id', Integer, ForeignKey('ExternalEntity.id'), primary_key=True),
    Column('group_id', Integer, ForeignKey('Group.id'), primary_key=True)
    )


##############################################################################
# USER AND GROUP DEFINITION
#

class DbRole(Base):
    __tablename__  = 'Role'
    __table_args__ = (UniqueConstraint('name'), TABLE_KWARGS)

    id   = Column(Integer, primary_key = True)
    name = Column(String(20), nullable = False)

    def __init__(self, name):
        super(DbRole, self).__init__()
        self.name = name

    def __repr__(self):
        return "DbRole(id = %r, name = '%s')" % (
            self.id,
            self.name
        )

    def to_dto(self):
        return Role(self.name)


class DbUser(Base):
    __tablename__  = 'User'
    __table_args__ = (UniqueConstraint('login'), TABLE_KWARGS)

    id        = Column(Integer, primary_key = True)
    login     = Column(String(32), nullable = False, index = True)
    full_name = Column(String(200), nullable = False)
    email     = Column(String(255), nullable = False)
    avatar    = Column(String(255))
    role_id   = Column(Integer, ForeignKey("Role.id"))

    role = relation("DbRole", backref=backref("users", order_by=id))

    def __init__(self, login, full_name, email, avatar=None, role=None):
        super(DbUser,self).__init__()
        self.login = login
        self.full_name = full_name
        self.email = email
        self.avatar = avatar
        link_relation(self, role, "role")

    def __repr__(self):
        return "DbUser(id = %r, login = '%s', full_name = '%s', email = '%s', avatar = '%s', role = %r)" % (
                self.id,
                self.login,
                self.full_name,
                self.email,
                self.avatar,
                self.role
            )

    def to_dto(self):
        return User(self.login, self.full_name, self.email, self.role.to_dto())


class DbAuthType(Base):
    __tablename__  = 'AuthType'
    __table_args__ = (UniqueConstraint('name'), TABLE_KWARGS)

    id   = Column(Integer, primary_key = True)
    name = Column(String(200), nullable = False, index = True)

    def __init__(self, name):
        super(DbAuthType, self).__init__()
        self.name = name

    def __repr__(self):
        return "DbAuthType(id = %r, name = '%s')" % (
            self.id,
            self.name
        )


class DbAuth(Base):
    __tablename__  = 'Auth'
    __table_args__ = (UniqueConstraint('auth_type_id', 'name'), UniqueConstraint('priority'), TABLE_KWARGS)

    id            = Column(Integer, primary_key = True)
    auth_type_id  = Column(Integer, ForeignKey("AuthType.id"), nullable = False)
    name          = Column(String(200), nullable = False)
    priority      = Column(Integer, nullable = False)
    configuration = Column(Text)

    auth_type = relation("DbAuthType", backref=backref("auths", order_by=id, cascade='all,delete'))

    def __init__(self, auth_type, name, priority, configuration=None):
        super(DbAuth, self).__init__()
        link_relation(self, auth_type, "auth_type")
        self.name = name
        self.priority = priority
        self.configuration = configuration

    def __repr__(self):
        return "DbAuth(id = %r, auth_type = %r, name = '%s', priority = %i, configuration = '%s')" % (
            self.id,
            self.auth_type,
            self.name,
            self.priority,
            self.configuration
        )

    def get_config_value(self, key):
        params = self.configuration.split(";")
        keys = [ param[:param.find("=")] for param in params ]
        values = [ param[param.find("=")+1:] for param in params ]
        return values[keys.index(key)]


class DbUserAuth(Base):
    __tablename__  = 'UserAuth'
    __table_args__ = (TABLE_KWARGS)

    id            = Column(Integer, primary_key = True)
    user_id       = Column(Integer, ForeignKey('User.id'), nullable = False, index = True)
    auth_id       = Column(Integer, ForeignKey('Auth.id'), nullable = False, index = True)
    configuration = Column(Text)

    user = relation("DbUser", backref=backref("auths", order_by=id, cascade='all,delete'))
    auth = relation("DbAuth", backref=backref("user_auths", order_by=id, cascade='all,delete'))

    def __init__(self, user, auth, configuration=None):
        super(DbUserAuth, self).__init__()
        link_relation(self, user, "user")
        link_relation(self, auth, "auth")
        self.configuration = configuration

    def __repr__(self):
        configuration_str = "None"
        if self.configuration is not None:
            configuration_str = ( "*".join("" for _ in self.configuration) )
        return "DbUserAuth(id = %r, user = %r, auth = %r, configuration = '%s')" % (
            self.id,
            self.user,
            self.auth,
            configuration_str
        )

    def to_business(self):
        return UserAuth.UserAuth.create_user_auth(self.auth.auth_type.name, self.auth.configuration) #TODO: Add DbUserAuth's configuration too


class DbExternalEntity(Base):
    __tablename__  = 'ExternalEntity'
    __table_args__ = (UniqueConstraint('name'), TABLE_KWARGS)

    id          = Column(Integer, primary_key = True)
    name        = Column(String(255), nullable = False)
    country     = Column(String(20), nullable = False)
    description = Column(Text, nullable = False)
    email       = Column(String(255), nullable = False)
    password    = Column(String(255), nullable = False)

    def __init__(self, name, country, description, email, password):
        super(DbExternalEntity, self).__init__()
        self.name = name
        self.country = country
        self.description = description
        self.email = email
        self.password = password # calculate hash?

    def __repr__(self):
        return "DbExternalEntity(id = %r, name = '%s', country = '%s', description = '%s', email = '%s')" % (
            self.id,
            self.name,
            self.country,
            self.description,
            self.email
        )

    def to_business(self):
        return ExternalEntity(self.id, self.name, self.country, self.description, self.email)

    def to_dto(self):
        return self.to_business() # Temporal


class DbGroup(Base):
    __tablename__  = 'Group'
    __table_args__ = (UniqueConstraint('parent_id', 'name'), TABLE_KWARGS)

    id        = Column(Integer, primary_key = True)
    name      = Column(String(250), nullable = False, index = True)
    parent_id = Column(Integer, ForeignKey("Group.id"), index = True)

    children = relation("DbGroup", backref=backref("parent", remote_side=id, cascade='all,delete'))
    users    = relation("DbUser", secondary=t_user_is_member_of, backref="groups")
    ees      = relation("DbExternalEntity", secondary=t_ee_is_member_of, backref="groups")

    def __init__(self, name, parent=None):
        super(DbGroup, self).__init__()
        self.name = name
        link_relation(self, parent, "parent")

    def __repr__(self):
        if self.parent is None:
            parent_str = "<None>"
        else:
            parent_str = "<" + self.parent.name + ">"
        return "DbGroup(id = %r, name = '%s', parent = '%s')" % (
            self.id,
            self.name,
            parent_str
        )

    def to_business_light(self):
        return Group(self.name, self.id)

    def to_dto(self):
        return self.to_business_light() # Temporal

##############################################################################
# EXPERIMENTS DEFINITION
#

class DbExperimentCategory(Base):
    __tablename__  = 'ExperimentCategory'
    __table_args__ = (UniqueConstraint('name'), TABLE_KWARGS)

    id   = Column(Integer, primary_key = True)
    name = Column(String(255), nullable = False, index = True)

    def __init__(self, name):
        super(DbExperimentCategory, self).__init__()
        self.name = name

    def __repr__(self):
        return "DbExperimentCategory(id = %r, name = '%s')" % (
            self.id,
            self.name
        )

    def to_business(self):
        return ExperimentCategory(self.name)


class DbExperiment(Base):
    __tablename__  = 'Experiment'
    __table_args__ = (UniqueConstraint('name', 'category_id'), TABLE_KWARGS)

    id          = Column(Integer, primary_key = True)
    name        = Column(String(255), nullable = False, index = True)
    category_id = Column(Integer, ForeignKey("ExperimentCategory.id"), nullable = False, index = True)
    start_date  = Column(DateTime, nullable = False)
    end_date    = Column(DateTime, nullable = False)

    category = relation("DbExperimentCategory", backref=backref("experiments", order_by=id, cascade='all,delete'))

    def __init__(self, name, category, start_date, end_date):
        super(DbExperiment, self).__init__()
        self.name = name
        link_relation(self, category, "category")
        self.start_date = start_date
        self.end_date = end_date

    def __repr__(self):
        return "DbExperiment(id = %r, name = '%s', category = %r, start_date = %r, end_date = %r)" % (
            self.id,
            self.name,
            self.category,
            self.start_date,
            self.end_date
        )

    def to_business(self):
        return Experiment(
            self.name,
            self.category.to_business(),
            self.start_date,
            self.end_date,
            self.id
            )

    def to_dto(self):
        return self.to_business() # Temporal


##############################################################################
# EXPERIMENT INSTANCE MEMBERSHIP DEFINITION
#

class DbUserUsedExperiment(Base):
    __tablename__  = 'UserUsedExperiment'
    __table_args__ = (TABLE_KWARGS)

    id               = Column(Integer, primary_key = True)
    user_id          = Column(Integer, ForeignKey("User.id"), nullable = False, index = True)
    experiment_id    = Column(Integer, ForeignKey("Experiment.id"), nullable = False)
    start_date       = Column(DateTime, nullable = False)
    start_date_micro = Column(Integer, nullable = False)
    end_date         = Column(DateTime)
    end_date_micro   = Column(Integer)
    origin           = Column(String(255), nullable = False)
    coord_address    = Column(String(255), nullable = False)
    reservation_id   = Column(String(50), index = True)

    user       = relation("DbUser", backref=backref("experiment_uses", order_by=id))
    experiment = relation("DbExperiment", backref=backref("user_uses", order_by=id))

    def __init__(self, user, experiment, start_date, origin, coord_address, reservation_id, end_date):
        super(DbUserUsedExperiment, self).__init__()
        link_relation(self, user, "user")
        link_relation(self, experiment, "experiment")
        self.start_date, self.start_date_micro = _timestamp_to_splitted_utc_datetime(start_date)
        self.set_end_date(end_date)
        self.origin = origin
        self.coord_address = coord_address
        self.reservation_id = reservation_id

    def set_end_date(self, end_date):
        self.end_date, self.end_date_micro = _timestamp_to_splitted_utc_datetime(end_date)

    def __repr__(self):
        return "DbUserUsedExperiment(id = %r, user = %r, experiment = %r, start_date = %r, start_date_micro = %i, end_date = %r, end_date_micro = %i, origin = '%s', coord_address = '%s', reservation_id = %r)" % (
            self.id,
            self.user,
            self.experiment,
            self.start_date,
            self.start_date_micro,
            self.end_date,
            self.end_date_micro,
            self.origin,
            self.coord_address,
            self.reservation_id
        )

    def to_business_light(self):
        usage = ExperimentUsage()
        usage.experiment_use_id = self.id
        usage.start_date        = _splitted_utc_datetime_to_timestamp(self.start_date, self.start_date_micro)
        usage.end_date          = _splitted_utc_datetime_to_timestamp(self.end_date, self.end_date_micro)
        usage.from_ip           = self.origin
        usage.reservation_id    = self.reservation_id
        usage.experiment_id     = ExperimentId(self.experiment.name, self.experiment.category.name)
        usage.coord_address     = CoordAddress.CoordAddress.translate_address(self.coord_address)
        
        request_info = {}
        for prop in self.properties:
            name  = prop.property_name.name
            value = prop.value
            request_info[name] = value
        
        usage.request_info = request_info
        return usage

    def to_business(self):
        usage = self.to_business_light()
        usage.commands   = [ command.to_business() for command in self.commands ]
        usage.sent_files = [ file.to_business() for file in self.files ]
        return usage

    def to_dto(self):
        use = ExperimentUse(
            self.start_date,
            self.end_date,
            self.experiment.to_dto(),
            self.user.to_dto(),
            self.origin,
            self.id
        )
        return use

#
# These properties will be added. The names will be "facebook", "mobile", "openid", "user.agent", etc.
#
class DbUserUsedExperimentProperty(Base):
    __tablename__   = 'UserUsedExperimentProperty'
    __table_args__  = (UniqueConstraint('name'), TABLE_KWARGS)

    id   = Column(Integer, primary_key = True)
    name = Column(String(255), nullable = False, index = True)

    def __init__(self, name, id = None):
        self.name = name
        self.id   = id

    def __repr__(self):
        return "DbUserUsedExperimentProperty(id = %r, name = %r)" % (self.id, self.name)

class DbUserUsedExperimentPropertyValue(Base):
    __tablename__  = 'UserUsedExperimentPropertyValue'
    __table_args__ = (UniqueConstraint('property_name_id', 'experiment_use_id'), TABLE_KWARGS)

    id                = Column(Integer, primary_key = True)
    property_name_id  = Column(Integer, ForeignKey("UserUsedExperimentProperty.id"), nullable = False)
    experiment_use_id = Column(Integer, ForeignKey("UserUsedExperiment.id"), nullable = False)
    value             = Column(String(255))

    property_name  = relation("DbUserUsedExperimentProperty", backref=backref("values",     order_by=id, cascade='all,delete'))
    experiment_use = relation("DbUserUsedExperiment",         backref=backref("properties", order_by=id, cascade='all,delete'))

    def __init__(self, value, property_name, experiment_use, id = None):
        self.id = id
        self.value = value
        self.property_name  = property_name
        self.experiment_use = experiment_use

    def __repr__(self):
        return "DbUserUsedExperimentPropertyValue(id = %r, value = %r, property_name_id = %r, experiment_use_id = %r)" % (
            self.id,
            self.value,
            self.property_name_id,
            self.experiment_use_id
        )

class DbUserFile(Base):
    __tablename__  = 'UserFile'
    __table_args__ = (TABLE_KWARGS)

    id                     = Column(Integer, primary_key = True)
    experiment_use_id      = Column(Integer, ForeignKey("UserUsedExperiment.id"), nullable = False)
    file_sent              = Column(String(255), nullable = False)
    file_hash              = Column(String(255), nullable = False)
    file_info              = Column(Text)
    response               = Column(Text)
    timestamp_before       = Column(DateTime, nullable = False)
    timestamp_before_micro = Column(Integer, nullable = False)
    timestamp_after        = Column(DateTime)
    timestamp_after_micro  = Column(Integer)

    experiment_use = relation("DbUserUsedExperiment", backref=backref("files", order_by=id, cascade='all,delete'))

    def __init__(self, experiment_use, file_sent, file_hash, timestamp_before, file_info=None, response=None, timestamp_after=None):
        super(DbUserFile, self).__init__()
        link_relation(self, experiment_use, "experiment_use")
        self.file_sent = file_sent
        self.file_hash = file_hash
        self.file_info = file_info
        self.response = response
        self.timestamp_before, self.timestamp_before_micro = _timestamp_to_splitted_utc_datetime(timestamp_before)
        self.set_timestamp_after(timestamp_after)

    def set_timestamp_after(self, timestamp_after):
        self.timestamp_after, self.timestamp_after_micro = _timestamp_to_splitted_utc_datetime(timestamp_after)

    def __repr__(self):
        return "DbUserFile(id = %r, experiment_use = %r, file_sent = '%s', file_hash = '%s', file_info = '%s', response = '%s', timestamp_before = %r, timestamp_before_micro = %i, timestamp_after = %r, timestamp_after_micro = %r)" % (
            self.id,
            self.experiment_use,
            self.file_sent,
            self.file_hash,
            self.file_info,
            self.response,
            self.timestamp_before,
            self.timestamp_before_micro,
            self.timestamp_after,
            self.timestamp_after_micro
        )

    def to_business(self):
        return FileSent(
            self.file_sent,
            self.file_hash,
            _splitted_utc_datetime_to_timestamp(self.timestamp_before, self.timestamp_before_micro),
            Command(self.response) if self.response is not None else NullCommand(),
            _splitted_utc_datetime_to_timestamp(self.timestamp_after, self.timestamp_after_micro),
            self.file_info
            )


class DbUserCommand(Base):
    __tablename__  = 'UserCommand'
    __table_args__ = (TABLE_KWARGS)

    id                     = Column(Integer, primary_key = True)
    experiment_use_id      = Column(Integer, ForeignKey("UserUsedExperiment.id"), nullable = False)
    command                = Column(Text, nullable = False)
    response               = Column(Text)
    timestamp_before       = Column(DateTime, nullable = False)
    timestamp_before_micro = Column(Integer, nullable = False)
    timestamp_after        = Column(DateTime)
    timestamp_after_micro  = Column(Integer)

    experiment_use = relation("DbUserUsedExperiment", backref=backref("commands", order_by=id, cascade='all,delete'))

    def __init__(self, experiment_use, command, timestamp_before, response=None, timestamp_after=None):
        super(DbUserCommand, self).__init__()
        link_relation(self, experiment_use, "experiment_use")
        self.command = command
        self.response = response
        self.timestamp_before, self.timestamp_before_micro = _timestamp_to_splitted_utc_datetime(timestamp_before)
        self.set_timestamp_after(timestamp_after)

    def set_timestamp_after(self, timestamp_after):
        self.timestamp_after, self.timestamp_after_micro = _timestamp_to_splitted_utc_datetime(timestamp_after)

    def __repr__(self):
        return "DbUserCommand(id = %r, experiment_use = %r, command = '%s', response = '%s', timestamp_before = %r, timestamp_before_micro = %i, timestamp_after = %r, timestamp_after_micro = %r)" % (
            self.id,
            self.experiment_use,
            self.command,
            self.response,
            self.timestamp_before,
            self.timestamp_before_micro,
            self.timestamp_after,
            self.timestamp_after_micro
        )

    def to_business(self):
        return CommandSent(
            Command(self.command) if self.command is not None else NullCommand(),
            _splitted_utc_datetime_to_timestamp(self.timestamp_before, self.timestamp_before_micro),
            Command(self.response) if self.response is not None else NullCommand(),
            _splitted_utc_datetime_to_timestamp(self.timestamp_after, self.timestamp_after_micro)
            )


class DbExternalEntityUsedExperiment(Base):
    __tablename__  = 'ExternalEntityUsedExperiment'
    __table_args__ = (TABLE_KWARGS)

    id               = Column(Integer, primary_key = True)
    ee_id            = Column(Integer, ForeignKey("ExternalEntity.id"), nullable = False)
    experiment_id    = Column(Integer, ForeignKey("Experiment.id"), nullable = False)
    start_date       = Column(DateTime, nullable = False)
    start_date_micro = Column(Integer, nullable = False)
    end_date         = Column(DateTime)
    end_date_micro   = Column(Integer)
    origin           = Column(String(255), nullable = False)
    coord_address    = Column(String(255), nullable = False)
    reservation_id   = Column(String(50))

    ee         = relation("DbExternalEntity", backref=backref("experiment_uses", order_by=id))
    experiment = relation("DbExperiment", backref=backref("ee_uses", order_by=id))

    def __init__(self, ee, experiment, start_date, origin, coord_address, reservation_id, end_date):
        super(DbExternalEntityUsedExperiment, self).__init__()
        link_relation(self, ee, "ee")
        link_relation(self, experiment, "experiment")
        self.start_date, self.start_date_micro = _timestamp_to_splitted_utc_datetime(start_date)
        self.end_date, self.end_date_micro = _timestamp_to_splitted_utc_datetime(end_date)
        self.reservation_id = reservation_id
        self.origin = origin
        self.coord_address = coord_address

    def __repr__(self):
        return "DbExternalEntityUsedExperiment(id = %r, ee = %r, experiment = %r, start_date = %r, start_date_micro = %i, end_date = %r, end_date_micro = %i, origin = '%s', coord_address = '%s', reservation_id = %r)" % (
            self.id,
            self.ee,
            self.experiment,
            self.start_date,
            self.start_date_micro,
            self.end_date,
            self.end_date_micro,
            self.origin,
            self.coord_address,
            self.reservation_id
        )

    def to_dto(self):
        use = ExperimentUse(
            _splitted_utc_datetime_to_timestamp(self.start_date, self.start_date_micro),
            _splitted_utc_datetime_to_timestamp(self.end_date, self.end_date_micro),
            self.experiment.to_dto(),
            self.ee.to_dto(),
            self.origin,
            self.id
        )
        return use


class DbExternalEntityFile(Base):
    __tablename__  = 'ExternalEntityFile'
    __table_args__ = (TABLE_KWARGS)

    id                     = Column(Integer, primary_key = True)
    experiment_use_id      = Column(Integer, ForeignKey("ExternalEntityUsedExperiment.id"), nullable = False)
    file_sent              = Column(String(255), nullable = False)
    file_hash              = Column(String(255), nullable = False)
    file_info              = Column(Text)
    response               = Column(Text)
    timestamp_before       = Column(DateTime, nullable = False)
    timestamp_before_micro = Column(Integer, nullable = False)
    timestamp_after        = Column(DateTime)
    timestamp_after_micro  = Column(Integer)

    experiment_use = relation("DbExternalEntityUsedExperiment", backref=backref("files", order_by=id, cascade='all,delete'))

    def __init__(self, experiment_use, file_sent, file_hash, timestamp_before, timestamp_before_micro, file_info=None, response=None, timestamp_after=None, timestamp_after_micro=None):
        super(DbExternalEntityFile, self).__init__()
        link_relation(self, experiment_use, "experiment_use")
        self.file_sent = file_sent
        self.file_hash = file_hash
        self.file_info = file_info
        self.response = response
        self.timestamp_before = timestamp_before
        self.timestamp_before_micro = timestamp_before_micro
        self.timestamp_after = timestamp_after
        self.timestamp_after_micro = timestamp_after_micro

    def __repr__(self):
        return "DbExternalEntityFile(id = %r, experiment_use = %r, file_sent = '%s', file_hash = '%s', file_info = '%s', response = '%s', timestamp_before = %r, timestamp_before_micro = %i, timestamp_after = %r, timestamp_after_micro = %r)" % (
            self.id,
            self.experiment_use,
            self.file_sent,
            self.file_hash,
            self.file_info,
            self.response,
            self.timestamp_before,
            self.timestamp_before_micro,
            self.timestamp_after,
            self.timestamp_after_micro
        )


class DbExternalEntityCommand(Base):
    __tablename__  = 'ExternalEntityCommand'
    __table_args__ = (TABLE_KWARGS)

    id                     = Column(Integer, primary_key = True)
    experiment_use_id      = Column(Integer, ForeignKey("ExternalEntityUsedExperiment.id"), nullable = False)
    command                = Column(Text, nullable = False)
    response               = Column(Text)
    timestamp_before       = Column(DateTime, nullable = False)
    timestamp_before_micro = Column(Integer, nullable = False)
    timestamp_after        = Column(DateTime)
    timestamp_after_micro  = Column(Integer)

    experiment_use = relation("DbExternalEntityUsedExperiment", backref=backref("commands", order_by=id, cascade='all,delete'))

    def __init__(self, experiment_use, command, timestamp_before, timestamp_before_micro, response=None, timestamp_after=None, timestamp_after_micro=None):
        super(DbExternalEntityCommand, self).__init__()
        link_relation(self, experiment_use, "experiment_use")
        self.command = command
        self.response = response
        self.timestamp_before = timestamp_before
        self.timestamp_before_micro = timestamp_before_micro
        self.timestamp_after = timestamp_after
        self.timestamp_after_micro = timestamp_after_micro

    def __repr__(self):
        return "DbExternalEntityCommand(id = %r, experiment_use = %r, command = '%s', response = '%s', timestamp_before = %r, timestamp_before_micro = %i, timestamp_after = %r, timestamp_after_micro = %r)" % (
            self.id,
            self.experiment_use,
            self.command,
            self.response,
            self.timestamp_before,
            self.timestamp_before_micro,
            self.timestamp_after,
            self.timestamp_after_micro
        )


##############################################################################
# USER PERMISSIONS
#

class DbPermissionType(Base):
    __tablename__  = 'PermissionType'
    __table_args__ = (UniqueConstraint('name'), TABLE_KWARGS)

    id                  = Column(Integer, primary_key = True)
    name                = Column(String(255), nullable = False)
    description         = Column(Text, nullable = False)
    user_applicable_id  = Column(Integer, ForeignKey("UserApplicablePermissionType.id"))
    role_applicable_id  = Column(Integer, ForeignKey("RoleApplicablePermissionType.id"))
    group_applicable_id = Column(Integer, ForeignKey("GroupApplicablePermissionType.id"))
    ee_applicable_id    = Column(Integer, ForeignKey("ExternalEntityApplicablePermissionType.id"))

    # I think there's a mistake here: this creates 1-N relationships, while they should be 1-1.
    # A quick search made me think that we're not using backref properly in this case, but now
    # it's not time to change this, so it'll be in a future upgrading version 0:-) (Jaime I, Oct 6th 2010)
    user_applicable  = relation("DbUserApplicablePermissionType", backref=backref("permission_type", order_by=id))
    role_applicable  = relation("DbRoleApplicablePermissionType", backref=backref("permission_type", order_by=id))
    group_applicable = relation("DbGroupApplicablePermissionType", backref=backref("permission_type", order_by=id))
    ee_applicable    = relation("DbExternalEntityApplicablePermissionType", backref=backref("permission_type", order_by=id))

    def __init__(self, name, description, user_applicable=False, role_applicable=False, group_applicable=False, ee_applicable=False):
        super(DbPermissionType, self).__init__()
        self.name = name
        self.description = description
        if user_applicable:
            link_relation(self, DbUserApplicablePermissionType(), "user_applicable")
        if role_applicable:
            link_relation(self, DbRoleApplicablePermissionType(), "role_applicable")
        if group_applicable:
            link_relation(self, DbGroupApplicablePermissionType(), "group_applicable")
        if ee_applicable:
            link_relation(self, DbExternalEntityApplicablePermissionType(), "ee_applicable")

    def __repr__(self):
        return "DbPermissionType(id = %r, name = '%s', description = '%s', user_applicable = %r, role_applicable = %r, group_applicable = %r, ee_applicable = %r)" % (
            self.id,
            self.name,
            self.description,
            self.user_applicable,
            self.role_applicable,
            self.group_applicable,
            self.ee_applicable
        )

    def get_parameter(self, parameter_name):
        return [ param for param in self.parameters if param.name == parameter_name ][0]

    def to_dto(self):
        ptype = PermissionType(
            self.name,
            self.description,
            self.user_applicable,
            self.role_applicable,
            self.group_applicable,
            self.ee_applicable)
        return ptype



class DbPermissionTypeParameter(Base):
    __tablename__  = 'PermissionTypeParameter'
    __table_args__ = (UniqueConstraint('permission_type_id', 'name'), TABLE_KWARGS)

    id                 = Column(Integer, primary_key = True)
    permission_type_id = Column(Integer, ForeignKey("PermissionType.id"), nullable = False)
    name               = Column(String(255), nullable = False)
    datatype           = Column(String(255), nullable = False)
    description        = Column(String(255), nullable = False)

    permission_type = relation("DbPermissionType", backref=backref("parameters", order_by=id, cascade='all,delete'))

    def __init__(self, permission_type, name, datatype, description):
        super(DbPermissionTypeParameter, self).__init__()
        link_relation(self, permission_type, "permission_type")
        self.name = name
        self.datatype = datatype
        self.description = description

    def __repr__(self):
        return "DbPermissionTypeParameter(id = %r, permission_type = %r, name = '%s', datatype = '%s', description = '%s')" % (
            self.id,
            self.permission_type,
            self.name,
            self.datatype,
            self.description
        )


class DbUserApplicablePermissionType(Base):
    __tablename__  = 'UserApplicablePermissionType'
    __table_args__ = (TABLE_KWARGS)

    id = Column(Integer, primary_key = True)

    def __init__(self):
        super(DbUserApplicablePermissionType, self).__init__()

    def __repr__(self):
        return "DbUserApplicablePermissionType(id = %r)" % (
            self.id
        )


class DbUserPermission(Base):
    __tablename__  = 'UserPermission'
    __table_args__ = (UniqueConstraint('permanent_id'), TABLE_KWARGS)

    id                            = Column(Integer, primary_key = True)
    user_id                       = Column(Integer, ForeignKey("User.id"), nullable = False)
    applicable_permission_type_id = Column(Integer, ForeignKey("UserApplicablePermissionType.id"), nullable = False)
    permanent_id                  = Column(String(255), nullable = False)
    date                          = Column(DateTime, nullable = False)
    comments                      = Column(Text)

    user                       = relation("DbUser", backref=backref("permissions", order_by=id, cascade='all,delete'))
    applicable_permission_type = relation("DbUserApplicablePermissionType", backref=backref("permissions", order_by=id, cascade='all,delete'))

    def __init__(self, user, applicable_permission_type, permanent_id, date, comments=None):
        super(DbUserPermission, self).__init__()
        link_relation(self, user, "user")
        link_relation(self, applicable_permission_type, "applicable_permission_type")
        self.permanent_id = permanent_id
        self.date = date
        self.comments = comments

    def __repr__(self):
        return "DbUserPermission(id = %r, user = %r, applicable_permission_type = %r, permanent_id = '%s', date = %r, comments = '%s')" % (
            self.id,
            self.user,
            self.applicable_permission_type,
            self.permanent_id,
            self.date,
            self.comments
        )

    def get_permission_type(self):
        return self.applicable_permission_type.permission_type[0]

    def get_parameter(self, parameter_name):
        return [ param for param in self.parameters if param.permission_type_parameter.name == parameter_name ][0]

    def to_dto(self):
        permission = Permission(
            self.applicable_permission_type.permission_type[0].name
        )
        for param in self.parameters:
            permission.add_parameter(param.to_dto())
        return permission


class DbUserPermissionParameter(Base):
    __tablename__  = 'UserPermissionParameter'
    __table_args__ = (UniqueConstraint('permission_id', 'permission_type_parameter_id'), TABLE_KWARGS)

    id                           = Column(Integer, primary_key = True)
    permission_id                = Column(Integer, ForeignKey("UserPermission.id"), nullable = False)
    permission_type_parameter_id = Column(Integer, ForeignKey("PermissionTypeParameter.id"), nullable = False)
    value                        = Column(Text)

    permission                = relation("DbUserPermission", backref=backref("parameters", order_by=id, cascade='all,delete'))
    permission_type_parameter = relation("DbPermissionTypeParameter", backref=backref("user_values", order_by=id, cascade='all,delete'))

    def __init__(self, permission, permission_type_parameter, value=None):
        super(DbUserPermissionParameter, self).__init__()
        link_relation(self, permission, "permission")
        link_relation(self, permission_type_parameter, "permission_type_parameter")
        self.value = value

    def __repr__(self):
        return "DbUserPermissionParameter(id = %r, permission = %r, permission_type_parameter = %r, value = '%s')" % (
            self.id,
            self.permission,
            self.permission_type_parameter,
            self.value
        )

    def get_name(self):
        return self.permission_type_parameter.name

    def get_datatype(self):
        return self.permission_type_parameter.datatype

    def to_dto(self):
        return PermissionParameter(
                    self.permission_type_parameter.name,
                    self.permission_type_parameter.datatype,
                    self.value
                )

class DbRoleApplicablePermissionType(Base):
    __tablename__  = 'RoleApplicablePermissionType'
    __table_args__ = (TABLE_KWARGS)

    id = Column(Integer, primary_key = True)

    def __init__(self):
        super(DbRoleApplicablePermissionType, self).__init__()

    def __repr__(self):
        return "DbRoleApplicablePermissionType(id = %r)" % (
            self.id
        )

class DbRolePermission(Base):
    __tablename__  = 'RolePermission'
    __table_args__ = (UniqueConstraint('permanent_id'), TABLE_KWARGS)

    id                            = Column(Integer, primary_key = True)
    role_id                       = Column(Integer, ForeignKey("Role.id"), nullable = False)
    applicable_permission_type_id = Column(Integer, ForeignKey("RoleApplicablePermissionType.id"), nullable = False)
    permanent_id                  = Column(String(255), nullable = False)
    date                          = Column(DateTime, nullable = False)
    comments                      = Column(Text)

    role                       = relation("DbRole", backref=backref("permissions", order_by=id, cascade='all,delete'))
    applicable_permission_type = relation("DbRoleApplicablePermissionType", backref=backref("permissions", order_by=id, cascade='all,delete'))

    def __init__(self, role, applicable_permission_type, permanent_id, date, comments=None):
        super(DbRolePermission, self).__init__()
        link_relation(self, role, "role")
        link_relation(self, applicable_permission_type, "applicable_permission_type")
        self.permanent_id = permanent_id
        self.date = date
        self.comments = comments

    def __repr__(self):
        return "DbRolePermission(id = %r, role = %r, applicable_permission_type = %r, permanent_id = '%s', date = %r, comments = '%s')" % (
            self.id,
            self.role,
            self.applicable_permission_type,
            self.permanent_id,
            self.date,
            self.comments
        )

    def get_permission_type(self):
        return self.applicable_permission_type.permission_type[0]

    def get_parameter(self, parameter_name):
        return [ param for param in self.parameters if param.permission_type_parameter.name == parameter_name ][0]

    def to_dto(self):
        permission = Permission(
            self.applicable_permission_type.permission_type[0].name
        )
        for param in self.parameters:
            permission.add_parameter(param.to_dto())
        return permission


class DbRolePermissionParameter(Base):
    __tablename__  = 'RolePermissionParameter'
    __table_args__ = (UniqueConstraint('permission_id', 'permission_type_parameter_id'), TABLE_KWARGS)

    id                           = Column(Integer, primary_key = True)
    permission_id                = Column(Integer, ForeignKey("RolePermission.id"), nullable = False)
    permission_type_parameter_id = Column(Integer, ForeignKey("PermissionTypeParameter.id"), nullable = False)
    value                        = Column(Text)

    permission                = relation("DbRolePermission", backref=backref("parameters", order_by=id, cascade='all,delete'))
    permission_type_parameter = relation("DbPermissionTypeParameter", backref=backref("role_values", order_by=id, cascade='all,delete'))

    def __init__(self, permission, permission_type_parameter, value=None):
        super(DbRolePermissionParameter, self).__init__()
        link_relation(self, permission, "permission")
        link_relation(self, permission_type_parameter, "permission_type_parameter")
        self.value = value

    def __repr__(self):
        return "DbRolePermissionParameter(id = %r, permission = %r, permission_type_parameter = %r, value = '%s')" % (
            self.id,
            self.permission,
            self.permission_type_parameter,
            self.value
        )

    def get_name(self):
        return self.permission_type_parameter.name

    def get_datatype(self):
        return self.permission_type_parameter.datatype

    def to_dto(self):
        return PermissionParameter(
                    self.permission_type_parameter.name,
                    self.permission_type_parameter.datatype,
                    self.value
                )


class DbGroupApplicablePermissionType(Base):
    __tablename__  = 'GroupApplicablePermissionType'
    __table_args__ = (TABLE_KWARGS)

    id = Column(Integer, primary_key = True)

    def __init__(self):
        super(DbGroupApplicablePermissionType, self).__init__()

    def __repr__(self):
        return "DbGroupApplicablePermissionType(id = %r)" % (
            self.id
        )


class DbGroupPermission(Base):
    __tablename__  = 'GroupPermission'
    __table_args__ = (UniqueConstraint('permanent_id'), TABLE_KWARGS)

    id                            = Column(Integer, primary_key = True)
    group_id                      = Column(Integer, ForeignKey("Group.id"), nullable = False)
    applicable_permission_type_id = Column(Integer, ForeignKey("GroupApplicablePermissionType.id"), nullable = False)
    permanent_id                  = Column(String(255), nullable = False)
    date                          = Column(DateTime, nullable = False)
    comments                      = Column(Text)

    group                      = relation("DbGroup", backref=backref("permissions", order_by=id, cascade='all,delete'))
    applicable_permission_type = relation("DbGroupApplicablePermissionType", backref=backref("permissions", order_by=id, cascade='all,delete'))

    def __init__(self, group, applicable_permission_type, permanent_id, date, comments=None):
        super(DbGroupPermission, self).__init__()
        link_relation(self, group, "group")
        link_relation(self, applicable_permission_type, "applicable_permission_type")
        self.permanent_id = permanent_id
        self.date = date
        self.comments = comments

    def __repr__(self):
        return "DbGroupPermission(id = %r, group = %r, applicable_permission_type = %r, permanent_id = '%s', date = %r, comments = '%s')" % (
            self.id,
            self.group,
            self.applicable_permission_type,
            self.permanent_id,
            self.date,
            self.comments
        )

    def get_permission_type(self):
        return self.applicable_permission_type.permission_type[0]

    def get_parameter(self, parameter_name):
        return [ param for param in self.parameters if param.permission_type_parameter.name == parameter_name ][0]

    def to_dto(self):
        permission = Permission(
            self.applicable_permission_type.permission_type[0].name
        )
        for param in self.parameters:
            permission.add_parameter(param.to_dto())
        return permission


class DbGroupPermissionParameter(Base):
    __tablename__  = 'GroupPermissionParameter'
    __table_args__ = (UniqueConstraint('permission_id', 'permission_type_parameter_id'), TABLE_KWARGS)

    id                           = Column(Integer, primary_key = True)
    permission_id                = Column(Integer, ForeignKey("GroupPermission.id"), nullable = False)
    permission_type_parameter_id = Column(Integer, ForeignKey("PermissionTypeParameter.id"), nullable = False)
    value                        = Column(Text)

    permission                = relation("DbGroupPermission", backref=backref("parameters", order_by=id, cascade='all,delete'))
    permission_type_parameter = relation("DbPermissionTypeParameter", backref=backref("group_values", order_by=id, cascade='all,delete'))

    def __init__(self, permission, permission_type_parameter, value=None):
        super(DbGroupPermissionParameter, self).__init__()
        link_relation(self, permission, "permission")
        link_relation(self, permission_type_parameter, "permission_type_parameter")
        self.value = value

    def __repr__(self):
        return "DbGroupPermissionParameter(id = %r, permission = %r, permission_type_parameter = %r, value = '%s')" % (
            self.id,
            self.permission,
            self.permission_type_parameter,
            self.value
        )

    def get_name(self):
        return self.permission_type_parameter.name

    def get_datatype(self):
        return self.permission_type_parameter.datatype

    def to_dto(self):
        return PermissionParameter(
                    self.permission_type_parameter.name,
                    self.permission_type_parameter.datatype,
                    self.value
                )


class DbExternalEntityApplicablePermissionType(Base):
    __tablename__  = 'ExternalEntityApplicablePermissionType'
    __table_args__ = (TABLE_KWARGS)

    id = Column(Integer, primary_key = True)

    def __init__(self):
        super(DbExternalEntityApplicablePermissionType, self).__init__()

    def __repr__(self):
        return "DbExternalEntityApplicablePermissionType(id = %r)" % (
            self.id
        )

class DbExternalEntityPermission(Base):
    __tablename__  = 'ExternalEntityPermission'
    __table_args__ = (UniqueConstraint('permanent_id'), TABLE_KWARGS)

    id                            = Column(Integer, primary_key = True)
    ee_id                         = Column(Integer, ForeignKey("ExternalEntity.id"), nullable = False)
    applicable_permission_type_id = Column(Integer, ForeignKey("ExternalEntityApplicablePermissionType.id"), nullable = False)
    permanent_id                  = Column(String(255), nullable = False)
    date                          = Column(DateTime, nullable = False)
    comments                      = Column(Text)

    ee                         = relation("DbExternalEntity", backref=backref("permissions", order_by=id, cascade='all,delete'))
    applicable_permission_type = relation("DbExternalEntityApplicablePermissionType", backref=backref("permissions", order_by=id, cascade='all,delete'))

    def __init__(self, ee, applicable_permission_type, permanent_id, date, comments=None):
        super(DbExternalEntityPermission, self).__init__()
        link_relation(self, ee, "ee")
        link_relation(self, applicable_permission_type, "applicable_permission_type")
        self.permanent_id = permanent_id
        self.date = date
        self.comments = comments

    def __repr__(self):
        return "DbExternalEntityPermission(id = %r, ee = %r, applicable_permission_type = %r, permanent_id = '%s', date = %r, comments = '%s')" % (
            self.id,
            self.ee,
            self.applicable_permission_type,
            self.permanent_id,
            self.date,
            self.comments
        )

    def get_permission_type(self):
        return self.applicable_permission_type.permission_type[0]

    def get_parameter(self, parameter_name):
        return [ param for param in self.parameters if param.permission_type_parameter.name == parameter_name ][0]

    def to_dto(self):
        permission = Permission(
            self.applicable_permission_type.permission_type[0].name
        )
        for param in self.parameters:
            permission.add_parameter(param.to_dto())
        return permission


class DbExternalEntityPermissionParameter(Base):
    __tablename__  = 'ExternalEntityPermissionParameter'
    __table_args__ = (UniqueConstraint('permission_id', 'permission_type_parameter_id'), TABLE_KWARGS)

    id                           = Column(Integer, primary_key = True)
    permission_id                = Column(Integer, ForeignKey("ExternalEntityPermission.id"), nullable = False)
    permission_type_parameter_id = Column(Integer, ForeignKey("PermissionTypeParameter.id"), nullable = False)
    value                        = Column(Text)

    permission                = relation("DbExternalEntityPermission", backref=backref("parameters", order_by=id, cascade='all,delete'))
    permission_type_parameter = relation("DbPermissionTypeParameter", backref=backref("ee_values", order_by=id, cascade='all,delete'))

    def __init__(self, permission, permission_type_parameter, value=None):
        super(DbExternalEntityPermissionParameter, self).__init__()
        link_relation(self, permission, "permission")
        link_relation(self, permission_type_parameter, "permission_type_parameter")
        self.value = value

    def __repr__(self):
        return "DbExternalEntityPermissionParameter(id = %r, permission = %r, permission_type_parameter = %r, value = '%s')" % (
            self.id,
            self.permission,
            self.permission_type_parameter,
            self.value
        )

    def get_name(self):
        return self.permission_type_parameter.name

    def get_datatype(self):
        return self.permission_type_parameter.datatype

    def to_dto(self):
        return PermissionParameter(
                    self.permission_type_parameter.name,
                    self.permission_type_parameter.datatype,
                    self.value
                )


def _splitted_utc_datetime_to_timestamp(dt, ms):
    if dt is not None:
        return calendar.timegm(dt.utctimetuple()) + ms / 1e6
    else:
        return None

def _timestamp_to_splitted_utc_datetime(timestamp):
    if timestamp is not None:
        dt = datetime.datetime.utcfromtimestamp(timestamp)
        return dt, dt.microsecond
    else:
        return None, None
