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

import os
import numbers
import datetime
import threading
import traceback
from functools import wraps
from collections import OrderedDict, namedtuple, defaultdict

import six
import sqlalchemy
import sqlalchemy.sql as sql
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.exc import NoResultFound

from dateutil.relativedelta import relativedelta

import voodoo.log as log
from voodoo.log import logged
from voodoo.typechecker import typecheck

from weblab.db import db
import weblab.db.model as model

import weblab.configuration_doc as configuration_doc
from weblab.data import ValidDatabaseSessionId
from weblab.data.command import Command
import weblab.data.dto.experiments as ExperimentAllowed
from weblab.data.experiments import ExperimentUsage, CommandSent, FileSent

import weblab.core.exc as DbErrors
import weblab.permissions as permissions

DEFAULT_VALUE = object()

_current = threading.local()
class UsesQueryParams( namedtuple('UsesQueryParams', ['login', 'experiment_name', 'category_name', 'group_names', 'start_date', 'end_date', 'min_date', 'max_date', 'count', 'country', 'date_precision', 'ip', 'page'])):
    PRIVATE_FIELDS = ('group_names')
    NON_FILTER_FIELDS = ('count', 'min_date', 'max_date', 'date_precision', 'page')

    @staticmethod
    def create(page=None, **kwargs):
        if page is None:
            page = 1
        return UsesQueryParams(page=page, **kwargs)

    def pubdict(self):
        result = {}
        for field in UsesQueryParams._fields:
            if field not in self.PRIVATE_FIELDS and getattr(self, field) is not None:
                result[field] = getattr(self, field)
        return result

    def filterdict(self):
        result = {}
        for field in UsesQueryParams._fields:
            if field not in self.PRIVATE_FIELDS and field not in self.NON_FILTER_FIELDS and getattr(self, field) is not None:
                result[field] = getattr(self, field)
        return result

# Support None as default params
UsesQueryParams.__new__.__defaults__ = (None,) * len(UsesQueryParams._fields)

def with_session(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        _current.session = self.Session()
        try:
            return func(self, *args, **kwargs)
        except sqlalchemy.exc.SQLAlchemyError:
            _current.session.rollback()
            raise
        finally:
            _current.session.close()

    return wrapper

class DatabaseGateway(object):

    forbidden_access = 'forbidden_access'

    def __init__(self, cfg_manager):
        super(DatabaseGateway, self).__init__()
        self.cfg_manager = cfg_manager
        self.Session, self.engine = db.initialize(cfg_manager)

    @typecheck(basestring)
    @logged()
    def get_user_by_name(self, user_login):
        session = self.Session()
        try:
            return self._get_user(session, user_login).to_dto()
        finally:
            session.close()

    @with_session
    def get_user(self, login):
        return _current.session.query(model.DbUser).filter_by(login=login).first()

    @with_session
    def get_user_preferences(self, login):
        user = _current.session.query(model.DbUser).filter_by(login=login).first()
        if user is None:
            return model.DbUserPreferences()

        all_preferences = user.preferences
        if len(all_preferences) == 0:
            return model.DbUserPreferences()

        return all_preferences[0]

    @with_session
    def update_preferences(self, login, preferences):
        user = _current.session.query(model.DbUser).filter_by(login=login).first()
        if user is None:
            return
        
        if len(user.preferences) == 0:
            user_preferences = model.DbUserPreferences(user)
            user.preferences.append(user_preferences)
            _current.session.add(user_preferences)
        else:
            user_preferences = user.preferences[0]
        
        for key, value in preferences.items():
            if key in model.DbUserPreferences.KEYS and hasattr(user_preferences, key):
                setattr(user_preferences, key, value)

        _current.session.commit()

    @logged()
    def list_clients(self):
        """Lists the ExperimentClients """
        session = self.Session()
        try:
            clients = {}
            for experiment in session.query(model.DbExperiment).options(joinedload('category'), joinedload('client_parameters')).all():
                exp = experiment.to_business()
                clients[exp.name, exp.category.name] = exp.client
            return clients
        finally:
            session.close()

    @logged()
    def get_client_id(self, experiment_name, category_name):
        """Lists the ExperimentClients """
        session = self.Session()
        try:
            category = session.query(model.DbExperimentCategory).filter_by(name = category_name).first()
            if category is None:
                return None
            experiment = session.query(model.DbExperiment).filter_by(name = experiment_name, category = category).first()
            if experiment is None:
                return None
            return experiment.client
        finally:
            session.close()

    def _get_permission_scope(self, permission):
        if isinstance(permission, model.DbUserPermission):
            return  'user'
        elif isinstance(permission, model.DbGroupPermission):
            return 'group'
        elif isinstance(permission, model.DbRolePermission):
            return 'role'
        return 'unknown'

    @with_session
    def check_experiment_exists(self, exp_name = None, cat_name = None):
        category = _current.session.query(model.DbExperimentCategory).filter_by(name = cat_name).first()
        if category is None:
            return False
        experiment = _current.session.query(model.DbExperiment).filter_by(name = exp_name, category = category).first()
        return experiment is not None

    # @typecheck(basestring, (basestring, None), (basestring, None))
    @logged()
    def list_experiments(self, user_login, exp_name = None, cat_name = None):
        session = self.Session()
        try:
            user = self._get_user(session, user_login)
            access_all_labs_permissions = self._gather_permissions(session, user, 'access_all_labs')
            user_permissions = self._gather_permissions(session, user, 'experiment_allowed')

            grouped_experiments = defaultdict(list) # {
            #    experiment_unique_id : [ experiment_allowed ]
            # }
            if len(access_all_labs_permissions) > 0:
                permission = access_all_labs_permissions[0]
                permission_scope = self._get_permission_scope(permission)
                default_priority = 100 # Super-low priority
                default_time_allowed = 180 # 3 minutes
                default_initialization = True

                query_obj = session.query(model.DbExperiment)
                if exp_name is not None:
                    query_obj = query_obj.filter_by(name=exp_name)
                if cat_name is not None:
                    category = session.query(model.DbExperimentCategory).filter_by(name=cat_name).first()
                    query_obj = query_obj.filter_by(category=category)

                for experiment in query_obj.all():
                    experiment_allowed = ExperimentAllowed.ExperimentAllowed(experiment.to_business(), default_time_allowed, default_priority, default_initialization, permission.permanent_id, permission.id, permission_scope)
                    experiment_unique_id = unicode(experiment)
                    grouped_experiments[experiment_unique_id].append(experiment_allowed)

            for permission in user_permissions:
                p_permanent_id                 = self._get_parameter_from_permission(session, permission, 'experiment_permanent_id')
                p_category_id                  = self._get_parameter_from_permission(session, permission, 'experiment_category_id')
                p_time_allowed                 = self._get_float_parameter_from_permission(session, permission, 'time_allowed')
                p_priority                     = self._get_int_parameter_from_permission(session, permission, 'priority', ExperimentAllowed.DEFAULT_PRIORITY)
                p_initialization_in_accounting = self._get_bool_parameter_from_permission(session, permission, 'initialization_in_accounting', ExperimentAllowed.DEFAULT_INITIALIZATION_IN_ACCOUNTING)
                
                # If a filter is passed, ignore those permissions on other experiments
                if cat_name is not None and exp_name is not None:
                    if p_category_id != cat_name or p_permanent_id != exp_name:
                        continue
                experiments = [ exp for exp in session.query(model.DbExperiment).filter_by(name=p_permanent_id).all() if exp.category.name == p_category_id ]
                if len(experiments) == 0:
                    continue

                experiment = experiments[0]

                permission_scope = self._get_permission_scope(permission)
                experiment_allowed = ExperimentAllowed.ExperimentAllowed(experiment.to_business(), p_time_allowed, p_priority, p_initialization_in_accounting, permission.permanent_id, permission.id, permission_scope)

                experiment_unique_id = p_permanent_id+"@"+p_category_id
                grouped_experiments[experiment_unique_id].append(experiment_allowed)

            # If any experiment is duplicated, only the less restrictive one is given
            experiments = []
            for experiment_unique_id in grouped_experiments:
                less_restrictive_experiment_allowed = grouped_experiments[experiment_unique_id][0]
                for experiment_allowed in grouped_experiments[experiment_unique_id]:
                    if experiment_allowed.time_allowed > less_restrictive_experiment_allowed.time_allowed:
                        less_restrictive_experiment_allowed = experiment_allowed
                experiments.append(less_restrictive_experiment_allowed)

            experiments.sort(lambda x,y: cmp(x.experiment.category.name, y.experiment.category.name))

            if experiments:
                experiment_allowed_by_id = { experiment_allowed.experiment.id : experiment_allowed for experiment_allowed in experiments }
                experiment_ids = [ experiment_allowed.experiment.id for experiment_allowed in experiments ]

                for experiment_id, uses_for_user in session.query(model.DbUserUsedExperiment.experiment_id, func.count(model.DbUserUsedExperiment.id)).filter(model.DbUserUsedExperiment.experiment_id.in_(experiment_ids), model.DbUserUsedExperiment.user_id == user.id).group_by(model.DbUserUsedExperiment.experiment_id).all():
                    experiment_allowed_by_id[experiment_id].total_uses = uses_for_user

                for experiment_id, max_date in session.query(model.DbUserUsedExperiment.experiment_id, func.max(model.DbUserUsedExperiment.start_date)).filter(model.DbUserUsedExperiment.experiment_id.in_(experiment_ids), model.DbUserUsedExperiment.user_id == user.id).group_by(model.DbUserUsedExperiment.experiment_id).all():
                    experiment_allowed_by_id[experiment_id].latest_use = max_date

            return tuple(experiments)
        finally:
            session.close()

    @typecheck(basestring)
    @logged()
    def is_access_forward(self, user_login):
        session = self.Session()
        try:
            user = self._get_user(session, user_login)
            user_permissions = self._gather_permissions(session, user, 'access_forward')
            return len(user_permissions) > 0
        finally:
            session.close()

    @typecheck(basestring)
    @logged()
    def is_instructor(self, user_login):
        session = self.Session()
        try:
            user = self._get_user(session, user_login)
            admin_permissions = self._gather_permissions(session, user, 'admin_panel_access')
            instructor_permissions = self._gather_permissions(session, user, 'instructor_of_group')
            return user.role.name == 'instructor' or len(admin_permissions) > 0 or len(instructor_permissions) > 0
        finally:
            session.close()

    @typecheck(basestring, ExperimentUsage)
    @logged()
    def store_experiment_usage(self, user_login, experiment_usage):
        session = self.Session()
        try:
            use = model.DbUserUsedExperiment(
                        self._get_user(session, user_login),
                        self._get_experiment(session, experiment_usage.experiment_id.exp_name, experiment_usage.experiment_id.cat_name),
                        experiment_usage.start_date,
                        experiment_usage.from_ip,
                        experiment_usage.coord_address.address,
                        experiment_usage.reservation_id,
                        experiment_usage.end_date,
                )
            session.add(use)
            # TODO: The c.response of an standard command is an object with
            # a commandstring, whereas the response to an async command is
            # a simple string to identify the request. The way in which the logger
            # currently handles these cases is somewhat shady.
            for c in experiment_usage.commands:
                # If we have a response, the c.response will be an object and not
                # a string. Generally, we will, unless the command was asynchronous
                # and it didn't finish executing.
                if type(c.response) != type(""):
                    session.add(model.DbUserCommand(
                                    use,
                                    c.command.commandstring,
                                    c.timestamp_before,
                                    c.response.commandstring,
                                    c.timestamp_after
                                ))
                else:
                    # In this other case, the response is a string, which means
                    # that we have not updated it with the real response. Probably,
                    # it was an asynchronous command which did not finish executing
                    # by the time the experiment ended.
                    session.add(model.DbUserCommand(
                                    use,
                                    c.command.commandstring,
                                    c.timestamp_before,
                                    "[RESPONSE NOT AVAILABLE]",
                                    c.timestamp_after
                                ))
            for f in experiment_usage.sent_files:
                if f.is_loaded():
                    saved = f.save(self.cfg_manager, experiment_usage.reservation_id)
                else:
                    saved = f
                session.add(model.DbUserFile(
                                use,
                                saved.file_path,
                                saved.file_hash,
                                saved.timestamp_before,
                                saved.file_info,
                                saved.response.commandstring,
                                saved.timestamp_after
                            ))
            
            permission_scope = experiment_usage.request_info.pop('permission_scope')
            permission_id = experiment_usage.request_info.pop('permission_id')
            if permission_scope == 'group':
                use.group_permission_id = permission_id
            elif permission_scope == 'user':
                use.user_permission_id = permission_id
            elif permission_scope == 'role':
                use.role_permission_id = permission_id

            for reservation_info_key in experiment_usage.request_info:
                db_key = session.query(model.DbUserUsedExperimentProperty).filter_by(name = reservation_info_key).first()
                if db_key is None:
                    db_key = model.DbUserUsedExperimentProperty(reservation_info_key)
                    session.add(db_key)

                value = experiment_usage.request_info[reservation_info_key]
                session.add(model.DbUserUsedExperimentPropertyValue( unicode(value), db_key, use ))

            session.commit()
        finally:
            session.close()

    @typecheck(basestring, float, CommandSent)
    @logged()
    def finish_experiment_usage(self, reservation_id, end_date, last_command ):
        session = self.Session()
        try:
            user_used_experiment = session.query(model.DbUserUsedExperiment).filter_by(reservation_id = reservation_id).first()
            if user_used_experiment is None:
                return False

            user_used_experiment.set_end_date(end_date)
            session.add(user_used_experiment)
            session.add(model.DbUserCommand(
                            user_used_experiment,
                            last_command.command.commandstring,
                            last_command.timestamp_before,
                            last_command.response.commandstring,
                            last_command.timestamp_after
                        ))
            session.commit()
            return True
        finally:
            session.close()

    @logged()
    def store_commands(self, complete_commands, command_requests, command_responses, complete_files, file_requests, file_responses):
        """ Stores all the commands in a single transaction; retrieving the ids of the file and command requests """
        request_mappings = {
            # entry_id : command_id
        }
        session = self.Session()
        try:
            db_commands_and_files = []

            for reservation_id, entry_id, command in complete_commands:
                db_command = self._append_command(session, reservation_id, command)
                if db_command == False:
                    request_mappings[entry_id] = False

            for reservation_id, entry_id, command in complete_files:
                db_file = self._append_file(session, reservation_id, command)
                if db_file == False:
                    request_mappings[entry_id] = False

            for entry_id in command_requests:
                reservation_id, command = command_requests[entry_id]
                db_command = self._append_command(session, reservation_id, command)
                if db_command == False:
                    request_mappings[entry_id] = False
                else:
                    db_commands_and_files.append((entry_id, db_command))

            for entry_id in file_requests:
                reservation_id, file = file_requests[entry_id]
                db_file = self._append_file(session, reservation_id, file)
                if db_file == False:
                    request_mappings[entry_id] = False
                else:
                    db_commands_and_files.append((entry_id, db_file))

            for entry_id, command_id, response, timestamp in command_responses:
                if not self._update_command(session, command_id, response, timestamp):
                    request_mappings[entry_id] = False

            for entry_id, file_id, response, timestamp in file_responses:
                if not self._update_file(session, file_id, response, timestamp):
                    request_mappings[entry_id] = False

            session.commit()
            for entry_id, db_command in db_commands_and_files:
                request_mappings[entry_id] = db_command.id

        finally:
            session.close()
       
        return request_mappings

    @typecheck(basestring, CommandSent)
    @logged()
    def append_command(self, reservation_id, command ):
        session = self.Session()
        try:
            db_command = self._append_command(session, reservation_id, command)
            session.commit()
            return db_command.id
        finally:
            session.close()

    def _append_command(self, session, reservation_id, command):
        user_used_experiment = session.query(model.DbUserUsedExperiment).filter_by(reservation_id = reservation_id).first()
        if user_used_experiment is None:
            return False
        db_command = model.DbUserCommand(
                        user_used_experiment,
                        command.command.commandstring,
                        command.timestamp_before,
                        command.response.commandstring if command.response is not None else None,
                        command.timestamp_after
                    )
        session.add(db_command)
        return db_command

    @typecheck(numbers.Integral, Command, float)
    @logged()
    def update_command(self, command_id, response, end_timestamp ):
        session = self.Session()
        try:
            if self._update_command(session, command_id, response, end_timestamp):
                session.commit()
                return True
            return False
        finally:
            session.close()

    def _update_command(self, session, command_id, response, end_timestamp):
        db_command = session.query(model.DbUserCommand).filter_by(id = command_id).first()
        if db_command is None:
            return False

        db_command.response = response.commandstring if response is not None else None
        db_command.set_timestamp_after(end_timestamp)
        session.add(db_command)
        return True


    @typecheck(basestring, FileSent)
    @logged()
    def append_file(self, reservation_id, file_sent):
        session = self.Session()
        try:
            db_file_sent = self._append_file(session, reservation_id, file_sent)
            session.commit()
            return db_file_sent.id
        finally:
            session.close()

    def _append_file(self, session, reservation_id, file_sent):
        user_used_experiment = session.query(model.DbUserUsedExperiment).filter_by(reservation_id = reservation_id).first()
        if user_used_experiment is None:
            return False
        db_file_sent = model.DbUserFile(
                        user_used_experiment,
                        file_sent.file_path,
                        file_sent.file_hash,
                        file_sent.timestamp_before,
                        file_sent.file_info,
                        file_sent.response.commandstring if file_sent.response is not None else None,
                        file_sent.timestamp_after
                    )
        session.add(db_file_sent)
        return db_file_sent

    @typecheck(numbers.Integral, Command, float)
    @logged()
    def update_file(self, file_id, response, end_timestamp ):
        session = self.Session()
        try:
            if self._update_file(session, file_id, response, end_timestamp):
                session.commit()
                return True
            return False
        finally:
            session.close()

    def _update_file(self, session, file_id, response, end_timestamp):
        db_file_sent = session.query(model.DbUserFile).filter_by(id = file_id).first()
        if db_file_sent is None:
            return False

        db_file_sent.response = response.commandstring if response is not None else None
        db_file_sent.set_timestamp_after(end_timestamp)
        session.add(db_file_sent)
        return True

    @logged()
    def list_usages_per_user(self, user_login, first=0, limit=20):
        session = self.Session()
        try:
            user = self._get_user(session, user_login)
            uses = session.query(model.DbUserUsedExperiment).filter_by(user=user).offset(first).limit(limit).all()
            return [ use.to_business_light() for use in uses ]
        finally:
            session.close()

    @logged()
    def retrieve_usage(self, usage_id):
        session = self.Session()
        try:
            use = session.query(model.DbUserUsedExperiment).filter_by(id=usage_id).one()
            return use.to_business()
        finally:
            session.close()

    @logged()
    def get_experiment_uses_by_id(self, user_login, reservation_ids):
        """ Retrieve the full information of these reservation_ids, if the user has permissions to do so. By default
         a user can only access to those reservations that he made in the past."""

        results = []
        session = self.Session()
        try:
            user = session.query(model.DbUser).filter_by(login = user_login).first()
            if user is None:
                return [self.forbidden_access] * len(reservation_ids)

            for reservation_id in reservation_ids:
                experiment_use = session.query(model.DbUserUsedExperiment).filter_by(reservation_id = reservation_id.id).first()
                if experiment_use is None:
                    results.append(None)
                else:
                    if experiment_use.user == user:
                        results.append(experiment_use.to_business())
                    else:
                        results.append(self.forbidden_access)
        finally:
            session.close()

        return results

    @with_session
    def is_admin(self, user_login):
        user = _current.session.query(model.DbUser).filter_by(login = user_login).options(joinedload('role')).first()
        if user.role.name in ('administrator', 'admin'):
            return True

        first_admin_permission = _current.session.query(model.DbUserPermission).filter_by(user = user, permission_type=permissions.ADMIN_PANEL_ACCESS).first()
        if first_admin_permission is not None:
            return True

        group_ids = [ group.id for group in user.groups ]
        if len(group_ids) > 0:
            first_admin_permission = _current.session.query(model.DbGroupPermission).filter(model.DbGroupPermission.group_id.in_(group_ids), model.DbGroupPermission.permission_type==permissions.ADMIN_PANEL_ACCESS).first()
            if first_admin_permission is not None:
                return True
        return False

    @logged()
    def get_user_permissions(self, user_login):
        session = self.Session()
        try:
            user = self._get_user(session, user_login)
            user_permissions = []
            for pt in permissions.permission_types:
                user_permissions.extend(self._gather_permissions(session, user, pt))
            dto_permissions = [ permission.to_dto() for permission in user_permissions ]
            return tuple(dto_permissions)
        finally:
            session.close()

    def _get_user(self, session, user_login):
        try:
            return session.query(model.DbUser).filter_by(login=user_login).one()
        except NoResultFound:
            raise DbErrors.DbProvidedUserNotFoundError("Unable to find a User with the provided login: '%s'" % user_login)

    @with_session
    def get_experiment(self, experiment_name, category_name):
        result = _current.session.query(model.DbExperiment) \
                .filter(model.DbExperimentCategory.name == category_name) \
                .filter_by(name=experiment_name).first()
        if result is not None:
            return result.to_business()
        return None
 
    def _get_experiment(self, session, exp_name, cat_name):
        try:
            return session.query(model.DbExperiment) \
                        .filter(model.DbExperimentCategory.name == cat_name) \
                        .filter_by(name=exp_name).one()
        except NoResultFound:
            raise DbErrors.DbProvidedExperimentNotFoundError("Unable to find an Experiment with the provided unique id: '%s@%s'" % (exp_name, cat_name))

    def _gather_groups_permissions(self, session, group, permission_type_name, permissions, remaining_list):
        if group.id in remaining_list:
            return

        remaining_list.append(group.id)
        self._add_or_replace_permissions(permissions, self._get_permissions(session, group, permission_type_name))
        
        if group.parent is not None:
            self._gather_groups_permissions(session, group.parent, permission_type_name, permissions, remaining_list)
        
        

    def _gather_permissions(self, session, user, permission_type_name):
        permissions = []
        self._add_or_replace_permissions(permissions, self._get_permissions(session, user.role, permission_type_name))

        remaining_list = []
        for group in user.groups:
            self._gather_groups_permissions(session, group, permission_type_name, permissions, remaining_list)

        self._add_or_replace_permissions(permissions, self._get_permissions(session, user, permission_type_name))
        return permissions

    def _add_or_replace_permissions(self, permissions, permissions_to_add):
        permissions.extend(permissions_to_add)

    def _get_permissions(self, session, user_or_role_or_group, permission_type_name):
        if isinstance(user_or_role_or_group, model.DbGroup):
            return session.query(model.DbGroupPermission).filter_by(group = user_or_role_or_group, permission_type = permission_type_name).options(joinedload('parameters')).all()

        if isinstance(user_or_role_or_group, model.DbUser):
            return session.query(model.DbUserPermission).filter_by(user = user_or_role_or_group, permission_type = permission_type_name).options(joinedload('parameters')).all()

        if isinstance(user_or_role_or_group, model.DbRole):
            return session.query(model.DbRolePermission).filter_by(role = user_or_role_or_group, permission_type = permission_type_name).options(joinedload('parameters')).all()

        raise Exception("Unknown type: {0}".format(user_or_role_or_group))

    def _get_parameter_from_permission(self, session, permission, parameter_name, default_value = DEFAULT_VALUE):
        try:
            param = [ p for p in permission.parameters if p.get_name() == parameter_name ][0]
        except IndexError:
            if default_value == DEFAULT_VALUE:
                raise DbErrors.DbIllegalStatusError(
                    permission.get_permission_type() + " permission without " + parameter_name
                )
            else:
                return default_value
        return param.value

    def _get_float_parameter_from_permission(self, session, permission, parameter_name, default_value = DEFAULT_VALUE):
        value = self._get_parameter_from_permission(session, permission, parameter_name, default_value)
        try:
            return float(value)
        except ValueError:
            raise DbErrors.InvalidPermissionParameterFormatError(
                "Expected float as parameter '%s' of '%s', found: '%s'" % (
                    parameter_name,
                    permission.get_permission_type(),
                    value
                )
            )

    def _get_int_parameter_from_permission(self, session, permission, parameter_name, default_value = DEFAULT_VALUE):
        value = self._get_parameter_from_permission(session, permission, parameter_name, default_value)
        try:
            return int(value)
        except ValueError:
            raise DbErrors.InvalidPermissionParameterFormatError(
                "Expected int as parameter '%s' of '%s', found: '%s'" % (
                    parameter_name,
                    permission.get_permission_type(),
                    value
                )
            )

    def _get_bool_parameter_from_permission(self, session, permission, parameter_name, default_value = DEFAULT_VALUE):
        return self._get_parameter_from_permission(session, permission, parameter_name, default_value)

    def _delete_all_uses(self):
        """ IMPORTANT: SHOULD NEVER BE USED IN PRODUCTION, IT'S HERE ONLY FOR TESTS """
        session = self.Session()
        try:
            uu = session.query(model.DbUserUsedExperiment).all()
            for i in uu:
                session.delete(i)
            session.commit()
        finally:
            session.close()

    def _insert_user_used_experiment(self, user_login, experiment_name, experiment_category_name, start_time, origin, coord_address, reservation_id, end_date, commands = None, files = None):
        """ IMPORTANT: SHOULD NEVER BE USED IN PRODUCTION, IT'S HERE ONLY FOR TESTS """
        if commands is None:
            commands = []

        if files is None:
            files    = []

        session = self.Session()
        try:
            user = session.query(model.DbUser).filter_by(login=user_login).one()
            category = session.query(model.DbExperimentCategory).filter_by(name=experiment_category_name).one()
            experiment = session.query(model.DbExperiment). \
                                    filter_by(name=experiment_name). \
                                    filter_by(category=category).one()
            experiment_id = experiment.id
            exp_use = model.DbUserUsedExperiment(user, experiment, start_time, origin, coord_address, reservation_id, end_date)
            session.add(exp_use)
            session.commit()
            return experiment_id
        finally:
            session.close()

    @logged()
    def retrieve_role_and_user_auths(self, username):
        """ Retrieve the role and user auths for a given username."""
        session = self.Session()
        try:
            try:
                user = session.query(model.DbUser).filter_by(login=username).one()
            except NoResultFound:
                raise DbErrors.DbUserNotFoundError("User '%s' not found in database" % username)

            all_user_auths = session.query(model.DbUserAuth).filter_by(user=user).all()
            
            # 
            sorted_user_auths = sorted(all_user_auths, lambda x, y: cmp(x.auth.priority, y.auth.priority))
            if len(sorted_user_auths) > 0:
                return user.login, user.role.name, [ user_auth.to_business() for user_auth in sorted_user_auths ]
            else:
                raise DbErrors.DbNoUserAuthNorPasswordFoundError(
                        "No UserAuth found"
                    )
        finally:
            session.close()

    @with_session
    def retrieve_avatar_user_auths(self, username):
        user = _current.session.query(model.DbUser).filter_by(login=username).options(joinedload('auths', 'auth', 'auth_type')).first()
        if user is None:
            return None
        return user.email, [ (user_auth.auth.auth_type.name, user_auth.auth.name, user_auth.auth.configuration, user_auth.configuration) 
                    for user_auth in user.auths 
                    if user_auth.auth.auth_type.name in ('FACEBOOK', )]

    @logged()
    def check_external_credentials(self, external_id, system):
        """ Given an External ID, such as the ID in Facebook or Moodle or whatever, and selecting
        the system, return the first username that matches with that user_id. The method will
        expect that the system uses something that starts by the id"""
        session = self.Session()
        try:
            try:
                auth_type = session.query(model.DbAuthType).filter_by(name=system).one()
                if len(auth_type.auths) == 0:
                    raise DbErrors.DbUserNotFoundError("No instance of system '%s' found in database." % system)
            except NoResultFound:
                raise DbErrors.DbUserNotFoundError("System '%s' not found in database" % system)

            try:
                user_auth = session.query(model.DbUserAuth).filter(model.DbUserAuth.auth_id.in_([auth.id for auth in auth_type.auths]), model.DbUserAuth.configuration==external_id).one()
            except NoResultFound:
                raise DbErrors.DbUserNotFoundError("User '%s' not found in database" % external_id)

            user = user_auth.user
            return ValidDatabaseSessionId( user.login, user.role.name)
        finally:
            session.close()

    ###########################################################################
    ##################   grant_external_credentials   #########################
    ###########################################################################
    @logged()
    def grant_external_credentials(self, username, external_id, system):
        """ Given a system and an external_id, grant access with those credentials for user user_id. Before calling
        this method, the system has checked that this user is the owner of external_id and of user_id"""
        session = self.Session()
        try:
            try:
                auth_type = session.query(model.DbAuthType).filter_by(name=system).one()
                auth = auth_type.auths[0]
            except (NoResultFound, KeyError):
                raise DbErrors.DbUserNotFoundError("System '%s' not found in database" % system)

            try:
                user = session.query(model.DbUser).filter_by(login=username).one()
            except NoResultFound:
                raise DbErrors.DbUserNotFoundError("User '%s' not found in database" % user)

            for user_auth in user.auths:
                if user_auth.auth == auth:
                    raise DbErrors.DbUserNotFoundError("User '%s' already has credentials in system %s" % (username, system))

            user_auth = model.DbUserAuth(user = user, auth = auth, configuration=str(external_id))
            session.add(user_auth)
            session.commit()
        finally:
            session.close()

    #####################################################################
    ##################   create_external_user   #########################
    #####################################################################
    @logged()
    def create_external_user(self, external_user, external_id, system, group_names):
        session = self.Session()
        try:
            try:
                auth_type = session.query(model.DbAuthType).filter_by(name=system).one()
                auth = auth_type.auths[0]
            except (NoResultFound, KeyError):
                raise DbErrors.DbUserNotFoundError("System '%s' not found in database" % system)

            groups = []
            for group_name in group_names:
                try:
                    group = session.query(model.DbGroup).filter_by(name=group_name).one()
                except NoResultFound:
                    raise DbErrors.DbUserNotFoundError("Group '%s' not found in database" % group_name)
                groups.append(group)

            try:
                role = session.query(model.DbRole).filter_by(name=external_user.role.name).one()
                user = model.DbUser(external_user.login, external_user.full_name, external_user.email, role = role)
                user_auth = model.DbUserAuth(user, auth, configuration = external_id)
                for group in groups:
                    group.users.append(user)
                session.add(user)
                session.add(user_auth)
                session.commit()
            except Exception as e:
                log.log( DatabaseGateway, log.level.Warning, "Couldn't create user: %s" % e)
                log.log_exc(DatabaseGateway, log.level.Info)
                raise DbErrors.DatabaseError("Couldn't create user! Contact administrator")
        finally:
            session.close()

    # Location updater
    @with_session
    def reset_locations_database(self):
        update_stmt = sql.update(model.DbUserUsedExperiment).values(hostname = None, city = None, most_specific_subdivision = None, country = None)
        _current.session.execute(update_stmt)
        _current.session.commit()

    @with_session
    def reset_locations_cache(self):
        _current.session.query(model.DbLocationCache).delete()
        _current.session.commit()

    @with_session
    def update_locations(self, location_func):
        """update_locations(location_func) -> number_of_updated
        
        update_locations receives a location_func which receives an IP address and
        returns the location in the following format:
        {
            'hostname': 'foo.fr', # or None
            'city': 'Bilbao', # or None
            'country': 'Spain', # or None
            'most_specific_subdivision': 'Bizkaia' # or None
        }

        If there is an error checking the data, it will simply return None.
        If the IP address is local, it will simply fill the hostname URL.

        update_locations will return the number of successfully changed registries.
        So if there were 10 IP addresses to be changed, and it failed in 5 of them,
        it will return 5. This way, the loop calling this function can sleep only if
        the number is zero.
        """
        counter = 0
        uses_without_location = list(_current.session.query(model.DbUserUsedExperiment).filter_by(hostname = None).limit(1024).all()) # Do it iterativelly, never process more than 1024 uses
        origins = set()
        for use in uses_without_location:
            origins.add(use.origin)

        if origins:
            cached_origins = {
                # origin: result
            }
            last_month = datetime.datetime.utcnow() - datetime.timedelta(days = 31)
            for cached_origin in  _current.session.query(model.DbLocationCache).filter(model.DbLocationCache.ip.in_(origins), model.DbLocationCache.lookup_time > last_month).all():
                cached_origins[cached_origin.ip] = {
                    'city' : cached_origin.city,
                    'hostname': cached_origin.hostname,
                    'country': cached_origin.country,
                    'most_specific_subdivision' : cached_origin.most_specific_subdivision,
                }

            for use in uses_without_location:
                if use.origin in cached_origins:
                    use.city = cached_origins[use.origin]['city']
                    use.hostname = cached_origins[use.origin]['hostname']
                    use.country = cached_origins[use.origin]['country']
                    use.most_specific_subdivision = cached_origins[use.origin]['most_specific_subdivision']
                    counter += 1
                else:
                    try:
                        result = location_func(use.origin)
                    except Exception:
                        traceback.print_exc()
                        continue
                    use.city = result['city']
                    use.hostname = result['hostname']
                    use.country = result['country']
                    use.most_specific_subdivision = result['most_specific_subdivision']
                    cached_origins[use.origin] = result
                    new_cached_result = model.DbLocationCache(ip = use.origin, lookup_time = datetime.datetime.utcnow(), hostname = result['hostname'], city = result['city'], country = result['country'], most_specific_subdivision = result['most_specific_subdivision'])
                    _current.session.add(new_cached_result)
                    counter += 1

            try:
                _current.session.commit()
            except Exception:
                traceback.print_exc()

        return counter

    # Admin default

    @with_session
    def frontend_admin_uses_last_week(self):
        now = datetime.datetime.utcnow() # Not UTC
        since = now + relativedelta(days=-7)
        group = (model.DbUserUsedExperiment.start_date_date,)
        converter = lambda args: args[0]
        date_generator = self._frontend_sequence_day_generator
        return self._frontend_admin_uses_last_something(since, group, converter, date_generator)

    @with_session
    def frontend_admin_uses_last_year(self):
        now = datetime.datetime.utcnow() # Not UTC
        since = (now + relativedelta(years=-1)).replace(day=1) # day=1 is important to search by start_date_month
        group = (model.DbUserUsedExperiment.start_date_year,model.DbUserUsedExperiment.start_date_month)
        converter = lambda args: datetime.date(args[0], args[1], 1)
        date_generator = self._frontend_sequence_month_generator
        return self._frontend_admin_uses_last_something(since, group, converter, date_generator)

    def _frontend_sequence_month_generator(self, since):
        now = datetime.date.today() # Not UTC
        cur_year = since.year
        cur_month = since.month
        cur_date = datetime.date(cur_year, cur_month, 1)
        dates = []
        while cur_date <= now:
            dates.append(cur_date)
            if cur_month == 12:
                cur_month = 1
                cur_year += 1
            else:
                cur_month += 1
            cur_date = datetime.date(cur_year, cur_month, 1)
        return dates

    def _frontend_sequence_day_generator(self, since):
        now = datetime.datetime.today() # Not UTC
        cur_date = since
        dates = []
        while cur_date <= now:
            dates.append(cur_date.date())
            cur_date = cur_date + datetime.timedelta(days = 1)
        return dates

    def _frontend_admin_uses_last_something(self, since, group, converter, date_generator):
        results = {
            # experiment_data : {
            #     datetime.date() : count
            # }
        }
        for row in _current.session.query(sqlalchemy.func.count(model.DbUserUsedExperiment.id), model.DbExperiment.name, model.DbExperimentCategory.name, *group).filter(model.DbUserUsedExperiment.start_date >= since, model.DbUserUsedExperiment.experiment_id == model.DbExperiment.id, model.DbExperiment.category_id == model.DbExperimentCategory.id).group_by(model.DbUserUsedExperiment.experiment_id, *group).all():
            count = row[0]
            experiment = '@'.join((row[1], row[2]))
            if experiment not in results:
                results[experiment] = {}
            results[experiment][converter(row[3:])] = count

        for date in date_generator(since):
            for experiment_id in results:
                results[experiment_id].setdefault(date, 0)

        return results

    @with_session
    def frontend_admin_uses_geographical_month(self):
        # This is really in the last literal month
        now = datetime.datetime.utcnow()
        since = now + relativedelta(months = -1)
        return self.quickadmin_uses_per_country(UsesQueryParams.create(start_date=since))

    @with_session
    def frontend_admin_latest_uses(self):
        return self.quickadmin_uses(limit = 10, query_params=UsesQueryParams.create())
      

    # Quickadmin
    def _apply_filters(self, query, query_params):
        if query_params.login:
            query = query.join(model.DbUserUsedExperiment.user).filter(model.DbUser.login == query_params.login)

        if query_params.experiment_name:
            query = query.join(model.DbUserUsedExperiment.experiment).filter(model.DbExperiment.name == query_params.experiment_name)

        if query_params.category_name:
            query = query.join(model.DbUserUsedExperiment.experiment).join(model.DbExperiment.category).filter(model.DbExperimentCategory.name == query_params.category_name)

        if query_params.group_names is not None:
            if len(query_params.group_names) == 0:
                # Automatically filter that there is no
                return query.filter(model.DbUser.login == None, model.DbUser.login != None)

            query = query.join(model.DbUserUsedExperiment.user).filter(model.DbUser.groups.any(model.DbGroup.name.in_(query_params.group_names)))

        if query_params.start_date:
            query = query.filter(model.DbUserUsedExperiment.start_date >= query_params.start_date)

        if query_params.end_date:
            query = query.filter(model.DbUserUsedExperiment.end_date <= query_params.end_date + datetime.timedelta(days=1))

        if query_params.ip:
            query = query.filter(model.DbUserUsedExperiment.origin == query_params.ip)

        if query_params.country:
            query = query.filter(model.DbUserUsedExperiment.country == query_params.country)

        return query
       
    @with_session
    def quickadmin_uses(self, limit, query_params):
        db_latest_uses_query = _current.session.query(model.DbUserUsedExperiment)

        db_latest_uses_query = self._apply_filters(db_latest_uses_query, query_params)

        db_latest_uses = db_latest_uses_query.options(joinedload("user"), joinedload("experiment"), joinedload("experiment", "category"), joinedload("properties")).order_by(model.DbUserUsedExperiment.start_date.desc()).limit(limit).offset((query_params.page - 1) * limit)

        external_user = _current.session.query(model.DbUserUsedExperimentProperty).filter_by(name = 'external_user').first()
        latest_uses = []
        for use in db_latest_uses:
            login = use.user.login
            display_name = login
            for prop in use.properties:
                if prop.property_name == external_user:
                    display_name = prop.value + u'@' + login

            if use.start_date:
                if use.end_date is None:
                    duration = datetime.datetime.utcnow() - use.start_date
                else:
                    duration = use.end_date - use.start_date
            else:
                duration = datetime.timedelta(seconds = 0)

            # Avoid microseconds
            duration_without_microseconds = datetime.timedelta(seconds = int(duration.total_seconds()))

            latest_uses.append({
                'id' : use.id,
                'login' : login,
                'display_name' : display_name,
                'full_name' : use.user.full_name,
                'experiment_name' : use.experiment.name,
                'category_name' : use.experiment.category.name,
                'start_date' : use.start_date,
                'end_date' : use.end_date,
                'from' : use.origin,
                'city' : use.city,
                'country' : use.country,
                'hostname' : use.hostname,
                'duration' : duration_without_microseconds,
            })
        return latest_uses

    @with_session
    def quickadmin_uses_per_country(self, query_params):
        db_latest_uses_query = _current.session.query(model.DbUserUsedExperiment.country, sqlalchemy.func.count(model.DbUserUsedExperiment.id)).filter(model.DbUserUsedExperiment.country != None)
        db_latest_uses_query = self._apply_filters(db_latest_uses_query, query_params)
        return dict(db_latest_uses_query.group_by(model.DbUserUsedExperiment.country).all())

    def quickadmin_uses_per_country_by(self, query_params):
        if query_params.date_precision == 'year':
            return self.quickadmin_uses_per_country_by_year(query_params)
        if query_params.date_precision == 'month':
            return self.quickadmin_uses_per_country_by_month(query_params)
        if query_params.date_precision == 'day':
            return self.quickadmin_uses_per_country_by_day(query_params)
        return {} 

    @with_session
    def quickadmin_uses_per_country_by_day(self, query_params):
        # country, count, year, month
        initial_query = _current.session.query(model.DbUserUsedExperiment.country, sqlalchemy.func.count(model.DbUserUsedExperiment.id), model.DbUserUsedExperiment.start_date_date)
        group_by = (model.DbUserUsedExperiment.country, model.DbUserUsedExperiment.start_date_date)
        return self._quickadmin_uses_per_country_by_date(query_params, initial_query, group_by)

    @with_session
    def quickadmin_uses_per_country_by_month(self, query_params):
        # country, count, year, month
        initial_query = _current.session.query(model.DbUserUsedExperiment.country, sqlalchemy.func.count(model.DbUserUsedExperiment.id), model.DbUserUsedExperiment.start_date_year, model.DbUserUsedExperiment.start_date_month)
        group_by = (model.DbUserUsedExperiment.country, model.DbUserUsedExperiment.start_date_year, model.DbUserUsedExperiment.start_date_month)
        return self._quickadmin_uses_per_country_by_date(query_params, initial_query, group_by)

    @with_session
    def quickadmin_uses_per_country_by_year(self, query_params):
        # country, count, year
        initial_query = _current.session.query(model.DbUserUsedExperiment.country, sqlalchemy.func.count(model.DbUserUsedExperiment.id), model.DbUserUsedExperiment.start_date_year)
        group_by = (model.DbUserUsedExperiment.country, model.DbUserUsedExperiment.start_date_year)
        return self._quickadmin_uses_per_country_by_date(query_params, initial_query, group_by)

    def _quickadmin_uses_per_country_by_date(self, query_params, initial_query, group_by):
        db_latest_uses_query = initial_query.filter(model.DbUserUsedExperiment.country != None)
        db_latest_uses_query = self._apply_filters(db_latest_uses_query, query_params)
        countries = {
            # country : [
            #     [ (year, month), count ]
            # ]
        }
        for row in db_latest_uses_query.group_by(*group_by).all():
            country = row[0]
            count = row[1]
            key = tuple(row[2:])
            if country not in countries:
                countries[country] = []
            countries[country].append((key, count))
            # Sort by the union of the keys
            countries[country].sort(lambda x, y: cmp('-'.join([ unicode(v).zfill(8) for v in x[0]]), '-'.join([ unicode(v).zfill(8) for v in y[0]])))
        return countries

    @with_session
    def quickadmin_uses_metadata(self, query_params):
        db_metadata_query = _current.session.query(sqlalchemy.func.min(model.DbUserUsedExperiment.start_date), sqlalchemy.func.max(model.DbUserUsedExperiment.start_date), sqlalchemy.func.count(model.DbUserUsedExperiment.id))
        db_metadata_query = self._apply_filters(db_metadata_query, query_params)
        first_element = db_metadata_query.first()
        if first_element:
            min_date, max_date, count = first_element
            return dict(min_date = min_date, max_date = max_date, count = count)

        return dict(min_date = datetime.datetime.utcnow(), max_date = datetime.datetime.now(), count = 0)


    @with_session
    def quickadmin_use(self, use_id):
        use = _current.session.query(model.DbUserUsedExperiment).filter_by(id = use_id).options(joinedload("user"), joinedload("experiment"), joinedload("experiment", "category"), joinedload("properties")).first()
        if not use:
            return {'found' : False}
        
        def get_prop(prop_name, default):
            return ([ prop.value for prop in use.properties if prop.property_name.name == prop_name ] or [ default ])[0]
            
        experiment = use.experiment.name + u'@' + use.experiment.category.name

        properties = OrderedDict()
        properties['Login'] = use.user.login
        properties['Name'] = use.user.full_name
        properties['In the name of'] = get_prop('external_user', 'Himself')
        properties['Experiment'] = experiment
        properties['Date'] = use.start_date
        properties['Origin'] = use.origin
        properties['Device used'] = use.coord_address
        properties['Server IP (if federated)'] = get_prop('from_direct_ip', use.origin)
        properties['Use ID'] = use.id
        properties['Reservation ID'] = use.reservation_id
        properties['Mobile'] = get_prop('mobile', "Don't know")
        properties['Facebook'] = get_prop('facebook', "Don't know")
        properties['Referer'] = get_prop('referer', "Don't know")
        properties['Web Browser'] = get_prop('user_agent', "Don't know")
        properties['Route'] = get_prop('route', "Don't know")
        properties['Locale'] = get_prop('locale', "Don't know")
        properties['City'] = use.city or 'Unknown'
        properties['Country'] = use.country or 'Unknown'
        properties['Hostname'] = use.hostname or 'Unknown'

        commands = []
        longest_length = 0
        for command in use.commands:
            timestamp_after = command.timestamp_after
            timestamp_before = command.timestamp_before
            if timestamp_after is not None and command.timestamp_after_micro is not None:
                timestamp_after = timestamp_after.replace(microsecond = command.timestamp_after_micro)

            if timestamp_before is not None and command.timestamp_before_micro is not None:
                timestamp_before = timestamp_before.replace(microsecond = command.timestamp_before_micro)

            if timestamp_after and timestamp_before:
                length = (timestamp_after - timestamp_before).total_seconds()
                if length > longest_length:
                    longest_length = length
            else:
                length = 'N/A'
            
            commands.append({
                'length' : length,
                'before' : timestamp_before,
                'after' : timestamp_after,
                'command' : command.command,
                'response' : command.response,
            })
               
        properties['Longest command'] = longest_length

        files = []
        for f in use.files:
            timestamp_after = f.timestamp_after
            timestamp_before = f.timestamp_before
            if timestamp_after is not None and f.timestamp_after_micro is not None:
                timestamp_after = timestamp_after.replace(microsecond = f.timestamp_after_micro)

            if timestamp_before is not None and f.timestamp_before_micro is not None:
                timestamp_before = timestamp_before.replace(microsecond = f.timestamp_before_micro)

            if timestamp_after and timestamp_before:
                length = (timestamp_after - timestamp_before).total_seconds()
                if length > longest_length:
                    longest_length = length
            else:
                length = 'N/A'

            files.append({
                'file_id' : f.id,
                'length' : length,
                'before' : timestamp_before,
                'after' : timestamp_after,
                'file_info' : f.file_info,
                'file_hash' : f.file_hash,
                'response' : command.response,
            })

        return {
            'found' : True,
            'properties' : properties,
            'commands' : commands,
            'files' : files,
        }       

    @with_session
    def quickadmin_filepath(self, file_id):
        use = _current.session.query(model.DbUserFile).filter_by(id = file_id).first()
        if use is None:
            return None
        initial_path = self.cfg_manager.get(configuration_doc.CORE_STORE_STUDENTS_PROGRAMS_PATH)
        if not initial_path:
            return None
        full_path = os.path.join(initial_path, use.file_sent)
        if not os.path.exists(full_path):
            return None

        return full_path

    @with_session
    def client_configuration(self):
        return dict([ (cp.name, cp.value) for cp in _current.session.query(model.DbClientProperties).all() ])

    @with_session
    def server_configuration(self):
        return dict([ (cp.name, cp.value) for cp in _current.session.query(model.DbServerProperties).all() ])

    @with_session
    def store_configuration(self, client_properties, server_properties):
        self._store_configuration(client_properties, model.DbClientProperties)
        self._store_configuration(server_properties, model.DbServerProperties)
        try:
            _current.session.commit()
        except sqlalchemy.exc.SQLAlchemyError:
            _current.session.rollback()
            raise

    def _store_configuration(self, properties, klass):
        properties = dict(properties)
        for cp in _current.session.query(klass).all():
            if cp.name in properties:
                cp.value = properties.pop(cp.name)
                _current.session.add(cp)

        for name, value in six.iteritems(properties):
            new_property = klass(name=name, value=value)
            _current.session.add(new_property)

    @with_session
    def list_user_logins(self):
        return [ row[0] for row in _current.session.query(model.DbUser.login).all() ]

    @with_session
    def latest_uses_experiment_user(self, experiment_name, category_name, login, limit):
        user_row = _current.session.query(model.DbUser.id).filter_by(login=login).first()
        if user_row is None:
            return []

        user_id = user_row[0]

        category = _current.session.query(model.DbExperimentCategory).filter_by(name=category_name).first()
        if category is None:
            return []

        experiment_row = _current.session.query(model.DbExperiment.id).filter_by(name=experiment_name, category=category).first()
        if experiment_row is None:
            return []

        experiment_id = experiment_row[0]

        data = []
        for start_date, country, origin, use_id in _current.session.query(model.DbUserUsedExperiment.start_date, model.DbUserUsedExperiment.country, model.DbUserUsedExperiment.origin, model.DbUserUsedExperiment.id).filter_by(user_id=user_id, experiment_id=experiment_id).order_by(model.DbUserUsedExperiment.start_date.desc()).limit(limit).all():
            data.append({
                'id': use_id,
                'start_date': start_date,
                'country': country,
                'origin': origin,
            })

        return data

    @with_session
    def get_experiment_stats(self, experiment_name, category_name):
        category = _current.session.query(model.DbExperimentCategory).filter_by(name=category_name).first()
        if category is None:
            return []

        experiment_row = _current.session.query(model.DbExperiment.id).filter_by(name=experiment_name, category=category).first()
        if experiment_row is None:
            return []

        experiment_id = experiment_row[0]

        now = datetime.datetime.now()
        last_year = now + relativedelta(years=-1)
        last_month = now + relativedelta(months=-1)

        total_uses = _current.session.query(func.count(model.DbUserUsedExperiment.id)).filter_by(experiment_id=experiment_id).first()[0]
        total_uses_last_month = _current.session.query(func.count(model.DbUserUsedExperiment.id)).filter(model.DbUserUsedExperiment.experiment_id == experiment_id, model.DbUserUsedExperiment.start_date >= last_month).first()
        total_uses_last_year = _current.session.query(func.count(model.DbUserUsedExperiment.id)).filter(model.DbUserUsedExperiment.experiment_id == experiment_id, model.DbUserUsedExperiment.start_date >= last_year).first()

        return {
            'total_uses': total_uses,
            'total_uses_last_month': total_uses_last_month,
            'total_uses_last_year': total_uses_last_year,
        }


def create_gateway(cfg_manager):
    return DatabaseGateway(cfg_manager)

