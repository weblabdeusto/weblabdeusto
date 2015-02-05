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
#         Luis Rodriguez <luis.rodriguez@opendeusto.es>

import os
import sys
import datetime
import random
import sha
import traceback
import weblab.configuration_doc as configuration_doc
import weblab.permissions as permissions
from voodoo.dbutil import get_sqlite_dbname

from console_ui import ConsoleUI
from exc import GoBackError

from db import DbGateway
from smtp import SmtpGateway
try:
    from weblab.admin.ldap_gateway import LdapGateway
    LdapGatewayClass = LdapGateway
except ImportError:
    LdapGatewayClass = None

def get_variable(dictionary, name):
    default = configuration_doc.variables[name].default
    if default == configuration_doc.NO_DEFAULT:
        return dictionary[name]
    else:
        return dictionary.get(name, default)

class DbConfiguration(object):
    def __init__(self, configuration_files, configuration_values):

        for configuration_file in configuration_files:
            if not os.path.exists(configuration_file):
                print >> sys.stderr, "Could not find configuration file", configuration_file
                sys.exit(1)

            globals()['CURRENT_PATH'] = configuration_file
            execfile(configuration_file, globals(), globals())    

        global_vars = globals()

        for key, value in (configuration_values or []):
            global_vars[key] = value

        self.db_host           = get_variable(global_vars, configuration_doc.DB_HOST)
        self.db_port           = get_variable(global_vars, configuration_doc.DB_PORT)
        self.db_engine         = get_variable(global_vars, configuration_doc.DB_ENGINE)
        self.db_name           = get_variable(global_vars, configuration_doc.DB_DATABASE)
        self.db_user           = get_variable(global_vars, configuration_doc.DB_USERNAME)
        self.db_pass           = get_variable(global_vars, configuration_doc.DB_PASSWORD)

        if get_variable(global_vars, configuration_doc.COORDINATOR_IMPL) == 'sqlalchemy':
            self.coord_db_host     = get_variable(global_vars, configuration_doc.COORDINATOR_DB_HOST)
            self.coord_db_port     = get_variable(global_vars, configuration_doc.COORDINATOR_DB_PORT)
            self.coord_db_engine   = get_variable(global_vars, configuration_doc.COORDINATOR_DB_ENGINE)
            self.coord_db_name     = get_variable(global_vars, configuration_doc.COORDINATOR_DB_NAME)
            self.coord_db_user     = get_variable(global_vars, configuration_doc.COORDINATOR_DB_USERNAME)
            self.coord_db_pass     = get_variable(global_vars, configuration_doc.COORDINATOR_DB_PASSWORD)
        else:
            self.coord_db_host = self.coord_db_port = self.coord_db_engine = self.coord_db_name = self.coord_db_user = self.coord_db_pass = None


    def build_url(self):
        if self.db_engine == 'sqlite':
            return 'sqlite:///%s' % get_sqlite_dbname(self.db_name)
        else:
            return "%(ENGINE)s://%(USER)s:%(PASSWORD)s@%(HOST)s/%(DATABASE)s" % \
                            { "ENGINE":   self.db_engine,
                              "USER":     self.db_user, "PASSWORD": self.db_pass,
                              "HOST":     self.db_host, "DATABASE": self.db_name }
    
    def build_coord_url(self):
        if self.coord_db_engine is None:
            return None
        elif self.coord_db_engine == 'sqlite':
            return 'sqlite:///%s' % get_sqlite_dbname(self.coord_db_name)
        else:
            return "%(ENGINE)s://%(USER)s:%(PASSWORD)s@%(HOST)s/%(DATABASE)s" % \
                            { "ENGINE":   self.coord_db_engine,
                              "USER":     self.coord_db_user, "PASSWORD": self.coord_db_pass,
                              "HOST":     self.coord_db_host, "DATABASE": self.coord_db_name }

class Controller(object):

    def __init__(self, configuration_files = None, configuration_values = None):
        super(Controller, self).__init__()

        db_conf = DbConfiguration(configuration_files, configuration_values)
        self.db_host   = db_conf.db_host
        self.db_port   = db_conf.db_port
        self.db_engine = db_conf.db_engine
        self.db_name   = db_conf.db_name
        self.db_user   = db_conf.db_user
        self.db_pass   = db_conf.db_pass

        self.smtp_host         = globals().get(configuration_doc.MAIL_SERVER_HOST)
        self.smtp_helo         = globals().get(configuration_doc.MAIL_SERVER_HELO)

        self.default_db_name   = self.db_name
        self.default_db_user   = self.db_user
        self.default_db_pass   = self.db_pass

        self.default_ldap_users_file   = 'USERS'
        self.default_openid_users_file = 'USERSOID'
        self.default_db_users_file     = 'USERSDB'

        self.default_notification_from    = globals().get(configuration_doc.MAIL_NOTIFICATION_SENDER)
        self.default_notification_bcc     = globals().get(configuration_doc.SERVER_ADMIN)
        self.default_notification_subject = 'WebLab-Deusto notification'

        self.default_notification_text_file = 'NOTIFICATION'
        self.default_notification_with_password_text_file = 'NOTIFICATION_WITH_PASSWORD'

        self.ui = ConsoleUI()
        self.init()
        self.menu()

    def init(self):
        if self.db_name is not None and self.db_user is not None and self.db_pass is not None:
            self.db = DbGateway(self.db_engine, self.db_host, self.db_port, self.db_name, self.db_user, self.db_pass)
        else:
            db_name, db_user, db_pass = self.ui.dialog_init(self.default_db_name, self.default_db_user, self.default_db_pass)
            self.db = DbGateway(self.db_engine, self.db_host, self.db_port, db_name, db_user, db_pass)

    def menu(self):
        option = None
        while option != 0:
            option = self.ui.dialog_menu()
            if option == 1:
                self.add_group()
            elif option == 2:
                self.add_experiment_category()
            elif option == 3:
                self.add_experiment()
            elif option == 4:
                self.add_users_to_group_file()
            elif option == 5:
                self.add_users_to_group()
            elif option == 6:
                self.add_user_with_db_authtype()
            elif option == 7:
                self.add_users_with_ldap_authtype()
            elif option == 8:
                self.add_users_with_openid_authtype()
            elif option == 9:
                self.add_users_batch_with_db_authtype()
            elif option == 10:
                self.grant_on_experiment_to_group()
            elif option == 11:
                self.grant_on_experiment_to_user()
            elif option == 12:
                self.grant_on_admin_panel_to_group()
            elif option == 13:
                self.grant_on_admin_panel_to_user()
            elif option == 14:
                self.grant_on_access_forward_to_group()
            elif option == 15:
                self.grant_on_access_forward_to_user()
            elif option == 16:
                self.list_users()
            elif option == 17:
                self.notify_users()
            elif option == 18:
                self.notify_users_with_passwords()
        self.ui.dialog_exit()
        sys.exit(0)

    def add_group(self):
        groups = self.db.get_groups()
        group_names = [ (group.id, group.name) for group in groups ]
        try:
            group_name, parent_group_id = self.ui.dialog_add_group(group_names)
            parent_group = [ group for group in groups if group.id == parent_group_id ][0] if parent_group_id is not None else None
            group = self.db.insert_group(group_name, parent_group)
            if group is not None:
                self.ui.notify("Group created:\n%r" % group)
            else:
                self.ui.error("The Group '%s' already exists." % group_name)
            self.ui.wait()
        except GoBackError:
            return


    def add_experiment_category(self):
        try:
            category_name = self.ui.dialog_add_experiment_category()
            category = self.db.insert_experiment_category(category_name)
            if category is not None:
                self.ui.notify("ExperimentCategory created:\n%r" % category)
            else:
                self.ui.error("The ExperimentCategory '%s' already exists." % category_name)
            self.ui.wait()
        except GoBackError:
            return

    def add_experiment(self):
        categories = self.db.get_experiment_categories()
        category_names = [ (category.id, category.name) for category in categories ]
        try:
            experiment_name, category_id = self.ui.dialog_add_experiment(category_names)
            category = [ category for category in categories if category.id == category_id ][0]
            start_date = datetime.datetime.utcnow()
            end_date = start_date.replace(year=start_date.year+12)
            experiment = self.db.insert_experiment(experiment_name, category, start_date, end_date)
            if experiment is not None:
                self.ui.notify("Experiment created:\n%r" % experiment)
            else:
                self.ui.error("The Experiment '%s' already exists." % experiment_name)
            self.ui.wait()
        except GoBackError:
            return

    def add_users_to_group_file(self):
        groups = self.db.get_groups()
        group_names = [ (group.id, group.name) for group in groups ]
        try:
            group_id, user_logins = self.ui.dialog_add_users_to_group_file(group_names, self.default_ldap_users_file)
            group = [ group for group in groups if group.id == group_id ][0]
            users = self.db.get_users(user_logins)
            if len(user_logins) > 0:
                self.ui.notify("The following Users have been added to the Group:\n%r" % group)
                error_users = []
                for user in users:
                    u, g = self.db.add_user_to_group(user, group)
                    if (u, g) is not (None, None):
                        self.ui.notify("%r" % u)
                    else:
                        error_users.append(user)
                self.ui.notify("Total added Users: %i" % (len(users)-len(error_users)))
                if len(error_users) > 0:
                    self.ui.error("Warning! The following Users could not be added to the Group: %r" % error_users)
                if len(user_logins) > len(users):
                    self.ui.notify("Warning! %i Users did not exist in the database." % (len(user_logins) - len(users)))
            else:
                self.ui.error("There are no Users to be added to the Group.")
            self.ui.wait()
        except GoBackError:
            return
       

    def add_users_to_group(self):
        groups = self.db.get_groups()
        users  = self.db.get_users()
        group_names = [ (group.id, group.name) for group in groups ]
        user_logins = [ (user.id, user.login) for user in users]
        user_logins_dict = dict(user_logins)
        try:
            group_id, user_id = self.ui.dialog_add_users_to_group(group_names, user_logins)
            user_logins = [user_logins_dict[user_id]]
            group = [ group for group in groups if group.id == group_id ][0]
            users = self.db.get_users(user_logins)
            if len(user_logins) > 0:
                self.ui.notify("The following Users have been added to the Group:\n%r" % group)
                error_users = []
                for user in users:
                    u, g = self.db.add_user_to_group(user, group)
                    if (u, g) is not (None, None):
                        self.ui.notify("%r" % u)
                    else:
                        error_users.append(user)
                self.ui.notify("Total added Users: %i" % (len(users)-len(error_users)))
                if len(error_users) > 0:
                    self.ui.error("Warning! The following Users could not be added to the Group: %r" % error_users)
                if len(user_logins) > len(users):
                    self.ui.notify("Warning! %i Users did not exist in the database." % (len(user_logins) - len(users)))
            else:
                self.ui.error("There are no Users to be added to the Group.")
            self.ui.wait()
        except GoBackError:
            return

    def add_user_with_db_authtype(self):
        roles = self.db.get_roles()
        role_names = [ (role.id, role.name) for role in roles ]
        auths = self.db.get_auths("DB")
        auth_names = [ (auth.id, auth.name) for auth in auths ]
        try:
            # Note: The following user_auth_config is the password
            login, full_name, email, avatar, role_id, auth_id, user_auth_config = self.ui.dialog_add_user_with_db_authtype(role_names, auth_names)
            role = [ role for role in roles if role.id == role_id ][0] if role_id is not None else None
            auth = [ auth for auth in auths if auth.id == auth_id ][0]
            user = self.db.insert_user(login, full_name, email, avatar, role)
            if user is not None:
                self.ui.notify("User created:\n%r" % user)
                user_auth = self.db.insert_user_auth(user, auth, self._password2sha(user_auth_config))
                assert user_auth is not None
                self.ui.notify("UserAuth created:\n%r" % user_auth)
            else:
                self.ui.error("The User '%s' already exists." % login)
            self.ui.wait()
        except GoBackError:
            return

    def add_users_batch_with_db_authtype(self):
        # Retrieve every role from the database
        roles = self.db.get_roles()
        role_names = [ (role.id, role.name) for role in roles ]

        # Retrieve every DB auth
        auths = self.db.get_auths("DB")
        auth_names = [ (auth.id, auth.name) for auth in auths ]

        try:

            # Get the data (asking the user if needed) about the users to add and the
            # role to assign them.
            user_logins, role_id = self.ui.dialog_add_users_batch_with_db_authtype(
                                                            role_names,
                                                            auth_names,
                                                            self.default_db_users_file
                                                        )

            # Get the actual role object through the role id we obtained before.
            role = [ role for role in roles if role.id == role_id ][0] if role_id is not None else None

            # Get the first DB auth. We will assume that there is one at most.
            if len(auths) < 1:
                self.ui.error("There is no auth available of the type DB")
            auth = auths[0]

            for user_data in user_logins:
                # create the user object using the login, full name, email and password we have
                # retrieved from the provided DB USERS file.
                user = self.db.insert_user(user_data[0], user_data[1], user_data[2], None, role)
                if user is not None:
                    self.ui.notify("User created:\n%r" % user)
                    user_auth = self.db.insert_user_auth(user, auth, self._password2sha(user_data[3]))
                    assert user_auth is not None
                    self.ui.notify("UserAuth created:\n%r" % user_auth)
                else:
                    self.ui.error("The User '%s' already exists." % str(user_data) )
            self.ui.wait()

        except GoBackError:
            return

    def add_users_with_ldap_authtype(self):
        if LdapGatewayClass is None:
            self.ui.error("LDAP is not available. Is python-ldap installed?")
            self.ui.wait()
            return
        roles = self.db.get_roles()
        role_names = [ (role.id, role.name) for role in roles ]
        auths = self.db.get_auths("LDAP")
        auth_names = [ (auth.id, auth.name) for auth in auths ]
        try:
            user_logins, role_id, auth_id = self.ui.dialog_add_users_with_ldap_authtype(
                                                            role_names,
                                                            auth_names,
                                                            self.default_ldap_users_file
                                                  )
            role = [ role for role in roles if role.id == role_id ][0] if role_id is not None else None
            auth = [ auth for auth in auths if auth.id == auth_id ][0]
            auth_username, auth_password, auth_domain = self.ui.dialog_authenticate_on_ldap()
            ldap = LdapGatewayClass(auth.get_config_value("ldap_uri"),
                               auth_domain,
                               auth.get_config_value("base"),
                               auth_username, auth_password)

            users_created_successfully = 0
            num_users = len(user_logins)
            for user_data in ldap.get_users(user_logins):
                try:
                    user = self.db.insert_user(user_data["login"], user_data["full_name"], user_data["email"], None, role)
                    if user is not None:
                        self.ui.notify(u"User created:\n%r" % repr(user))
                        user_auth = self.db.insert_user_auth(user, auth, None)
                        assert user_auth is not None
                        self.ui.notify(u"UserAuth created:\n%r" % repr(user_auth))
                        users_created_successfully += 1
                    else:
                        self.ui.error("The User '%s' already exists." % user_data["login"])
                        self.db.session.rollback()
                except Exception, ex:
                    self.ui.error("The User '%s' could not be created. Ignoring him/her. Reason: %s" % (user_data["login"], ex.__repr__()))
                    traceback.print_exc()
            self.ui.notify("Created %d users out of %d." % (users_created_successfully, num_users))
            self.ui.wait()
        except GoBackError:
            return

    def add_users_with_openid_authtype(self):
        # Retrieve every role from the database
        roles = self.db.get_roles()
        role_names = [ (role.id, role.name) for role in roles ]

        # Retrieve every OpenID auth
        auths = self.db.get_auths("OPENID")
        auth_names = [ (auth.id, auth.name) for auth in auths ]

        try:

            # Get the data (asking the user if needed) about the users to add and the
            # role to assign them.
            user_logins, role_id = self.ui.dialog_add_users_with_openid_authtype(
                                                            role_names,
                                                            auth_names,
                                                            self.default_openid_users_file
                                                        )

            # Get the actual role object through the role id we obtained before.
            role = [ role for role in roles if role.id == role_id ][0] if role_id is not None else None

            # Get the first OpenID auth. We will assume that there is one at most.
            if len(auths) < 1:
                self.ui.error("There is no auth available of the type OpenID")
            auth = auths[0]

            for user_data in user_logins:
                # create the user object using the login, full name, and email we have
                # retrieved from the provided OpenID USERS file.
                user = self.db.insert_user(user_data[0], user_data[1], user_data[2], None, role)
                if user is not None:
                    self.ui.notify("User created:\n%r" % user)
                    user_auth = self.db.insert_user_auth(user, auth, user_data[3])
                    assert user_auth is not None
                    self.ui.notify("UserAuth created:\n%r" % user_auth)
                else:
                    self.ui.error("The User '%s' already exists." % str(user_data) )
            self.ui.wait()

        except GoBackError:
            return

    def grant_on_experiment_to_group(self):
        groups = self.db.get_groups()
        group_names = [ (group.id, group.name) for group in groups ]
        experiments = self.db.get_experiments()
        experiment_names = [ (experiment.id, '%s@%s' % (experiment.name, experiment.category.name)) for experiment in experiments ]
        try:
            group_id, experiment_id, time_allowed, priority, initialization_in_accounting = self.ui.dialog_grant_on_experiment_to_group(group_names, experiment_names)
            group = [ group for group in groups if group.id == group_id ][0] if group_id is not None else None
            experiment = [ experiment for experiment in experiments if experiment.id == experiment_id ][0] if experiment_id is not None else None
            experiment_unique_id = "%s@%s" % (experiment.name, experiment.category.name)
            group_permission_permanent_id = "%s::%s" % (group.name, experiment_unique_id)
            group_permission = self.db.grant_on_experiment_to_group(
                    group,
                    permissions.EXPERIMENT_ALLOWED,
                    group_permission_permanent_id,
                    datetime.datetime.utcnow(),
                    "Permission on %s to use %s" % (group.name, experiment_unique_id),
                    experiment,
                    time_allowed,
                    priority,
                    initialization_in_accounting
            )
            if group_permission is not None:
                self.ui.notify("GroupPermission created:\n%r" % group_permission)
                for parameter in group_permission.parameters:
                    self.ui.notify("GroupPermissionParameter created:\n%r" % parameter)
            else:
                self.ui.error("The GroupPermission '%s' already exists." % group_permission_permanent_id)
            self.ui.wait()
        except GoBackError:
            return

    def grant_on_experiment_to_user(self):
        users = self.db.get_users()
        user_names = [ (user.id, user.login) for user in users ]
        experiments = self.db.get_experiments()
        experiment_names = [ (experiment.id, '%s@%s' % (experiment.name, experiment.category.name)) for experiment in experiments ]
        try:
            user_id, experiment_id, time_allowed, priority, initialization_in_accounting = self.ui.dialog_grant_on_experiment_to_user(user_names, experiment_names)
            user = [ user for user in users if user.id == user_id ][0] if user_id is not None else None
            experiment = [ experiment for experiment in experiments if experiment.id == experiment_id ][0] if experiment_id is not None else None
            experiment_unique_id = "%s@%s" % (experiment.name, experiment.category.name)
            user_permission_permanent_id = "%s::%s" % (user.login, experiment_unique_id)
            user_permission = self.db.grant_on_experiment_to_user(
                    user,
                    permissions.EXPERIMENT_ALLOWED,
                    user_permission_permanent_id,
                    datetime.datetime.utcnow(),
                    "Permission on %s to use %s" % (user.login, experiment_unique_id),
                    experiment,
                    time_allowed,
                    priority,
                    initialization_in_accounting
            )
            if user_permission is not None:
                self.ui.notify("UserPermission created:\n%r" % user_permission)
                for parameter in user_permission.parameters:
                    self.ui.notify("UserPermissionParameter created:\n%r" % parameter)
            else:
                self.ui.error("The UserPermission '%s' already exists." % user_permission_permanent_id)
            self.ui.wait()
        except GoBackError:
            return

    def grant_on_admin_panel_to_group(self):
        groups = self.db.get_groups()
        group_names = [ (group.id, group.name) for group in groups ]
        try:
            group_id = self.ui.dialog_grant_on_admin_panel_to_group(group_names)
            group = [ group for group in groups if group.id == group_id ][0] if group_id is not None else None
            group_permission_permanent_id = "%s::admin_panel_access" % group.name
            group_permission = self.db.grant_on_admin_panel_to_group( group, permissions.ADMIN_PANEL_ACCESS,
                    group_permission_permanent_id, datetime.datetime.utcnow(),
                    "Permission on %s to use %s" % (group.name, group_permission_permanent_id))
            if group_permission is not None:
                self.ui.notify("GroupPermission created:\n%r" % group_permission)
                for parameter in group_permission.parameters:
                    self.ui.notify("GroupPermissionParameter created:\n%r" % parameter)
            else:
                self.ui.error("The GroupPermission '%s' already exists." % group_permission_permanent_id)
            self.ui.wait()
        except GoBackError:
            return

    def grant_on_admin_panel_to_user(self):
        users = self.db.get_users()
        user_names = [ (user.id, user.login) for user in users ]
        try:
            user_id = self.ui.dialog_grant_on_admin_panel_to_user(user_names)
            user = [ user for user in users if user.id == user_id ][0] if user_id is not None else None
            user_permission_permanent_id = "%s::admin_panel_access" % user.login
            user_permission = self.db.grant_on_admin_panel_to_user( user, permissions.ADMIN_PANEL_ACCESS,
                    user_permission_permanent_id, datetime.datetime.utcnow(),
                    "Permission on %s to use %s" % (user.login, user_permission_permanent_id))
            if user_permission is not None:
                self.ui.notify("UserPermission created:\n%r" % user_permission)
                for parameter in user_permission.parameters:
                    self.ui.notify("UserPermissionParameter created:\n%r" % parameter)
            else:
                self.ui.error("The UserPermission '%s' already exists." % user_permission_permanent_id)
            self.ui.wait()
        except GoBackError:
            return

    def grant_on_access_forward_to_group(self):
        groups = self.db.get_groups()
        group_names = [ (group.id, group.name) for group in groups ]
        try:
            group_id = self.ui.dialog_grant_on_access_forward_to_group(group_names)
            group = [ group for group in groups if group.id == group_id ][0] if group_id is not None else None
            group_permission_permanent_id = "%s::access_forward" % group.name
            group_permission = self.db.grant_on_access_forward_to_group( group, permissions.ACCESS_FORWARD,
                    group_permission_permanent_id, datetime.datetime.utcnow(),
                    "Permission on %s to use %s" % (group.name, group_permission_permanent_id))
            if group_permission is not None:
                self.ui.notify("GroupPermission created:\n%r" % group_permission)
                for parameter in group_permission.parameters:
                    self.ui.notify("GroupPermissionParameter created:\n%r" % parameter)
            else:
                self.ui.error("The GroupPermission '%s' already exists." % group_permission_permanent_id)
            self.ui.wait()
        except GoBackError:
            return

    def grant_on_access_forward_to_user(self):
        users = self.db.get_users()
        user_names = [ (user.id, user.login) for user in users ]
        try:
            user_id = self.ui.dialog_grant_on_access_forward_to_user(user_names)
            user = [ user for user in users if user.id == user_id ][0] if user_id is not None else None
            user_permission_permanent_id = "%s::access_forward" % user.login
            user_permission = self.db.grant_on_access_forward_to_user( user, permissions.ACCESS_FORWARD,
                    user_permission_permanent_id, datetime.datetime.utcnow(),
                    "Permission on %s to use %s" % (user.login, user_permission_permanent_id))
            if user_permission is not None:
                self.ui.notify("UserPermission created:\n%r" % user_permission)
                for parameter in user_permission.parameters:
                    self.ui.notify("UserPermissionParameter created:\n%r" % parameter)
            else:
                self.ui.error("The UserPermission '%s' already exists." % user_permission_permanent_id)
            self.ui.wait()
        except GoBackError:
            return

    def list_users(self):
        groups = self.db.get_groups()
        group_names = [ (group.id, group.name) for group in groups ]
        try:
            group_id = self.ui.dialog_list_users_get_group(group_names)
            users = [ group.users for group in groups if group.id == group_id ][0] if group_id is not None else self.db.get_users()
            self.ui.dialog_list_users_show_users(users)
            self.ui.wait()
        except GoBackError:
            return

    def notify_users(self):
        groups = self.db.get_groups()
        group_names = [ (group.id, group.name) for group in groups ]
        try:
            fromm, group_id, bcc, subject, text = self.ui.dialog_notify_users(
                                                            group_names,
                                                            self.default_notification_from,
                                                            self.default_notification_bcc,
                                                            self.default_notification_subject,
                                                            self.default_notification_text_file
                                                     )
            users = [ group.users for group in groups if group.id == group_id ][0] if group_id is not None else self.db.get_users()
            if len(users) > 0:
                smtp = SmtpGateway(self.smtp_host, self.smtp_helo)
                for user in users:
                    self.ui.notify_begin("Sending email to %s..." % user.email)
                    smtp.send(fromm, (user.email,) + bcc, subject, text % {'FULL_NAME': user.full_name, 'LOGIN': user.login})
                    self.ui.notify_end("done.")
            else:
                self.ui.error("The selected Group has no Users to notify.")
            self.ui.wait()
        except GoBackError:
            return

    def notify_users_with_passwords(self):
        """
        Will send a mail to every specified user with their welcome text. That welcome text
        will include the password. Because passwords are not stored in the database (only
        their hashes are), a "dbusers" file will need to be specified to extract the passwords
        from.
        """
        groups = self.db.get_groups()
        group_names = [ (group.id, group.name) for group in groups ]
        try:
            fromm, group_id, bcc, subject, text = self.ui.dialog_notify_users_with_passwords(
                                                            group_names,
                                                            self.default_notification_from,
                                                            self.default_notification_bcc,
                                                            self.default_notification_subject,
                                                            self.default_notification_with_password_text_file
                                                     )
            users = [ group.users for group in groups if group.id == group_id ][0] if group_id is not None else self.db.get_users()

            # The DB does not contain the passwords, so we will retrieve them from the DBUSERS file.
            users_from_file = self.ui.dialog_read_db_users_file_for_notify(self.default_db_users_file)

            # Store the passwords in a dictionary, associating them with the login names.
            user_pwds = {}
            for entry in users_from_file:
                user_pwds[entry[0]] = entry[3]

            if len(users) > 0 and len(users_from_file) > 0:

                smtp = SmtpGateway(self.smtp_host, self.smtp_helo)
                for user in users:
                    if( user.login in user_pwds ):
                        pwd = user_pwds[user.login]
                        self.ui.notify_begin("Sending email to %s..." % user.email)
                        smtp.send(fromm, (user.email,) + bcc, subject, (text.decode('utf-8') % {'FULL_NAME': user.full_name, 'LOGIN': user.login, 'PASSWORD': pwd}).encode('utf-8'))
                        self.ui.notify_end("done.")
                    else:
                        self.ui.notify("[Warning]: Did not notify %s. The password is not available in the specified users file" % user.login)
            else:
                self.ui.error("The selected Group has no Users to notify, or the users file specified is empty.")
            self.ui.wait()
        except GoBackError:
            return

    def _password2sha(self, password):
        randomstuff = ""
        for _ in range(4):
            c = chr(ord('a') + random.randint(0,25))
            randomstuff += c
        password = password if password is not None else ''
        return randomstuff + "{sha}" + sha.new(randomstuff + password).hexdigest()
