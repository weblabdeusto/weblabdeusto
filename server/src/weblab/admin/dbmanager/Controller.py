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
#         Luis Rodriguez <luis.rodriguez@opendeusto.es>

import sys
import datetime
import random
import sha

from ConsoleUI import ConsoleUI
from Exceptions import GoBackException

from DbGateway import DbGateway
from SmtpGateway import SmtpGateway
try:
    from LdapGateway import LdapGateway
    LdapGatewayClass = LdapGateway
except ImportError:
    LdapGatewayClass = None

try:
    from configuration import DB_HOST, SMTP_HOST, SMTP_HELO
    from configuration import DEFAULT_DB_NAME, DEFAULT_DB_USER, DEFAULT_DB_PASS
    from configuration import DEFAULT_LDAP_USERS_FILE
    from configuration import DEFAULT_OPENID_USERS_FILE
    from configuration import DEFAULT_DB_USERS_FILE
    from configuration import DEFAULT_NOTIFICATION_FROM, DEFAULT_NOTIFICATION_BCC, DEFAULT_NOTIFICATION_SUBJECT, DEFAULT_NOTIFICATION_TEXT_FILE
    from configuration import DEFAULT_NOTIFICATION_WITH_PASSWORD_TEXT_FILE
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
                self.add_users_to_group()
            elif option == 5:
                self.add_user_with_db_authtype()
            elif option == 6:
                self.add_users_with_ldap_authtype()
            elif option == 7:
                self.add_users_with_openid_authtype()
            elif option == 8:
                self.grant_on_experiment_to_group()
            elif option == 9:
                self.grant_on_experiment_to_user()
            elif option == 10:
                self.list_users()
            elif option == 11:
                self.notify_users()
            elif option == 12: 
                self.add_users_batch_with_db_authtype() # TODO: Move this option to where it belongs.
            elif option == 13:
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
        category_names = [ (category.id, category.name) for category in categories ]
        try:
            experiment_name, category_id = self.ui.dialog_add_experiment(category_names)
            category = [ category for category in categories if category.id == category_id ][0]
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
        
    def add_users_to_group(self):
        groups = self.db.get_groups()
        group_names = [ (group.id, group.name) for group in groups ]
        try:
            group_id, user_logins = self.ui.dialog_add_users_to_group(group_names, DEFAULT_LDAP_USERS_FILE)
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
        except GoBackException:
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
        except GoBackException:
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
                                                            DEFAULT_DB_USERS_FILE
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
            
        except GoBackException:
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
                                                            DEFAULT_LDAP_USERS_FILE
                                                  )
            role = [ role for role in roles if role.id == role_id ][0] if role_id is not None else None
            auth = [ auth for auth in auths if auth.id == auth_id ][0]
            auth_username, auth_password, auth_domain = self.ui.dialog_authenticate_on_ldap()
            ldap = LdapGatewayClass(auth.get_config_value("ldap_uri"),
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
                                                            DEFAULT_OPENID_USERS_FILE
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
            
        except GoBackException:
            return

    def grant_on_experiment_to_group(self):
        groups = self.db.get_groups()
        group_names = [ (group.id, group.name) for group in groups ]
        experiments = self.db.get_experiments()
        experiment_names = [ (experiment.id, experiment.name) for experiment in experiments ]
        permission_type = self.db.get_permission_type("experiment_allowed")
        try:
            group_id, experiment_id, time_allowed = self.ui.dialog_grant_on_experiment_to_group(group_names, experiment_names)
            group = [ group for group in groups if group.id == group_id ][0] if group_id is not None else None
            experiment = [ experiment for experiment in experiments if experiment.id == experiment_id ][0] if experiment_id is not None else None
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
        user_names = [ (user.id, user.login) for user in users ]
        experiments = self.db.get_experiments()
        experiment_names = [ (experiment.id, experiment.name) for experiment in experiments ]
        permission_type = self.db.get_permission_type("experiment_allowed")
        try:
            user_id, experiment_id, time_allowed = self.ui.dialog_grant_on_experiment_to_user(user_names, experiment_names)
            user = [ user for user in users if user.id == user_id ][0] if user_id is not None else None
            experiment = [ experiment for experiment in experiments if experiment.id == experiment_id ][0] if experiment_id is not None else None
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
        group_names = [ (group.id, group.name) for group in groups ]
        try:
            group_id = self.ui.dialog_list_users_get_group(group_names)
            users = [ group.users for group in groups if group.id == group_id ][0] if group_id is not None else self.db.get_users()
            self.ui.dialog_list_users_show_users(users)
            self.ui.wait()
        except GoBackException:
            return
        
    def notify_users(self):
        groups = self.db.get_groups()
        group_names = [ (group.id, group.name) for group in groups ]
        try:
            fromm, group_id, bcc, subject, text = self.ui.dialog_notify_users(
                                                            group_names,
                                                            DEFAULT_NOTIFICATION_FROM,
                                                            DEFAULT_NOTIFICATION_BCC,
                                                            DEFAULT_NOTIFICATION_SUBJECT,
                                                            DEFAULT_NOTIFICATION_TEXT_FILE
                                                     )
            users = [ group.users for group in groups if group.id == group_id ][0] if group_id is not None else self.db.get_users()
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
        
    def notify_users_with_passwords(self):
        groups = self.db.get_groups()
        group_names = [ (group.id, group.name) for group in groups ]
        try:
            fromm, group_id, bcc, subject, text = self.ui.dialog_notify_users(
                                                            group_names,
                                                            DEFAULT_NOTIFICATION_FROM,
                                                            DEFAULT_NOTIFICATION_BCC,
                                                            DEFAULT_NOTIFICATION_SUBJECT,
                                                            DEFAULT_NOTIFICATION_WITH_PASSWORD_TEXT_FILE
                                                     )
            users = [ group.users for group in groups if group.id == group_id ][0] if group_id is not None else self.db.get_users()
            
            # The DB does not contain the passwords, so we will retrieve them from the DBUSERS file. 
            users_from_file = self.ui.dialog_read_db_users_file_for_notify(DEFAULT_DB_USERS_FILE)
            
            # Store the passwords in a dictionary, associating them with the login names. 
            user_pwds = {}
            for entry in users_from_file:
                user_pwds[entry[0]] = entry[3]
                            
            if len(users) > 0 and len(users_from_file) > 0:
                
                smtp = SmtpGateway(SMTP_HOST, SMTP_HELO)
                for user in users:
                    if( user.login in user_pwds ):
                        pwd = user_pwds[user.login]
                        self.ui.notify_begin("Sending email to %s..." % user.email)
                        smtp.send(fromm, (user.email,) + bcc, subject, text % {'FULL_NAME': user.full_name, 'LOGIN': user.login, 'PASSWORD': pwd})
                        self.ui.notify_end("done.")
                    else:
                        self.ui.notify("[Warning]: Did not notify %s. The password is not available in the specified users file", user.login)
            else:
                self.ui.error("The selected Group has no Users to notify, or the users file specified is empty.")
            self.ui.wait()
        except GoBackException:
            return
        
    def _password2sha(self, password):
        randomstuff = ""
        for _ in range(4):
            c = chr(ord('a') + random.randint(0,25))
            randomstuff += c
        password = password if password is not None else ''
        return randomstuff + "{sha}" + sha.new(randomstuff + password).hexdigest()