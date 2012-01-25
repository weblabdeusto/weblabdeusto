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
import os
import getpass

from exc import GoBackException

GO_BACK_KEYWORD = "[back]"

class ConsoleUI(object):

    def __init__(self):
        super(ConsoleUI, self).__init__()

    def _raw_input(self, prompt):
        return raw_input(prompt)

    def _getpass(self, prompt):
        return getpass.getpass(prompt)

    def _print(self, text=""):
        print text

    """
    These reading functions consider the following pre-conditions:
        * Keeping the input value blank means to accept the default value.
        * If there's no default value and the field is nullable, the default value will be None.
        * It's now allowed to give a default value when the field is nullable. A programming exception will be raised. 
    """        

    def _format_label(self, label, nullable=False, default=None):
        assert not ( nullable and default is not None )
        if default is not None:
            label += " [default: %s]" % default
        else:
            if nullable:
                label += " [default: <null>]"
        label += ": "
        return label

    def _in_range(self, value, min_value, max_value):
        return value >= min_value and value <= max_value

    def _valid_list_of_emails(self, emails):
        return reduce(lambda x,y: x and y, map(lambda x: "@" in x and "." in x, emails))

    def _csv_to_tuple(self, csv):
        return tuple(( v.strip() for v in csv.split(",") )) if csv is not None else ()

    #
    # 1st layer: Input-level (responsible for the 'default' parameter)
    #
    def _read_bool(self, label, default):
        while True:
            try:
                input = self._raw_input(label)
                if input == GO_BACK_KEYWORD:
                    raise GoBackException()
                if len(input) == 0:
                    input = default
                if input.lower() not in ('y','yes','n','no'):
                    continue
                result = input.lower() in ('y','yes')
                break
            except ValueError:
                pass 
        return result           

    def _read_int(self, label, default):
        while True:
            try:
                input = self._raw_input(label)
                if input == GO_BACK_KEYWORD:
                    raise GoBackException()
                if len(input) == 0:
                    input = default
                result = int(input) if input is not None else None
                break
            except ValueError:
                pass 
        return result           

    def _read_str(self, label, default):
        while True:
            try:
                input = self._raw_input(label)
                if input == GO_BACK_KEYWORD:
                    raise GoBackException()
                if len(input) == 0:
                    input = default
                result = input
                break
            except ValueError:
                pass 
        return result    

    def _read_password(self, label, default):
        while True:
            try:
                input = self._getpass(label)
                if input == GO_BACK_KEYWORD:
                    raise GoBackException()
                if len(input) == 0:
                    input = default
                result = input
                break
            except ValueError:
                pass 
        return result   

    #
    # 2nd layer: Low-level Fields (responsible for the 'nullable' parameter)
    #

    def _read_field_bool(self, label, nullable=False, default=None):
        label = self._format_label(label, nullable, default)
        response = self._read_bool(label, default)
        while ( not nullable and response is None ):
            response = self._read_bool(label, default)
        return response

    def _read_field_int(self, label, min_value=-sys.maxint, max_value=sys.maxint-1, nullable=False, default=None):
        label = self._format_label(label, nullable, default)
        response = self._read_int(label, default)
        while ( not nullable and response is None ) or ( response is not None and not self._in_range(response, min_value, max_value) ):
            response = self._read_int(label, default)
        return response

    def _read_field_int_from_list(self, label, values, nullable=False, default=None):
        label = self._format_label(label, nullable, default)
        response = self._read_int(label, default)
        while ( not nullable and response is None ) or ( response is not None and response not in values ):
            response = self._read_int(label, default)
        return response

    def _read_field_str(self, label, nullable=False, default=None):
        label = self._format_label(label, nullable, default)
        response = self._read_str(label, default)
        while not nullable and response is None:
            response = self._read_str(label, default)
        return response

    def _read_field_choose(self, label, options, nullable=False, default=None):
        if len(options) > 0:
            self._print()
            for num, option in options:
                self._print(" %i. %s" % (num, option))
        else:
            assert nullable
            self._print(" [No options to choose]")
        response = self._read_field_int_from_list(label, map(lambda x: x[0], options), nullable, default)
        return response

    def _read_field_password(self, label, nullable=False, default=None):
        label = self._format_label(label, nullable, default)
        response = self._read_password(label, default)
        while not nullable and response is None:
            response = self._read_password(label, default)
        return response

    #
    # 3rd layer: High-level Fields
    #

    def _read_field_verified_password(self, label, nullable=False):
        response1 = self._read_field_password(label, nullable)
        response2 = self._read_field_password(label+" (verify)", nullable)    
        while response1 != response2:
            response1 = self._read_field_password(label, nullable)
            response2 = self._read_field_password(label+" (verify)", nullable)
        return response1

    def _read_field_file(self, label, nullable=False, default=None):
        response = self._read_field_str(label, nullable, default)
        while response is not None and not os.path.isfile(response):
            response = self._read_field_str(label, nullable, default)
        return open(response).readlines() if response is not None else None

    def _read_field_textarea(self, label, nullable=False, default=None):
        lines = self._read_field_file(label, nullable, default)
        return "".join(lines) if lines is not None else None

    def _read_field_email(self, label, nullable=False, default=None):
        response = self._read_field_str(label, nullable, default)
        while response is not None and "@" not in response and "." not in response:
            response = self._read_field_str(label, nullable, default)
        return response if response is not None else None    

    def _read_field_emails(self, label, nullable=False, default=None):
        response = self._read_field_str(label+" (separate by ,)", nullable, default)
        emails = self._csv_to_tuple(response)
        while response is not None and not self._valid_list_of_emails(emails):
            response = self._read_field_str(label+" (separate by ,)", nullable, default)
            emails = self._csv_to_tuple(response)
        return emails

    #
    # 4th layer: Application-level fields
    #    

    def _read_field_full_users_file(self, label, nullable=False, default=None):
        """
        Reads a users file which contains the full data for each user, in the following format:
         username, fullname, email, openid-template

        Returns a list containing, for each user, a list with its data.
        """
        response = self._read_field_file(label, nullable, default)
        lines = [ line for line in response if not line.startswith('#')]
        users = []
        for line in lines:
            user = line.split(',')
            user = [ elem.strip("\n\t ") for elem in user ]
            if len(user) == 4:
                users.append(user)
            else:
                self.notify("[Warning] Ignoring: %s" % str(user))
        return users

    #
    # 4th layer: Application-level fields
    #    

    def _read_field_full_users_db_file(self, label, nullable=False, default=None):
        """
        Reads a users file which contains the full data for each user, in the following format:
         username, fullname, email, password

        Returns a list containing, for each user, a list with its data.
        """
        response = self._read_field_file(label, nullable, default)
        lines = [ line for line in response if not line.startswith('#')]
        users = []
        for line in lines:
            user = line.split(',')
            user = [ elem.strip("\n\t ") for elem in user ]
            if len(user) == 4:
                users.append(user)
            else:
                self.notify("[Warning] Ignoring: %s" % str(user))
        return users


    def _read_field_users_file(self, label, nullable=False, default=None):
        """
        Reads a simple users file, returning the user names stored within
        """
        response = self._read_field_file(label, nullable, default)
        if response is not None:
            user_logins = [ login for login in
                                    (''.join(char for char in line if not char.isspace()) for line in response) 
                                  if not login.startswith('#') and not len(login) == 0
                          ]
            return user_logins
        else:
            return None

    #
    # Dialogs
    #

    def _clean(self, can_go_back=True):
        for _ in xrange(50):
            self._print()
        self._print("----------------------------------")
        self._print("- WebLab-Deusto Database Manager -")
        self._print("----------------------------------")
        if can_go_back:
            self._print("     type '%s' to go back" % GO_BACK_KEYWORD)
        self._print()

    def dialog_init(self, default_db_name, default_db_user, default_db_pass):
        self._clean(False)
        self._print("Connection")
        self._print()
        return self._read_field_str("Database name", default=default_db_name), \
               self._read_field_str("Database user", default=default_db_user), \
               self._read_field_password("Database password", default=default_db_pass)


    def dialog_menu(self):
        self._clean(False)
        self._print("Main Menu")
        self._print() 
        self._print(" 1. Add Group")
        self._print(" 2. Add Experiment Category")
        self._print(" 3. Add Experiment")
        self._print(" 4. Add Users to Group")
        self._print(" 5. Add User with DB AuthType")
        self._print(" 6. Add Users with LDAP AuthType")
        self._print(" 7. Add Users with OpenID AuthType")
        self._print(" 8. Add Users (batch) with DB AuthType")
        self._print(" 9. Grant on Experiment to Group")
        self._print(" 10. Grant on Experiment to User")
        self._print(" 11. Grant on Admin Panel to Group")
        self._print(" 12. Grant on Admin Panel to User")
        self._print(" 13. Grant on Access Forward to Group")
        self._print(" 14. Grant on Access Forward to User")
        self._print(" 15. List Users")
        self._print(" 16. Notify users")
        self._print(" 17. Notify users (With passwords)")
        self._print()
        self._print("0. Exit")
        self._print()
        while True:
            try:
                option = self._read_field_int("Option", 0, 17)
                break
            except GoBackException:
                pass
        return option

    def dialog_add_group(self, groups):
        self._clean()
        self._print("Add Group")
        self._print()
        return self._read_field_str("Name"), \
               self._read_field_choose("Parent Group", groups, True)

    def dialog_add_experiment_category(self):
        self._clean()
        self._print("Add Experiment Category")
        self._print()
        return self._read_field_str("Name")

    def dialog_add_experiment(self, categories):
        self._clean()
        self._print("Add Experiment")
        self._print()
        return self._read_field_str("Name"), \
               self._read_field_choose("Category", categories)        

    def dialog_add_users_to_group(self, groups, default_users_file):
        self._clean()
        self._print("Add Users to Group")
        self._print()
        user_logins = self._read_field_users_file("Users file", default=default_users_file)
        for user_login in user_logins:
            self._print(" %s" % user_login)
        return self._read_field_choose("Group", groups), \
               user_logins


    def dialog_add_user_with_db_authtype(self, roles, auths):
        self._clean()
        self._print("Add User with DB AuthType")
        self._print()
        return self._read_field_str("Login"), \
               self._read_field_str("Full name"), \
               self._read_field_email("Email"), \
               self._read_field_str("Avatar", True), \
               self._read_field_choose("Role", roles, True), \
               self._read_field_choose("Auth", auths), \
               self._read_field_verified_password("Password", True)

    def dialog_authenticate_on_ldap(self):
        self._clean()
        self._print("LDAP Authentication")
        self._print()
        return self._read_field_str("Username"), \
               self._read_field_password("Password"), \
               self._read_field_str("Domain")               

    def dialog_add_users_with_ldap_authtype(self, roles, auths, default_users_file):
        self._clean()
        self._print("Add Users with LDAP AuthType")
        self._print()
        user_logins = self._read_field_users_file("Users file", default=default_users_file)
        for user_login in user_logins:
            self._print(" %s" % user_login)
        return user_logins, \
               self._read_field_choose("Role", roles, True), \
               self._read_field_choose("Auth", auths)             

    def dialog_add_users_with_openid_authtype(self, roles, auths, default_users_file):
        """
        Provides the console interface to add users through OpenID.
        Returns a tuple: (user_data, role)
        user_data contains a list with the data of every user in the list.
        role contains the role that will be applied to every new user within that list.
        """
        self._clean()
        self._print("Add Users with OpenID AuthType")
        self._print()

        # Retrieve a list of lists with the data container in the specified users file.
        user_logins = self._read_field_full_users_file("Users file", default=default_users_file)

        # Display each user's data.
        for user_login in user_logins:
            self._print(" %s" % str(user_login))

        # Let the user choose a role to apply to every user 
        role = self._read_field_choose("Role", roles, True)
        return user_logins, role

    def dialog_add_users_batch_with_db_authtype(self, roles, auths, default_users_file):
        """
        Provides the console interface to add a list of users to the DB.
        Returns a tuple: (user_data, role)
        user_data contains a list with the data of every user in the list.
        role contains the role that will be applied to every new user within that list.
        """
        self._clean()
        self._print("Add Users (batch) with DB AuthType")
        self._print()

        # Retrieve a list of lists with the data container in the specified users file.
        user_logins = self._read_field_full_users_db_file("Users file", default=default_users_file)

        # Display each user's data.
        for user_login in user_logins:
            self._print(" %s" % str(user_login))

        # Let the user choose a role to apply to every user 
        role = self._read_field_choose("Role", roles, True)
        return user_logins, role

    def dialog_read_db_users_file_for_notify(self, default_users_file):
        """
        Provides the console interface to read the list of users with the password
        information, to be used for mail notifications.
        Returns a list of tuples with the users' data.
        """
        self._clean()
        self._print("Read user information file")
        self._print()

        # Retrieve a list of lists with the data container in the specified users file.
        user_logins = self._read_field_full_users_db_file("Users file", default=default_users_file)

        # Display each user's data.
        for user_login in user_logins:
            self._print(" %s" % str(user_login))

        return user_logins


    def dialog_grant_on_experiment_to_group(self, groups, experiments):
        self._clean()
        self._print("Grant on Experiment to Group")
        self._print()
        return self._read_field_choose("Group", groups), \
               self._read_field_choose("Experiment", experiments), \
               self._read_field_int("Time allowed"), \
               self._read_field_int("Priority (0-10, lower is more priority)", min_value = 0, max_value=10, default=5), \
               self._read_field_choose("For the time allowed, you are counting with initialization?", [ (1,'yes'),(2,'no')]) == 1

    def dialog_grant_on_experiment_to_user(self, users, experiments):
        self._clean()
        self._print("Grant on Experiment to User")
        self._print()
        return self._read_field_choose("User", users), \
               self._read_field_choose("Experiment", experiments), \
               self._read_field_int("Time allowed"), \
               self._read_field_int("Priority (0-10, lower is more priority)", min_value = 0, max_value=10, default=5), \
               self._read_field_choose("For the time allowed, you are counting with initialization?", [ (1,'yes'),(2,'no')]) == 1

    def dialog_grant_on_admin_panel_to_group(self, groups):
        self._clean()
        self._print("Grant on Admin Panel to Group")
        self._print()
        return self._read_field_choose("Group", groups)

    def dialog_grant_on_admin_panel_to_user(self, users):
        self._clean()
        self._print("Grant on Admin Panel to User")
        self._print()
        return self._read_field_choose("User", users)

    def dialog_grant_on_access_forward_to_group(self, groups):
        self._clean()
        self._print("Grant on Access Forward to Group")
        self._print()
        return self._read_field_choose("Group", groups)

    def dialog_grant_on_access_forward_to_user(self, users):
        self._clean()
        self._print("Grant on Access Forward to User")
        self._print()
        return self._read_field_choose("User", users)

    def dialog_list_users_get_group(self, groups):
        self._clean()
        self._print("List Users")
        self._print()
        return self._read_field_choose("Group", groups, True)

    def dialog_notify_users(self, groups, default_from, default_bcc, default_subject, default_text_file):
        self._clean()
        self._print("Notify Users")
        self._print()
        return self._read_field_email("From", default=default_from), \
               self._read_field_choose("To", groups), \
               self._read_field_emails("BCC", default=default_bcc), \
               self._read_field_str("Subject", default=default_subject), \
               self._read_field_textarea("Text file", default=default_text_file)

    def dialog_notify_users_with_passwords(self, groups, default_from, default_bcc, default_subject, default_text_file):
        self._clean()
        self._print("Notify Users (With passwords)")
        self._print()
        return self._read_field_email("From", default=default_from), \
               self._read_field_choose("To", groups), \
               self._read_field_emails("BCC", default=default_bcc), \
               self._read_field_str("Subject", default=default_subject), \
               self._read_field_textarea("Text file", default=default_text_file)

    def dialog_list_users_show_users(self, users):
        self._clean()
        self._print("List Users")
        self._print()
        if len(users) > 0: 
            for user in users:
                self._print(user)
        else:
            self._print("[No Users in the database]")

    def dialog_exit(self):
        self._clean(False)
        self._print("Good bye.")
        self._print()

    def ask(self, question):
        self._print()
        response = ""
        while response.lower() not in ("y", "n"):
            response = self._raw_input("%s (y/n): " % question)
        return response == "y"  

    def notify(self, message):
        self._print()
        self._print(message)

    def notify_begin(self, message):
        self._print()
        self._print(message,)

    def notify_end(self, message):
        self._print(message)

    def error(self, message):
        self._print()
        self._print("Error: " + message)

    def wait(self):
        self._print()
        self._print("Press any key to continue...",)
        sys.stdin.read(1)
