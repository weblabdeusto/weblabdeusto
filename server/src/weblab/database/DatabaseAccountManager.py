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

import weblab.exceptions.database.DatabaseExceptions as DbExceptions
import weblab.database.DatabaseConstants as DbConst

class DatabaseUserInformation(object):
    def __init__(self,user,password):
        self.user = user
        self.password = password

__users = {
    DbConst.AUTH        : { DbConst.NAME: DbConst.AUTH,         DbConst.READ : None },
    DbConst.STUDENT     : { DbConst.NAME: DbConst.STUDENT,      DbConst.READ : None, DbConst.WRITE: None },
    DbConst.PROFESSOR   : { DbConst.NAME: DbConst.PROFESSOR,        DbConst.READ : None, DbConst.WRITE: None },
    DbConst.ADMINISTRATOR   : { DbConst.NAME: DbConst.ADMINISTRATOR,    DbConst.READ : None, DbConst.WRITE: None },
    DbConst.EXTERNAL_ENTITY : { DbConst.NAME: DbConst.EXTERNAL_ENTITY,  DbConst.READ : None, DbConst.WRITE: None }
}

def update_database_accounts(accounts):
    #accounts in the same format as __users
    for i in accounts:
        for j in accounts[i]:
            if j != DbConst.NAME:
                __users[i][j] = DatabaseUserInformation( 
                        accounts[i][j].user,
                        accounts[i][j].password
                    )

def get_credentials(level):
    if not level in __users.keys():
        raise DbExceptions.DbCredentialsLevelNotFoundException(
                'Level not found: <%s>. Known levels: <%s>' % 
                    (level,__users.keys())
            )
    return __users[level]

