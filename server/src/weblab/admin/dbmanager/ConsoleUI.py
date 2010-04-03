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
import os
import getpass

from Exceptions import GoBackException, InvalidNullableAndDefaultValuesException

GO_BACK_KEYWORD = "[back]"

class ConsoleUI(object):

    def __init__(self):
        super(ConsoleUI, self).__init__()
        
    """
    These reading functions consider the following pre-conditions:
        * Keeping the input value blank means to accept the default value.
        * If there's no default value and the field is nullable, the default value will be None.
        * It's now allowed to give a default value when the field is nullable. A programming exception will be raised. 
    """        
        
    def _format_label(self, label, nullable=False, default=None):
        if nullable and default is not None:
            raise InvalidNullableAndDefaultValuesException("Programming error: it's not allowed to give a default value for a nullable field.")
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
    
    def _read_int(self, label, default):
        while True:
            try:
                input = raw_input(label)
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
                input = raw_input(label)
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
                input = getpass.getpass(label)
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

    def _read_field_int(self, label, min_value=-sys.maxint, max_value=sys.maxint-1, nullable=False, default=None):
        label = self._format_label(label, nullable, default)
        response = self._read_int(label, default)
        while ( not nullable and response is None ) or ( response is not None and not self._in_range(response, min_value, max_value) ):
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
            print
            for num, option in enumerate(options):
                print " %i. %s" % (num, option)
        else:
            print " [No options to choose]"
        response = self._read_field_int(label, 0, len(options)-1, nullable, default)
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
    
    def _read_field_users_file(self, label, nullable=False, default=None):
        response = self._read_field_file(label, nullable, default)
        if response is not None:
            user_logins = [ login for login in
                                    (''.join(char for char in line if not char.isspace()) for line in response) 
                                  if not login.startswith('#')
                          ]
            return user_logins
        else:
            return None
        
    #
    # Dialogs
    #
            
    def _clean(self, can_go_back=True):
        for i in xrange(50):
            print
        print "----------------------------------"
        print "- WebLab-Deusto Database Manager -"
        print "----------------------------------"
        if can_go_back:
            print "     type '%s' to go back" % GO_BACK_KEYWORD
        print
        
    def dialog_init(self, default_db_name, default_db_user, default_db_pass):
        self._clean(False)
        print "Connection"
        print 
        return self._read_field_str("Database name", default=default_db_name), \
               self._read_field_str("Database user", default=default_db_user), \
               self._read_field_password("Database password", default=default_db_pass)
        
                
    def dialog_menu(self):
        self._clean(False)
        print "Main Menu"
        print 
        print "1. Add Group"
        print "2. Add Experiment Category"
        print "3. Add Experiment"
        print "4. Add User with DB AuthType"
        print "5. Add Users with LDAP AuthType"
        print "6. Grant on Experiment to Group"
        print "7. Grant on Experiment to User"
        print "8. List Users"
        print "9. Notify Users"
        print
        print "0. Exit"
        print
        while True:
            try:
                option = self._read_field_int("Option", 0, 9)
                break
            except GoBackException:
                pass
        return option

    def dialog_add_group(self, groups):
        self._clean()
        print "Add Group"
        print
        return self._read_field_str("Name"), \
               self._read_field_choose("Parent Group", groups, True)

    def dialog_add_experiment_category(self):
        self._clean()
        print "Add Experiment Category"
        print 
        return self._read_field_str("Name")
        
    def dialog_add_experiment(self, categories):
        self._clean()
        print "Add Experiment"
        print 
        return self._read_field_str("Name"), \
               self._read_field_choose("Category", categories)
               
    def dialog_add_user_with_db_authtype(self, roles, auths):
        self._clean()
        print "Add User with DB AuthType"
        print 
        return self._read_field_str("Login"), \
               self._read_field_str("Full name"), \
               self._read_field_email("Email"), \
               self._read_field_str("Avatar", True), \
               self._read_field_choose("Role", roles, True), \
               self._read_field_choose("Auth", auths), \
               self._read_field_verified_password("Password", True)
               
    def dialog_authenticate_on_ldap(self):
        self._clean()
        print "LDAP Authentication"
        print 
        return self._read_field_str("Username"), \
               self._read_field_password("Password"), \
               self._read_field_str("Domain")               
               
    def dialog_add_users_with_ldap_authtype(self, roles, auths, default_users_file):
        self._clean()
        print "Add Users with LDAP AuthType"
        print 
        user_logins = self._read_field_users_file("Users file", default=default_users_file)
        for user_login in user_logins:
            print " %s" % user_login
        return user_logins, \
               self._read_field_choose("Role", roles, True), \
               self._read_field_choose("Auth", auths)               
               
    def dialog_grant_on_experiment_to_group(self, groups, experiments):
        self._clean()
        print "Grant on Experiment to Group"
        print 
        return self._read_field_choose("Group", groups), \
               self._read_field_choose("Experiment", experiments), \
               self._read_field_int("Time allowed")               
               
    def dialog_grant_on_experiment_to_user(self, users, experiments):
        self._clean()
        print "Grant on Experiment to User"
        print 
        return self._read_field_choose("User", users), \
               self._read_field_choose("Experiment", experiments), \
               self._read_field_int("Time allowed")         
               
    def dialog_list_users_get_group(self, groups):
        self._clean()
        print "List Users"
        print 
        return self._read_field_choose("Group", groups, True)
  
    def dialog_notify_users(self, groups, default_from, default_bcc, default_subject, default_text_file):
        self._clean()
        print "Notify Users"
        print
        return self._read_field_email("From", default=default_from), \
               self._read_field_choose("To", groups), \
               self._read_field_emails("BCC", default=default_bcc), \
               self._read_field_str("Subject", default=default_subject), \
               self._read_field_textarea("Text file", default=default_text_file)

    def dialog_list_users_show_users(self, users):
        self._clean()
        print "List Users"
        print
        if len(users) > 0: 
            for user in users:
                print user
        else:
            print "[No Users in the database]"
               
    def dialog_exit(self):
        self._clean(False)
        print "Good bye."
        print 
        
    def ask(self, question):
        print
        response = ""
        while response.lower() not in ("y", "n"):
            response = raw_input("%s (y/n): " % question)
        return response == "y"  
    
    def notify(self, message):
        print
        print message
    
    def notify_begin(self, message):
        print
        print message,

    def notify_end(self, message):
        print message
        
    def error(self, message):
        print
        print "Error: " + message
        
    def wait(self):
        print
        print "Press any key to continue...",
        sys.stdin.read(1)
