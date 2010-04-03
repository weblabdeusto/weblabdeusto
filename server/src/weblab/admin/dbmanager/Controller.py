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

import sys
import datetime

from ConsoleUI import ConsoleUI
from Exceptions import GoBackException

from DbGateway import DbGateway
from SmtpGateway import SmtpGateway
try:
    from LdapGateway import LdapGateway
except ImportError:
    LdapGateway = None

try:
    from configuration import DB_HOST, SMTP_HOST, SMTP_HELO
    from configuration import DEFAULT_DB_NAME, DEFAULT_DB_USER, DEFAULT_DB_PASS
    from configuration import DEFAULT_LDAP_USERS_FILE
    from configuration import DEFAULT_NOTIFICATION_FROM, DEFAULT_NOTIFICATION_BCC, DEFAULT_NOTIFICATION_SUBJECT, DEFAULT_NOTIFICATION_TEXT_FILE
except Exception, e:
    print "File configuration.py not found. See configuration.py.dist. Error:", str(e)
    sys.exit(1)


class Controller(object):

    def __init__(self):
        super(Controller, self).__init__()
        self.ui = ConsoleUI()
        self.init()
        self.menu()
        
    def init(self):
        db_name, db_user, db_pass = self.ui.dialog_init(DEFAULT_DB_NAME, DEFAULT_DB_USER, DEFAULT_DB_PASS)
        self.db = DbGateway(DB_HOST, db_name, db_user, db_pass)
        
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
                self.add_user_with_db_authtype()
            elif option == 5:
                self.add_users_with_ldap_authtype()
            elif option == 6:
                self.grant_on_experiment_to_group()
            elif option == 7:
                self.grant_on_experiment_to_user()
            elif option == 8:
                self.list_users()
            elif option == 9:
                self.notify_users()
        self.ui.dialog_exit()
        sys.exit(0)

    def add_group(self):
        groups = self.db.get_groups()
        group_names = [ group.name for group in groups ]
        try:
            group_name, parent_group_index = self.ui.dialog_add_group(group_names)
            parent_group = groups[parent_group_index] if parent_group_index is not None else None             
            group = self.db.insert_group(group_name, parent_group)
            if group is not None:
                self.ui.notify("Group created:\n%r" % group)
            else:
                self.ui.error("The Group '%s' already exists." % group_name)     
            self.ui.wait()
        except GoBackException:
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
        except GoBackException:
            return
                    
    def add_experiment(self):
        categories = self.db.get_experiment_categories()
        category_names = [ category.name for category in categories ]
        try:
            experiment_name, category_index = self.ui.dialog_add_experiment(category_names)
            category = categories[category_index]
            start_date = datetime.datetime.utcnow()
            end_date = start_date.replace(year=start_date.year+10)
            experiment = self.db.insert_experiment(experiment_name, category, start_date, end_date)
            if experiment is not None:
                self.ui.notify("Experiment created:\n%r" % experiment)
            else:
                self.ui.error("The Experiment '%s' already exists." % experiment_name)     
            self.ui.wait()
        except GoBackException:
            return
        
    def add_user_with_db_authtype(self):
        roles = self.db.get_roles()
        role_names = [ role.name for role in roles ]
        auths = self.db.get_auths("DB")
        auth_names = [ auth.name for auth in auths ]
        try:
            login, full_name, email, avatar, role_index, auth_index, user_auth_config = self.ui.dialog_add_user_with_db_authtype(role_names, auth_names)
            role = roles[role_index] if role_index is not None else None
            auth = auths[auth_index]
            user = self.db.insert_user(login, full_name, email, avatar, role)
            if user is not None:
                self.ui.notify("User created:\n%r" % user)
                user_auth = self.db.insert_user_auth(user, auth, user_auth_config)
                assert user_auth is not None
                self.ui.notify("UserAuth created:\n%r" % user_auth)
            else:
                self.ui.error("The User '%s' already exists." % login)     
            self.ui.wait()
        except GoBackException:
            return
        
    def add_users_with_ldap_authtype(self):
        if LdapGateway is None:
            self.ui.error("LDAP is not available. Is python-ldap installed?")
            self.ui.wait()
            return
        roles = self.db.get_roles()
        role_names = [ role.name for role in roles ]
        auths = self.db.get_auths("LDAP")
        auth_names = [ auth.name for auth in auths ]
        try:
            user_logins, role_index, auth_index = self.ui.dialog_add_users_with_ldap_authtype(
                                                            role_names,
                                                            auth_names,
                                                            DEFAULT_LDAP_USERS_FILE
                                                  )
            role = roles[role_index] if role_index is not None else None
            auth = auths[auth_index]
            auth_username, auth_password, auth_domain = self.ui.dialog_authenticate_on_ldap()
            ldap = LdapGateway(auth.get_config_value("ldap_uri"),
                               auth_domain,
                               auth.get_config_value("base"),
                               auth_username, auth_password)
            for user_data in ldap.get_users(user_logins):
                user = self.db.insert_user(user_data["login"], user_data["full_name"], user_data["email"], None, role)
                if user is not None:
                    self.ui.notify("User created:\n%r" % user)
                    user_auth = self.db.insert_user_auth(user, auth, None)
                    assert user_auth is not None
                    self.ui.notify("UserAuth created:\n%r" % user_auth)
                else:
                    self.ui.error("The User '%s' already exists." % user_data["login"])     
            self.ui.wait()
        except GoBackException:
            return
        
    def grant_on_experiment_to_group(self):
        groups = self.db.get_groups()
        group_names = [ group.name for group in groups ]
        experiments = self.db.get_experiments()
        experiment_names = [ experiment.name for experiment in experiments ]
        permission_type = self.db.get_permission_type("experiment_allowed")
        try:
            group_index, experiment_index, time_allowed = self.ui.dialog_grant_on_experiment_to_group(group_names, experiment_names)
            group = groups[group_index] if group_index is not None else None
            experiment = experiments[experiment_index] if experiment_index is not None else None
            experiment_unique_id = "%s@%s" % (experiment.name, experiment.category.name)
            group_permission_permanent_id = "%s::%s" % (group.name, experiment_unique_id) 
            group_permission = self.db.grant_on_experiment_to_group(
                    group,
                    permission_type,
                    group_permission_permanent_id,
                    datetime.datetime.utcnow(),
                    "Permission on %s to use %s" % (group.name, experiment_unique_id),
                    experiment,
                    time_allowed
            )
            if group_permission is not None:
                self.ui.notify("GroupPermission created:\n%r" % group_permission)
                for parameter in group_permission.parameters:
                    self.ui.notify("GroupPermissionParameter created:\n%r" % parameter)
            else:
                self.ui.error("The GroupPermission '%s' already exists." % group_permission_permanent_id)     
            self.ui.wait()
        except GoBackException:
            return
        
    def grant_on_experiment_to_user(self):
        users = self.db.get_users()
        user_names = [ user.login for user in users ]
        experiments = self.db.get_experiments()
        experiment_names = [ experiment.name for experiment in experiments ]
        permission_type = self.db.get_permission_type("experiment_allowed")
        try:
            user_index, experiment_index, time_allowed = self.ui.dialog_grant_on_experiment_to_user(user_names, experiment_names)
            user = users[user_index] if user_index is not None else None
            experiment = experiments[experiment_index] if experiment_index is not None else None
            experiment_unique_id = "%s@%s" % (experiment.name, experiment.category.name)
            user_permission_permanent_id = "%s::%s" % (user.login, experiment_unique_id) 
            user_permission = self.db.grant_on_experiment_to_user(
                    user,
                    permission_type,
                    user_permission_permanent_id,
                    datetime.datetime.utcnow(),
                    "Permission on %s to use %s" % (user.login, experiment_unique_id),
                    experiment,
                    time_allowed
            )
            if user_permission is not None:
                self.ui.notify("UserPermission created:\n%r" % user_permission)
                for parameter in user_permission.parameters:
                    self.ui.notify("UserPermissionParameter created:\n%r" % parameter)
            else:
                self.ui.error("The UserPermission '%s' already exists." % user_permission_permanent_id)     
            self.ui.wait()
        except GoBackException:
            return   
        
    def list_users(self):
        groups = self.db.get_groups()
        group_names = [ group.name for group in groups ]
        try:
            group_index = self.ui.dialog_list_users_get_group(group_names)
            if group_index is not None:
                users = groups[group_index].users
            else:
                users = self.db.get_users()
            self.ui.dialog_list_users_show_users(users)
            self.ui.wait()
        except GoBackException:
            return
        
    def notify_users(self):
        groups = self.db.get_groups()
        group_names = [ group.name for group in groups ]
        try:
            fromm, group_index, bcc, subject, text = self.ui.dialog_notify_users(
                                                            group_names,
                                                            DEFAULT_NOTIFICATION_FROM,
                                                            DEFAULT_NOTIFICATION_BCC,
                                                            DEFAULT_NOTIFICATION_SUBJECT,
                                                            DEFAULT_NOTIFICATION_TEXT_FILE
                                                     )
            if group_index is not None:
                users = groups[group_index].users
            else:
                users = self.db.get_users()
            if len(users) > 0:
                smtp = SmtpGateway(SMTP_HOST, SMTP_HELO)
                for user in users:
                    self.ui.notify_begin("Sending email to %s..." % user.email)
                    smtp.send(fromm, (user.email,) + bcc, subject, text % {'FULL_NAME': user.full_name, 'LOGIN': user.login})
                    self.ui.notify_end("done.")
            else:
                self.ui.error("The selected Group has no Users to notify.")
            self.ui.wait()
        except GoBackException:
            return