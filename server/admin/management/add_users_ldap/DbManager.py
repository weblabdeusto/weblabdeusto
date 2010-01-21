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

import sys
import os
sys.path.append(os.sep.join(('..','..','server','src')))

import libraries
import MySQLdb as dbi
import configuration as Cfg

       
class DbManager(object):
    
    def __init__(self):
        self.connection = dbi.connect( 
            host   = Cfg.DB_HOSTNAME,
            db     = Cfg.DB_NAME,
            user   = Cfg.DB_USERNAME,
            passwd = Cfg.DB_PASSWORD
        )
        #self.cursor = self.connection.cursor()

    def user_exists(self, user_login):
        cursor = self.connection.cursor()
        sentence = """SELECT * FROM %(table_users)s
                WHERE %(table_users)s.user_login = %(provided_user_login)s""" % {
                'table_users' : self._get_table('User'),
                'provided_user_login' : '%s'
            }
        cursor.execute(sentence, user_login)
        lines = cursor.fetchall()
        return len(lines) > 0

    def group_exists(self, group_name):
        cursor = self.connection.cursor()
        sentence = """SELECT * FROM %(table_groups)s
                WHERE %(table_groups)s.group_name = %(provided_group_name)s""" % {
                'table_groups' : self._get_table('Group'),
                'provided_group_name' : '%s'
            }
        cursor.execute(sentence, group_name)
        lines = cursor.fetchall()
        return len(lines) > 0
    
    def has_auth(self, user_login, auth_instance_id):
        cursor = self.connection.cursor()
        sentence = """SELECT * FROM %(table_users)s u, %(table_user_auth_user_relation)s r
                WHERE u.user_id=r.uaur_user_id and u.user_id=GetUserIDByName(%(provided_user_login)s) and r.uaur_user_auth_instance_id=GetUserAuthInstanceID(%(provided_auth_instance_id)s)""" % {
                'table_users' : self._get_table('User'),
                'table_user_auth_user_relation' : self._get_table('UserAuthUserRelation'),
                'provided_user_login' : '%s',
                'provided_auth_instance_id' : '%s'
            }
        print sentence
        cursor.execute(sentence, (user_login, auth_instance_id,))
        lines = cursor.fetchall()
        print "lines:",
        print lines
        print
        return len(lines) > 0
    
    def _get_table(self, table_name):
        complete_prefix = Cfg.DB_PREFIX #+ 'v_a_'
        return complete_prefix + table_name
    
    def close(self):
        self.connection.close()