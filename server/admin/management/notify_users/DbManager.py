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
#

import MySQLdb as dbi
import Configuration

        
class DbManager(object):
    
    def __init__(self):
        self.connection = dbi.connect( 
            host   = Configuration.HOSTNAME,
            db     = Configuration.DATABASE,
            user   = Configuration.USERNAME,
            passwd = Configuration.PASSWORD
        )
        self.cursor = self.connection.cursor()

    def get_group_users(self, group_name):
        sentence = """SELECT %(table_users)s.user_id,user_login, user_full_name, user_email 
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
        users = []
        for id, login, full_name, email in lines:
            users.append(dict(id=id, login=login, full_name=full_name, email=email))
        return users

    def _get_table(self, table_name):
        complete_prefix = Configuration.PREFIX + 'v_a_'
        return complete_prefix + table_name