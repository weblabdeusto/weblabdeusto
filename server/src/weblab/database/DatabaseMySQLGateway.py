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

from weblab.database.DatabaseConstants import AUTH, STUDENT, PROFESSOR, ADMINISTRATOR, EXTERNAL_ENTITY
from weblab.database.DatabaseConstants import READ, WRITE, NAME
from weblab.database.DatabaseConstants import SELECT, UPDATE, INSERT

import weblab.exceptions.database.DatabaseExceptions as DbExceptions
import voodoo.exceptions.configuration.ConfigurationExceptions as CfgExceptions

import sqlalchemy

#TODO: capture MySQL Exceptions!!!

DB_DRIVER = 'db_driver'
DEFAULT_DB_DRIVER = 'MySQLdb'

DB_HOST = 'db_host'
DEFAULT_DB_HOST = 'localhost'

DB_DATABASE = 'db_database'
DEFAULT_DB_DATABASE = 'WebLab'

DB_PREFIX = 'db_prefix'
DEFAULT_DB_PREFIX = 'wl_'

DB_CONNECTION_POOL_SIZE = 'db_connection_pool_size'
DEFAULT_DB_CONNECTION_POOL_SIZE = 25

DB_CONNECTION_TIMEOUT = 'db_connection_timeout'
DEFAULT_DB_CONNECTION_TIMEOUT = 60 # seconds

def _db_credentials_checker(f):
    def _get_cursor(self,username,password):
        connection = self.dbi.connect(
                host    = self.host,
                user    = username,
                passwd  = password,
                db  = self.database_name
            )
        return connection.cursor(), connection

    def checker(self,credentials,*args,**kargs):
        #Credentials is a dictionary like:
        #credentials.name -> name (AUTH,ADMINISTRATOR... as in DatabaseConstants.py)
        #credentials[READ] -> (.user,.password)
        #(optionally, credentials[WRITE] -> (.user,.password) )
        cursors = {}
        cursors[NAME] = credentials[NAME]
        cursors[READ], rconnection = _get_cursor(
                    self,
                    credentials[READ].user,
                    credentials[READ].password
                )

        wconnection = None
        if credentials.has_key(WRITE):
            cursors[WRITE], wconnection = _get_cursor(
                        self,
                        credentials[WRITE].user,
                        credentials[WRITE].password
                    )
        try:
            return f(self,cursors,*args,**kargs)
        finally:
            try:
                cursors[READ].close()

                if cursors.has_key(WRITE):
                    wconnection.commit()
                    cursors[WRITE].close()
            except:
                pass

            rconnection.close()
            if wconnection is not None:
                wconnection.close()

    checker.__name__ = f.__name__
    checker.__doc__ = f.__doc__
    return checker

class AbstractDatabaseGateway(object):
    def __init__(self, cfg_manager):

        self._cfg_manager  = cfg_manager

        try:
            self.driver        = cfg_manager.get_value(DB_DRIVER, DEFAULT_DB_DRIVER)
            self.host          = cfg_manager.get_value(DB_HOST, DEFAULT_DB_HOST)            
            self.database_name = cfg_manager.get_value(DB_DATABASE, DEFAULT_DB_DATABASE)
            cfg_prefix         = cfg_manager.get_value(DB_PREFIX, DEFAULT_DB_PREFIX)
        except CfgExceptions.KeyNotFoundException, knfe:
            raise DbExceptions.DbMisconfiguredException(
                    "Configuration manager didn't provide values for at least one parameter: %s" % knfe,
                    knfe
                )

        self.prefix = cfg_prefix + 'v_' #The application will only have access to views
        self.user_prefix = {
            EXTERNAL_ENTITY : 'e_',
            ADMINISTRATOR   : 'a_',
            PROFESSOR   : 'p_',
            STUDENT     : 's_',
            AUTH        : 'auth_'
        }
        self.write_prefix = 'rw_'
        self.write_update_prefix = self.write_prefix + 'update_'
        self.write_insert_prefix = self.write_prefix + 'insert_'

        #Module
        dbi = __import__(self.driver)

        pool_size = self._cfg_manager.get_value(DB_CONNECTION_POOL_SIZE, DEFAULT_DB_CONNECTION_POOL_SIZE)
        timeout = self._cfg_manager.get_value(DB_CONNECTION_TIMEOUT, DEFAULT_DB_CONNECTION_TIMEOUT)
        self.dbi  = sqlalchemy.pool.manage(dbi, pool_size = pool_size, timeout = timeout)

    def _get_user_role(self,cursors,role_id):
        sentence = """SELECT role_name
                FROM %(table_name)s
                WHERE role_id = %(id)s""" %{
                    'table_name' : self._get_table('Role',cursors[NAME],SELECT),
                    'id' : '%s'
                }
        cursors[READ].execute(sentence,role_id)
        line = cursors[READ].fetchone()
        return line[0]

    def _get_table(self,table_name,db_user_name,operation):
        table = self.prefix + self.user_prefix[db_user_name]
        if operation.lower() == SELECT:
            return table + table_name
        if table_name in ('Laboratory','UserUsedExperiment'):
            # TEST ME
            if operation.lower() == UPDATE:
                return table + self.write_update_prefix + table_name
            elif operation.lower() == INSERT:
                return table + self.write_insert_prefix + table_name
        else:
            if operation.lower() in (UPDATE,INSERT):
                return table + self.write_prefix + table_name
            else:
                raise NotImplementedError('operation %s not implemented' % operation)

