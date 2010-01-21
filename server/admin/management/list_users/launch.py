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
# Author: Pablo Orduña <pablo@ordunya.com>
# 

import sys

from optparse import OptionParser

import MySQLdb as dbi

try:
    import configuration
except Exception, e:
    print "File configuration.py not found. See configuration.py.dist. Error:", str(e)
    sys.exit(1)


class ListManager(object):
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def connect(self):
        self.connection = dbi.connect( 
            host   = configuration.HOSTNAME,
            db     = configuration.DATABASE,
            user   = username,
            passwd = password
        )

        self.cursor = self.connection.cursor()

    def list_groups(self):
        sentence = """SELECT group_id, group_name, user_full_name 
                FROM %(table_groups)s, %(table_users)s
                WHERE group_owner_id = user_id
            """ % {
                'table_groups' : self._get_table('Group'),
                'table_users'  : self._get_table('User')
            }
        self.cursor.execute(sentence)
        lines = self.cursor.fetchall()
        for group_id, group_name, user_name in lines:
            print "|%s|%s|%s|" % (group_id, group_name, user_name)
        

    def list_users(self, group_name):
        sentence = """SELECT %(table_users)s.user_id,user_login, user_full_name 
                FROM %(table_users)s, %(table_groups)s,%(table_user_member_of)s
                WHERE %(table_users)s.user_id = %(table_user_member_of)s.user_id 
                AND %(table_groups)s.group_id = %(table_user_member_of)s.group_id 
                AND %(table_groups)s.group_name = %(provided_group_name)s""" % {
                'table_users' : self._get_table('User'),
                'table_groups' : self._get_table('Group'),
                'table_user_member_of' : self._get_table('UserIsMemberOf'),
                'provided_group_name' : '%s'
            }
        self.cursor.execute(sentence, group_name)
        lines = self.cursor.fetchall()
        for user_id, user_login, user_full_name in lines:
            print "|%s|%s|%s|" % (user_id, user_login, user_full_name)

    def _get_table(self, table_name):
        complete_prefix = configuration.PREFIX + 'v_a_'
        return complete_prefix + table_name

if __name__ == '__main__':
    option_parser = OptionParser()

    option_parser.add_option( "-g", "--list-groups",
            action="store_true",
            dest="list_groups",
            help="Lists all the groups" 
        )

    option_parser.add_option( "-l", "--list-users",
            dest="list_users",
            nargs=1,
            default=None,
            help="Lists all users member of a group" 
        )

    options, _ = option_parser.parse_args()

    list_manager = ListManager(configuration.USERNAME, configuration.PASSWORD)
    list_manager.connect()

    if options.list_groups:
        list_manager.list_groups()
    elif options.list_users:
        list_manager.list_users(options.list_users)
    else:
        print "No such option"