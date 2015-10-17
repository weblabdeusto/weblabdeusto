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
#         Pablo Orduña <pablo@ordunya.com>
#
from __future__ import print_function, unicode_literals

import datetime
import calendar
import traceback
import pickle

from voodoo.dbutil import get_table_kwargs

from sqlalchemy import Column, Boolean, Integer, BigInteger, String, DateTime, Date, Text, ForeignKey, UniqueConstraint, Table, Index, Unicode, UnicodeText
from sqlalchemy.orm import backref, relationship
from sqlalchemy.ext.declarative import declarative_base

from voodoo.gen import CoordAddress

from weblab.core.login.simple import create_user_auth

from weblab.data.dto.experiments import Experiment, ExperimentClient, ExperimentCategory
from weblab.data.dto.permissions import Permission, PermissionParameter
from weblab.data.experiments import ExperimentId, ExperimentUsage, FileSent, CommandSent
from weblab.data.command import Command, NullCommand
from weblab.data.dto.users import User
from weblab.data.dto.users import Role
from weblab.data.dto.users import Group
from weblab.data.dto.experiments import ExperimentUse

import weblab.permissions as permissions

Base = declarative_base()

TABLE_KWARGS = get_table_kwargs()

class AlembicVersion(Base):
    """ Alembic is a database version manager for SQLAlchemy. This class
    represents the internal way of Alembic for managing versions.
    """
    __tablename__ = 'alembic_version'
    
    version_num = Column(String(32), nullable = False, primary_key = True)

    def __init__(self, version_num):
        self.version_num = version_num

##############################################################################
# N<->M RELATIONAL TABLES
#

t_user_is_member_of = Table('UserIsMemberOf', Base.metadata,
    Column('user_id', Integer, ForeignKey('User.id'), primary_key=True),
    Column('group_id', Integer, ForeignKey('Group.id'), primary_key=True)
    )

##############################################################################
# 
# SERVER PROPERTIES
# 

class DbServerProperties(Base):
    __tablename__ = 'ServerProperties'

    id = Column(Integer, primary_key = True)
    name = Column(Unicode(50), nullable = False, index = True, unique = True)
    _value = Column(UnicodeText) # pickle object, in base64. Max: 64 KB

    def __init__(self, name, value):
        super(DbServerProperties, self).__init__()
        self.name = name
        self.value = value

    @property
    def value(self):
        if self._value is None:
            return None
        return pickle.loads(self._value.decode('base64'))

    @value.setter
    def value(self, value):
        if value is None:
            self._value = None
        else:
            serialized = pickle.dumps(value)
            self._value = serialized.encode('base64')

    def __unicode__(self):
        return u"%s = %r" % (self.name, self.value)

    def __repr__(self):
        return "DbServerProperties(%r, %r)" % (self.name, self. value)

##############################################################################
# 
# CLIENT PROPERTIES
# 

class DbClientProperties(Base):
    __tablename__ = 'ClientProperties'

    id = Column(Integer, primary_key = True)
    name = Column(Unicode(50), nullable = False, index = True, unique = True)
    _value = Column(UnicodeText) # pickle object, in base64. Max: 64 KB

    def __init__(self, name, value):
        super(DbClientProperties, self).__init__()
        self.name = name
        self.value = value

    @property
    def value(self):
        if self._value is None:
            return None
        return pickle.loads(self._value.decode('base64'))

    @value.setter
    def value(self, value):
        if value is None:
            self._value = None
        else:
            serialized = pickle.dumps(value)
            self._value = serialized.encode('base64').decode('utf-8')

    def __unicode__(self):
        return u"%s = %r" % (self.name, self.value)

    def __repr__(self):
        return "DbClientProperties(%r, %r)" % (self.name, self. value)


class DbLocationCache(Base):
    __tablename__  = 'LocationCache'
    
    id = Column(Integer, primary_key = True)
    ip = Column(Unicode(64), index = True, nullable = False)
    lookup_time = Column(DateTime, index = True, nullable = False)
    hostname = Column(Unicode(255), index = True)
    city = Column(Unicode(255), index = True)
    country = Column(Unicode(255), index = True)
    most_specific_subdivision = Column(Unicode(255), index = True)

    def __init__(self, ip, lookup_time, hostname, city = None, country = None, most_specific_subdivision = None):
        self.ip = ip
        self.lookup_time = lookup_time
        self.hostname = hostname
        self.city = city
        self.country = country
        self.most_specific_subdivision = most_specific_subdivision

##############################################################################
# USER AND GROUP DEFINITION
#

class DbRole(Base):
    __tablename__  = 'Role'
    __table_args__ = (UniqueConstraint('name'), TABLE_KWARGS)

    id   = Column(Integer, primary_key = True)
    name = Column(Unicode(20), nullable = False)

    def __init__(self, name = None):
        super(DbRole, self).__init__()
        self.name = name

    def __repr__(self):
        return "DbRole(id = %r, name = %r)" % (
            self.id,
            self.name
        )

    def __unicode__(self):
        return self.name

    def to_dto(self):
        return Role(self.name)


class DbUser(Base):
    __tablename__  = 'User'
    __table_args__ = (UniqueConstraint('login'), TABLE_KWARGS)

    id        = Column(Integer, primary_key = True)
    login     = Column(Unicode(32), nullable = False, index = True)
    full_name = Column(Unicode(200), nullable = False, index = True)
    email     = Column(Unicode(255), nullable = False, index = True)
    avatar    = Column(Unicode(255))
    role_id   = Column(Integer, ForeignKey("Role.id"))

    role      = relationship("DbRole", backref=backref("users", order_by=id))
    groups    = relationship("DbGroup", secondary=t_user_is_member_of)

    def __init__(self, login = None, full_name = None, email = None, avatar=None, role=None):
        super(DbUser,self).__init__()
        self.login = login
        self.full_name = full_name
        self.email = email
        self.avatar = avatar
        self.role = role

    def __repr__(self):
        user_repr = "DbUser(id = %r, login = %r, full_name = %r, email = %r, avatar = %r, role = %r)" % (
                self.id,
                self.login,
                self.full_name,
                self.email,
                self.avatar,
                self.role
            )
        if isinstance(user_repr, unicode):
            user_repr = user_repr.encode('utf-8')
        return user_repr

    def __unicode__(self):
        return self.login

    def to_dto(self):
        return User(self.login, self.full_name, self.email, self.role.to_dto())


class DbAuthType(Base):
    __tablename__  = 'AuthType'
    __table_args__ = (UniqueConstraint('name'), TABLE_KWARGS)

    id   = Column(Integer, primary_key = True)
    name = Column(Unicode(200), nullable = False, index = True)

    def __init__(self, name = None):
        super(DbAuthType, self).__init__()
        self.name = name

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return "DbAuthType(id = %r, name = %r)" % (
            self.id,
            self.name
        )


class DbAuth(Base):
    __tablename__  = 'Auth'
    __table_args__ = (UniqueConstraint('auth_type_id', 'name'), UniqueConstraint('priority'), TABLE_KWARGS)

    id            = Column(Integer, primary_key = True)
    auth_type_id  = Column(Integer, ForeignKey("AuthType.id"), nullable = False)
    name          = Column(Unicode(200), nullable = False)
    priority      = Column(Integer, nullable = False)
    configuration = Column(Text)

    auth_type = relationship("DbAuthType", backref=backref("auths", order_by=id, cascade='all,delete'))

    def __init__(self, auth_type = None, name = None, priority = None, configuration=None):
        super(DbAuth, self).__init__()
        self.auth_type = auth_type
        self.name = name
        self.priority = priority
        self.configuration = configuration

    def __repr__(self):
        return "DbAuth(id = %r, auth_type = %r, name = %r, priority = %r, configuration = %r)" % (
            self.id,
            self.auth_type,
            self.name,
            self.priority,
            self.configuration
        )

    def __unicode__(self):
        return u'%s - %s' % (self.auth_type.name, self.name)

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

    user = relationship("DbUser", backref=backref("auths", order_by=id, cascade='all,delete'))
    auth = relationship("DbAuth", backref=backref("user_auths", order_by=id, cascade='all,delete'))

    def __init__(self, user = None, auth = None, configuration=None):
        super(DbUserAuth, self).__init__()
        self.user = user
        self.auth = auth
        self.configuration = configuration

    def __repr__(self):
        configuration_str = "None"
        if self.configuration is not None:
            configuration_str = ( "*".join("" for _ in self.configuration) )
        user_auth_repr = "DbUserAuth(id = %r, user = %r, auth = %r, configuration = %r)" % (
            self.id,
            self.user,
            self.auth,
            configuration_str
        )
        if isinstance(user_auth_repr, unicode):
            user_auth_repr = user_auth_repr.encode('utf-8')
        return user_auth_repr

    def to_business(self):
        return create_user_auth(self.auth.auth_type.name, self.auth.configuration, self.configuration)


class DbGroup(Base):
    __tablename__  = 'Group'
    __table_args__ = (UniqueConstraint('parent_id', 'name'), TABLE_KWARGS)

    id        = Column(Integer, primary_key = True)
    name      = Column(Unicode(250), nullable = False, index = True)
    parent_id = Column(Integer, ForeignKey("Group.id"), index = True)

    children = relationship("DbGroup", backref=backref("parent", remote_side=id, cascade='all,delete'))
    users    = relationship("DbUser", secondary=t_user_is_member_of)

    def __init__(self, name = None, parent=None):
        super(DbGroup, self).__init__()
        self.name   = name
        self.parent = parent

    def __repr__(self):
        if self.parent is None:
            parent_str = "<None>"
        else:
            parent_str = "<" + self.parent.name + ">"
        return "DbGroup(id = %r, name = %r, parent = %r)" % (
            self.id,
            self.name,
            parent_str
        )
    
    def __unicode__(self):
        return self.name

    def to_business_light(self):
        return Group(self.name, self.id)

    def to_dto(self):
        return self.to_business_light() # Temporal

class DbUserPreferences(Base):
    __tablename__  = 'UserPreferences'
    __table_args__ = (TABLE_KWARGS)

    id            = Column(Integer, primary_key = True)
    user_id       = Column(Integer, ForeignKey('User.id'), nullable = False, index = True, unique = True)
    # Set of user preferences. Only one register per user
    labs_sort_method = Column(Unicode(32), nullable = False, default = 'alphabetical', server_default = 'alphabetical')
    # "alphabetical"; "date"; "uses"; "categories"

    user = relationship("DbUser", backref=backref("preferences", order_by=id, cascade='all,delete'))

    KEYS = ['labs_sort_method']

    def __init__(self, user = None):
        super(DbUserPreferences, self).__init__()
        self.user = user
        self.labs_sort_method = 'alphabetical'

    def __repr__(self):
        return "DbUserPreferences(%r, %r)" % (self.user, self.labs_sort_method)

##############################################################################
# SCHEDULERS DEFINITION
#


class DbScheduler(Base):
    """ A DbScheduler represents a Queue, an external WebLab-Deusto, iLab batch, or whatever. 
    """
    __tablename__ = 'Scheduler'
    __table_args__ = (UniqueConstraint('name'), TABLE_KWARGS)

    id             = Column(Integer, primary_key = True)
    name           = Column(Unicode(255), nullable = False, index = True)
    summary        = Column(Unicode(255), nullable = False, index = True)
    scheduler_type = Column(Unicode(255), nullable = False, index = True)
    config         = Column(Unicode(4096), nullable = False)
    is_external    = Column(Boolean, nullable = False, index = True)

    def __init__(self, name = None, summary = None, scheduler_type = None, config = None, is_external = None):
        super(DbScheduler, self).__init__()
        self.name           = name
        self.summary        = summary
        self.scheduler_type = scheduler_type
        self.config         = config
        self.is_external    = is_external

    def __unicode__(self):
        return self.summary

class DbSchedulerResource(Base):
    """ A DbScheduler will have one or multiple resources, as long as 
    it is not external. If it is external, then it must have zero (since
    they're managed by the external system). """

    __tablename__  = 'SchedulerResource'
    __table_args__ = (UniqueConstraint('name', 'scheduler_id'), TABLE_KWARGS)

    id             = Column(Integer, primary_key = True)
    name           = Column(Unicode(255), nullable = False, index = True)
    scheduler_id   = Column(Integer, ForeignKey("Scheduler.id"), nullable = False, index = True)
    slots          = Column(Integer, nullable = False)

    scheduler = relationship("DbScheduler", backref=backref("resources", order_by=id, cascade='all,delete'))

    def __init__(self, name = None, scheduler = None, slots = None):
        super(DbSchedulerResource, self).__init__()
        self.name = name
        self.scheduler = scheduler
        self.slots = slots
   
class DbExperimentInstance(Base):
    """ A Experiment Instance is managed by the Laboratory Server. So basically
    it is an identification used between the Laboratory Server and the Core server to
    identify a particular experiment server. Each ExperimentInstance must be linked to
    a DbschedulerResource. This table can't be created through the admin panel directly, 
    but by registering it.
    """

    __tablename__  = 'ExperimentInstance'
    __table_args__ = (UniqueConstraint('name', 'scheduler_resource_id'), TABLE_KWARGS)

    id                      = Column(Integer, primary_key = True)
    name                    = Column(Unicode(255), nullable = False, index = True)
    min_slot                = Column(Integer, nullable = False, index = True)
    max_slot                = Column(Integer, nullable = False, index = True)
    scheduler_resource_id   = Column(Integer, ForeignKey("SchedulerResource.id"), nullable = False, index = True)
    experiment_id           = Column(Integer, ForeignKey("Experiment.id"), nullable = False, index = True)

    scheduler_resource = relationship("DbSchedulerResource", backref=backref("experiment_instances", order_by=id, cascade='all,delete'))
    experiment = relationship("DbExperiment", backref=backref("experiment_instances", order_by=id, cascade='all,delete'))
    
    def __init__(self, name, slots, scheduler_resource):
        super(DbExperimentInstance, self).__init__()
        self.name = name
        self.slots = slots
        self.scheduler_resource = scheduler_resource
    
##############################################################################
# EXPERIMENTS DEFINITION
#

class DbExperimentCategory(Base):
    __tablename__  = 'ExperimentCategory'
    __table_args__ = (UniqueConstraint('name'), TABLE_KWARGS)

    id   = Column(Integer, primary_key = True)
    name = Column(Unicode(255), nullable = False, index = True)

    def __init__(self, name = None):
        super(DbExperimentCategory, self).__init__()
        self.name = name

    def __repr__(self):
        return "DbExperimentCategory(id = %r, name = %r)" % (
            self.id,
            self.name
        )

    def __unicode__(self):
        return self.name

    def to_business(self):
        return ExperimentCategory(self.name)


class DbExperiment(Base):
    __tablename__  = 'Experiment'
    __table_args__ = (UniqueConstraint('name', 'category_id'), TABLE_KWARGS)

    id          = Column(Integer, primary_key = True)
    name        = Column(Unicode(255), nullable = False, index = True)
    category_id = Column(Integer, ForeignKey("ExperimentCategory.id"), nullable = False, index = True)
    start_date  = Column(DateTime, nullable = False)
    end_date    = Column(DateTime, nullable = False)
    client      = Column(Unicode(255), index = True)

    category            = relationship("DbExperimentCategory", backref=backref("experiments", order_by=id, cascade='all,delete'))

    def __init__(self, name = None, category = None, start_date = None, end_date = None, client = None):
        super(DbExperiment, self).__init__()
        self.name = name
        self.category = category
        self.start_date = start_date
        self.end_date = end_date
        self.client = client

    def __repr__(self):
        return "DbExperiment(id = %r, name = %r, category = %r, start_date = %r, end_date = %r)" % (
            self.id,
            self.name,
            self.category,
            self.start_date,
            self.end_date
        )

    def __unicode__(self):
        return u'%s@%s' % (self.name, self.category.name if self.category is not None else '')

    def to_business(self):
        configuration = {}
        for param in self.client_parameters:
            try:
                if param.value is not None and len(param.value):
                    if param.parameter_type == 'string':
                        configuration[param.parameter_name] = param.value
                    elif param.parameter_type == 'integer':
                        configuration[param.parameter_name] = int(param.value)
                    elif param.parameter_type == 'floating':
                        configuration[param.parameter_name] = float(param.value)
                    elif param.parameter_type == 'bool':
                        configuration[param.parameter_name] = param.value.lower() == 'true'
                    else:
                        print("Unknown Experiment Client Parameter type %s" % param.parameter_type)
            except (ValueError, TypeError) as e:
                assert e is not None # avoid pyflakes
                traceback.print_exc()
                continue
                
        client = ExperimentClient(self.client, configuration)
        return Experiment(
            self.name,
            self.category.to_business(),
            self.start_date,
            self.end_date,
            client,
            self.id
            )

    def to_dto(self):
        return self.to_business() # Temporal

class DbExperimentClientParameter(Base):
    __tablename__  = 'ExperimentClientParameter'
    __table_args__ = (TABLE_KWARGS)
    
    id               = Column(Integer, primary_key = True)
    experiment_id    = Column(Integer, ForeignKey("Experiment.id"), nullable = False, index = True)
    parameter_name   = Column(Unicode(255), nullable = False, index = True)
    parameter_type   = Column(Unicode(15), nullable = False, index = True)
    value            = Column(Unicode(600), nullable = False)

    experiment       = relationship("DbExperiment", backref=backref("client_parameters", order_by=id))

    def __init__(self, experiment = None, parameter_name = None, parameter_type = None, value = None):
        self.experiment     = experiment
        self.parameter_name = parameter_name
        self.parameter_type = parameter_type
        self.value          = value

class DbSchedulerExternalExperimentEntry(Base):
    __tablename__ = 'SchedulerExternalExperimentEntry'
    __table_args__ = (UniqueConstraint('experiment_id', 'scheduler_id'), TABLE_KWARGS)

    id             = Column(Integer, primary_key = True)
    experiment_id  = Column(Integer, ForeignKey("Experiment.id"), nullable = False, index = True)
    scheduler_id   = Column(Integer, ForeignKey("Scheduler.id"), nullable = False, index = True)
    config         = Column(Unicode(1024))
    
    experiment = relationship("DbExperiment", backref=backref("external_schedulers", order_by=id))
    scheduler  = relationship("DbScheduler", backref=backref("external_experiments", order_by=id))

    def __init__(self, experiment = None, scheduler = None, config = None):
        self.experiment = experiment
        self.scheduler = scheduler
        self.config = config

    def __repr__(self):
        return "DbSchedulerExternalExperimentEntry(%r, %r, %r)" % (self.experiment, self.scheduler, self.config)

    def __unicode__(self):
        return u"Entry for experiment %s on scheduler %s with config = %r" % (self.experiment, self.scheduler, self.config)


##############################################################################
# EXPERIMENT INSTANCE MEMBERSHIP DEFINITION
#

class DbUserUsedExperiment(Base):
    __tablename__  = 'UserUsedExperiment'
    __table_args__ = ( Index('idx_UserUsedExperiment_timetable', 'start_date_weekday', 'start_date_hour'),
                       Index('idx_UserUsedExperiment_user_experiment', 'user_id', 'experiment_id'),
                       Index('idx_UserUsedExperiment_user_origin', 'user_id', 'origin'),

                       Index('idx_UserUsedExperiment_user_group_permission_id', 'user_id', 'group_permission_id'),
                       Index('idx_UserUsedExperiment_user_user_permission_id', 'user_id', 'user_permission_id'),
                       Index('idx_UserUsedExperiment_user_role_permission_id', 'user_id', 'role_permission_id'),

                       Index('idx_UserUsedExperiment_experiment_id_group_id', 'experiment_id', 'group_permission_id'),
                       Index('idx_UserUsedExperiment_experiment_id_user_id', 'experiment_id', 'user_permission_id'),
                       Index('idx_UserUsedExperiment_experiment_id_role_id', 'experiment_id', 'role_permission_id'),
                       TABLE_KWARGS)

    id                      = Column(Integer, primary_key = True)

    # Basic data

    user_id                 = Column(Integer, ForeignKey("User.id"), nullable = False, index = True)
    experiment_id           = Column(Integer, ForeignKey("Experiment.id"), nullable = False, index = True)
    start_date              = Column(DateTime, nullable = False, index = True)
    start_date_micro        = Column(Integer, nullable = False)
    end_date                = Column(DateTime, index = True)
    end_date_micro          = Column(Integer)

    # TODO: use these new two fields
    max_error_in_millis     = Column(Integer, nullable = True)
    finish_reason           = Column(Integer, nullable = True) # NULL = unknown; 0 = actively finished; 1 = timed out (client); 2 = kicked by scheduler; 3 = batch.

    # 
    # The following data is used for optimized analytics (optimized queries based on this data).
    # 
    start_date_date         = Column(Date, index = True)
    start_date_weekday      = Column(Integer, index = True) # 0..6, as in datetime.datetime.weekday()
    start_date_hour         = Column(Integer, index = True) # 0..23
    start_date_year         = Column(Integer, index = True) # e.g., 2015
    start_date_month        = Column(Integer, index = True) # 1..12, as in datetime.date.month
    start_date_week_monday  = Column(Integer, index = True) # number of weeks since January 5, 1970 (first Monday after epoc)
    start_date_week_sunday  = Column(Integer, index = True) # number of weeks since January 4, 1970 (first Monday after epoc)

    session_time_micro      = Column(BigInteger, index = True) # This should take into account finish_reason
    session_time_seconds    = Column(Integer, index = True) # This should take into account finish_reason

    # 
    # Who accessed the experiment?
    # 

    permission_permanent_id = Column(Unicode(255), nullable = True, index = True)
    group_permission_id     = Column(Integer, ForeignKey('GroupPermission.id'), nullable = True)
    user_permission_id      = Column(Integer, ForeignKey('UserPermission.id'), nullable = True)
    role_permission_id      = Column(Integer, ForeignKey('RolePermission.id'), nullable = True)
    origin                  = Column(Unicode(255), nullable = False, index = True)
    coord_address           = Column(Unicode(255), nullable = False, index = True)
    reservation_id          = Column(Unicode(50), index = True)

    user                    = relationship("DbUser", backref=backref("experiment_uses", order_by=id))
    experiment              = relationship("DbExperiment", backref=backref("user_uses", order_by=id))

    group_permission        = relationship("DbGroupPermission", backref=backref("uses", order_by=id))
    user_permission         = relationship("DbUserPermission",  backref=backref("uses", order_by=id))
    role_permission         = relationship("DbRolePermission",  backref=backref("uses", order_by=id))

    hostname                  = Column(Unicode(255), index = True)
    city                      = Column(Unicode(255), index = True)
    country                   = Column(Unicode(255), index = True)
    most_specific_subdivision = Column(Unicode(255), index = True)

    def __init__(self, user = None, experiment = None, start_date = None, origin = None, coord_address = None, reservation_id = None, end_date = None, max_error_in_millis = None, finish_reason = None, permission_permanent_id = None, group_permission = None, user_permission = None, role_permission = None, session_time_micro = None, hostname = None, city = None, country = None, most_specific_subdivision = None):
        super(DbUserUsedExperiment, self).__init__()
        self.user = user
        self.experiment = experiment
        self.start_date, self.start_date_micro = _timestamp_to_splitted_utc_datetime(start_date)
        self.start_date_date = self.start_date.date()
        self.start_date_hour = self.start_date.hour
        self.start_date_weekday = self.start_date.weekday()
        self.start_date_year = self.start_date.year
        self.start_date_month = self.start_date.month
        self.start_date_week_sunday = (self.start_date_date - datetime.date(1970, 1, 4)).days / 7
        self.start_date_week_monday = (self.start_date_date - datetime.date(1970, 1, 5)).days / 7
        self.set_end_date(end_date)
        self.origin = origin
        self.coord_address = coord_address
        self.reservation_id = reservation_id
        self.max_error_in_millis = max_error_in_millis
        self.finish_reason       = finish_reason
        self.permission_permanent_id = permission_permanent_id
        self.group_permission = group_permission
        self.user_permission = user_permission
        self.role_permission = role_permission
        self.hostname = hostname
        self.city = city
        self.country = country
        self.most_specific_subdivision = most_specific_subdivision

        if end_date is not None:
            self.session_time_micro = (self.end_date - self.start_date).seconds * 1e6 + (self.end_date - self.start_date).microseconds
            self.session_time_seconds = self.session_time_micro / 1000000
        else:
            self.session_time_micro = session_time_micro
            if self.session_time_micro:
                self.session_time_seconds = self.session_time_micro / 1000000

    def set_end_date(self, end_date):
        self.end_date, self.end_date_micro = _timestamp_to_splitted_utc_datetime(end_date)
        if end_date:
            self.session_time_micro = (self.end_date - self.start_date).seconds * 1e6 + (self.end_date - self.start_date).microseconds
            self.session_time_seconds = self.session_time_micro / 1000000

    def __repr__(self):
        return "DbUserUsedExperiment(id = %r, user = %r, experiment = %r, start_date = %r, start_date_micro = %r, end_date = %r, end_date_micro = %r, origin = %r, coord_address = %r, reservation_id = %r)" % (
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
        usage.coord_address     = CoordAddress.translate(self.coord_address)
        
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
    name = Column(Unicode(255), nullable = False, index = True)

    def __init__(self, name = None, id = None):
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
    value             = Column(Unicode(255))

    property_name  = relationship("DbUserUsedExperimentProperty", backref=backref("values",     order_by=id, cascade='all,delete'))
    experiment_use = relationship("DbUserUsedExperiment",         backref=backref("properties", order_by=id, cascade='all,delete'))

    def __init__(self, value = None, property_name = None, experiment_use = None, id = None):
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
    __table_args__ = (Index('idx_UserFile_experiment_use_id_file_hash', 'experiment_use_id', 'file_hash'), TABLE_KWARGS)

    id                     = Column(Integer, primary_key = True)
    experiment_use_id      = Column(Integer, ForeignKey("UserUsedExperiment.id"), nullable = False)
    file_sent              = Column(Unicode(255), nullable = False)
    file_hash              = Column(Unicode(255), nullable = False, index = True)
    file_info              = Column(Text)
    response               = Column(Text)
    timestamp_before       = Column(DateTime, nullable = False)
    timestamp_before_micro = Column(Integer, nullable = False)
    timestamp_after        = Column(DateTime)
    timestamp_after_micro  = Column(Integer)

    experiment_use = relationship("DbUserUsedExperiment", backref=backref("files", order_by=id, cascade='all,delete'))

    def __init__(self, experiment_use = None, file_sent = None, file_hash = None, timestamp_before = None, file_info=None, response=None, timestamp_after=None):
        super(DbUserFile, self).__init__()
        self.experiment_use = experiment_use
        self.file_sent = file_sent
        self.file_hash = file_hash
        self.file_info = file_info
        self.response = response
        self.timestamp_before, self.timestamp_before_micro = _timestamp_to_splitted_utc_datetime(timestamp_before)
        self.set_timestamp_after(timestamp_after)

    def set_timestamp_after(self, timestamp_after):
        self.timestamp_after, self.timestamp_after_micro = _timestamp_to_splitted_utc_datetime(timestamp_after)

    def __repr__(self):
        return "DbUserFile(id = %r, experiment_use = %r, file_sent = %r, file_hash = %r, file_info = %r, response = %r, timestamp_before = %r, timestamp_before_micro = %r, timestamp_after = %r, timestamp_after_micro = %r)" % (
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

    experiment_use = relationship("DbUserUsedExperiment", backref=backref("commands", order_by=id, cascade='all,delete'))

    def __init__(self, experiment_use = None, command = None, timestamp_before = None, response=None, timestamp_after=None):
        super(DbUserCommand, self).__init__()
        self.experiment_use = experiment_use
        self.command = command
        self.response = response
        self.timestamp_before, self.timestamp_before_micro = _timestamp_to_splitted_utc_datetime(timestamp_before)
        self.set_timestamp_after(timestamp_after)

    def set_timestamp_after(self, timestamp_after):
        self.timestamp_after, self.timestamp_after_micro = _timestamp_to_splitted_utc_datetime(timestamp_after)

    def __repr__(self):
        return "DbUserCommand(id = %r, experiment_use = %r, command = %r, response = %r, timestamp_before = %r, timestamp_before_micro = %r, timestamp_after = %r, timestamp_after_micro = %r)" % (
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


##############################################################################
# USER PERMISSIONS
#

class DbUserPermission(Base):
    __tablename__  = 'UserPermission'
    __table_args__ = (UniqueConstraint('permanent_id'), TABLE_KWARGS)

    id                 = Column(Integer, primary_key = True)
    user_id            = Column(Integer, ForeignKey("User.id"), nullable = False)
    permission_type    = Column(Unicode(255), nullable = False, index = True)
    permanent_id       = Column(Unicode(255), nullable = False, index = True)
    date               = Column(DateTime, nullable = False)
    comments           = Column(Text)

    user               = relationship("DbUser", backref=backref("permissions", order_by=id, cascade='all,delete'))

    def __init__(self, user = None, permission_type = None, permanent_id = None, date = None, comments=None):
        super(DbUserPermission, self).__init__()
        self.user = user
        self.permission_type = permission_type
        self.permanent_id = permanent_id
        self.date = date
        self.comments = comments

    def __repr__(self):
        return "DbUserPermission(id = %r, user = %r, permission_type = %r, permanent_id = %r, date = %r, comments = %r)" % (
            self.id,
            self.user,
            self.permission_type,
            self.permanent_id,
            self.date,
            self.comments
        )

    def get_permission_type(self):
        return self.permission_type

    def get_parameter(self, parameter_name):
        return [ param for param in self.parameters if param.permission_type_parameter == parameter_name ][0]

    def to_dto(self):
        permission = Permission( self.permission_type )
        for param in self.parameters:
            permission.add_parameter(param.to_dto())
        return permission


class DbUserPermissionParameter(Base):
    __tablename__  = 'UserPermissionParameter'
    __table_args__ = (UniqueConstraint('permission_id', 'permission_type_parameter'), TABLE_KWARGS)

    id                           = Column(Integer, primary_key = True)
    permission_id                = Column(Integer, ForeignKey("UserPermission.id"), nullable = False)
    permission_type_parameter    = Column(Unicode(255), nullable = False, index = True)
    value                        = Column(Text)

    permission                = relationship("DbUserPermission", backref=backref("parameters", order_by=id, cascade='all,delete'))

    def __init__(self, permission = None, permission_type_parameter = None, value=None):
        super(DbUserPermissionParameter, self).__init__()
        self.permission = permission
        self.permission_type_parameter = permission_type_parameter
        self.value = value

    def __repr__(self):
        return "DbUserPermissionParameter(id = %r, permission = %r, permission_type_parameter = %r, value = %r)" % (
            self.id,
            self.permission,
            self.permission_type_parameter,
            self.value
        )

    def get_name(self):
        return self.permission_type_parameter

    def get_datatype(self):
        permission_type = self.permission.permission_type
        parameter = permissions.permission_types[permission_type].get_parameter(self.permission_type_parameter)
        return parameter.datatype

    def to_dto(self):
        return PermissionParameter( self.get_name(), self.get_datatype(), self.value )

class DbRolePermission(Base):
    __tablename__  = 'RolePermission'
    __table_args__ = (UniqueConstraint('permanent_id'), TABLE_KWARGS)

    id                            = Column(Integer, primary_key = True)
    role_id                       = Column(Integer, ForeignKey("Role.id"), nullable = False)
    permission_type               = Column(Unicode(255), nullable = False, index = True)
    permanent_id                  = Column(Unicode(255), nullable = False, index = True)
    date                          = Column(DateTime, nullable = False)
    comments                      = Column(Text)

    role            = relationship("DbRole", backref=backref("permissions", order_by=id, cascade='all,delete'))

    def __init__(self, role = None, permission_type = None, permanent_id = None, date = None, comments=None):
        super(DbRolePermission, self).__init__()
        self.role = role
        self.permission_type = permission_type
        self.permanent_id = permanent_id
        self.date = date
        self.comments = comments

    def __repr__(self):
        return "DbRolePermission(id = %r, role = %r, permission_type = %r, permanent_id = %r, date = %r, comments = %r)" % (
            self.id,
            self.role,
            self.permission_type,
            self.permanent_id,
            self.date,
            self.comments
        )

    def get_permission_type(self):
        return self.permission_type

    def get_parameter(self, parameter_name):
        return [ param for param in self.parameters if param.permission_type_parameter == parameter_name ][0]

    def to_dto(self):
        permission = Permission( self.permission_type )

        for param in self.parameters:
            permission.add_parameter(param.to_dto())
        return permission


class DbRolePermissionParameter(Base):
    __tablename__  = 'RolePermissionParameter'
    __table_args__ = (UniqueConstraint('permission_id', 'permission_type_parameter'), TABLE_KWARGS)

    id                           = Column(Integer, primary_key = True)
    permission_id                = Column(Integer, ForeignKey("RolePermission.id"), nullable = False)
    permission_type_parameter    = Column(Unicode(255), nullable = False, index = True)
    value                        = Column(Text)

    permission                = relationship("DbRolePermission", backref=backref("parameters", order_by=id, cascade='all,delete'))

    def __init__(self, permission = None, permission_type_parameter = None, value=None):
        super(DbRolePermissionParameter, self).__init__()
        self.permission = permission
        self.permission_type_parameter = permission_type_parameter
        self.value = value

    def __repr__(self):
        return "DbRolePermissionParameter(id = %r, permission = %r, permission_type_parameter = %r, value = %r)" % (
            self.id,
            self.permission,
            self.permission_type_parameter,
            self.value
        )

    def get_name(self):
        return self.permission_type_parameter

    def get_datatype(self):
        permission_type = self.permission.permission_type
        parameter = permissions.permission_types[permission_type].get_parameter(self.permission_type_parameter)
        return parameter.datatype

    def to_dto(self):
        return PermissionParameter( self.get_name(), self.get_datatype(), self.value )


class DbGroupPermission(Base):
    __tablename__  = 'GroupPermission'
    __table_args__ = (UniqueConstraint('permanent_id'), TABLE_KWARGS)

    id                 = Column(Integer, primary_key = True)
    group_id           = Column(Integer, ForeignKey("Group.id"), nullable = False)
    permission_type    = Column(Unicode(255), nullable = False, index = True)
    permanent_id       = Column(Unicode(255), nullable = False, index = True)
    date               = Column(DateTime, nullable = False)
    comments           = Column(Text)

    group           = relationship("DbGroup", backref=backref("permissions", order_by=id, cascade='all,delete'))

    def __init__(self, group = None, permission_type = None, permanent_id = None, date = None, comments=None):
        super(DbGroupPermission, self).__init__()
        self.group = group
        self.permission_type = permission_type
        self.permanent_id = permanent_id
        self.date = date
        self.comments = comments

    def __repr__(self):
        return "DbGroupPermission(id = %r, group = %r, permission_type = %r, permanent_id = %r, date = %r, comments = %r)" % (
            self.id,
            self.group,
            self.permission_type,
            self.permanent_id,
            self.date,
            self.comments
        )

    def get_permission_type(self):
        return self.permission_type

    def get_parameter(self, parameter_name):
        return [ param for param in self.parameters if param.permission_type_parameter == parameter_name ][0]

    def to_dto(self):
        permission = Permission( self.permission_type )
        for param in self.parameters:
            permission.add_parameter(param.to_dto())
        return permission


class DbGroupPermissionParameter(Base):
    __tablename__  = 'GroupPermissionParameter'
    __table_args__ = (UniqueConstraint('permission_id', 'permission_type_parameter'), TABLE_KWARGS)

    id                           = Column(Integer, primary_key = True)
    permission_id                = Column(Integer, ForeignKey("GroupPermission.id"), nullable = False)
    permission_type_parameter    = Column(Unicode(255), nullable = False, index = True)
    value                        = Column(Text)

    permission                = relationship("DbGroupPermission", backref=backref("parameters", order_by=id, cascade='all,delete'))

    def __init__(self, permission = None, permission_type_parameter = None, value=None):
        super(DbGroupPermissionParameter, self).__init__()
        self.permission = permission
        self.permission_type_parameter = permission_type_parameter
        self.value = value

    def __repr__(self):
        return "DbGroupPermissionParameter(id = %r, permission = %r, permission_type_parameter = %r, value = %r)" % (
            self.id,
            self.permission,
            self.permission_type_parameter,
            self.value
        )

    def get_name(self):
        return self.permission_type_parameter

    def get_datatype(self):
        permission_type = self.permission.permission_type
        parameter = permissions.permission_types[permission_type].get_parameter(self.permission_type_parameter)
        return parameter.datatype

    def to_dto(self):
        return PermissionParameter( self.get_name(), self.get_datatype(), self.value )

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

