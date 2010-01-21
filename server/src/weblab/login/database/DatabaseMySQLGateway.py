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

import re

import voodoo.hashing as hashlib
from voodoo.log import logged

import weblab.exceptions.database.DatabaseExceptions as DbExceptions
from weblab.database.DatabaseConstants import READ, NAME, SELECT
import weblab.database.DatabaseMySQLGateway as dbMySQLGateway
import weblab.login.database.dao.UserAuth as UserAuth
import weblab.data.UserType as UserType


#TODO: capture MySQL Exceptions!!!

class AuthDatabaseGateway(dbMySQLGateway.AbstractDatabaseGateway):

    def __init__(self, cfg_manager):
        super(AuthDatabaseGateway, self).__init__(cfg_manager)

    ####################################################################
    ##################   check_user_password   #########################
    ####################################################################
    @dbMySQLGateway._db_credentials_checker
    @logged(except_for='passwd')
    def check_user_password(self,cursors,user,passwd):
        """check_user_password(credentials,user,passwd) -> UserType, user_id, auth_required

        Provided user and password, the method returns the UserType
        of the user if user and password are correct, and a if not.
        """
        sentence = """SELECT user_password, user_role_id, user_id 
                FROM %(table_name)s 
                WHERE user_login = %(provided_login)s""" % {
                        'table_name'    : self._get_table('User',cursors[NAME],SELECT),
                        'provided_login': '%s' #a parameter
                    }
        cursors[READ].execute(sentence,user)
        line = cursors[READ].fetchone()
        if line == None:
            raise DbExceptions.DbUserNotFoundException("User <%s> not found in database" % user)
        else:
            retrieved_password = line[0]
            user_authenticated = False
            if retrieved_password is not None:
                user_authenticated = self._check_password(retrieved_password, passwd)
                    
            role_id = int(line[1]) 
            user_id = int(line[2])
            user_role = self._get_user_role(cursors,role_id)

            if user_authenticated:
                auth_info = None
            else:
                auth_info = self._retrieve_auth_information(cursors, user_id)
            
            return UserType.getUserTypeEnumerated(user_role),user_id,auth_info

    def _check_password(self, retrieved_password, provided_passwd):
        #Now, user_password is the value stored in the database
        #
        #The format is: random_chars{algorithm}hashed_password
        #
        #random_characters will be, for example, axjl
        #algorithm will be md5 or sha (or sha1), or in the future, other hash algorithms
        #hashed_password will be the hash of random_chars + passwd, using "algorithm" algorithm
        #
        #For example:
        #aaaa{sha}a776159c8c7ff8b73e43aa54d081979e72511474
        #would be the stored password for "password", since
        #the sha hash of "aaaapassword" is a7761...
        #
        REGEX = "([a-zA-Z0-9]*){([a-zA-Z0-9_-]+)}([a-fA-F0-9]+)"
        mo = re.match(REGEX, retrieved_password)
        if mo is None:
            raise DbExceptions.DbInvalidPasswordFormatException(
                    "Invalid password format"
                )
        first_chars, algorithm, hashed_passwd = mo.groups()

        if algorithm == 'sha':
            algorithm = 'sha1' #TODO

        try:
            hashobj = hashlib.new(algorithm)
        except Exception, e:
            raise DbExceptions.DbHashAlgorithmNotFoundException(
                    "Algorithm %s not found" % algorithm
                )

        hashobj.update((first_chars + provided_passwd).encode())
        return hashobj.hexdigest() == hashed_passwd

    def _retrieve_auth_information(self, cursors, user_id):
        sentence = """SELECT auth_name, uai_configuration
                FROM %(UserAuthTable)s, %(UserAuthInstanceTable)s, %(UserAuthUserRelationTable)s
                WHERE 
                    uai_user_auth_id = user_auth_id
                    AND uaur_user_auth_instance_id = user_auth_instance_id
                    AND uaur_user_id = %(provided_user_id)s
            """ % {
            'UserAuthTable':        self._get_table('UserAuth',cursors[NAME],SELECT),
            'UserAuthInstanceTable':    self._get_table('UserAuthInstance',cursors[NAME],SELECT),
            'UserAuthUserRelationTable':    self._get_table('UserAuthUserRelation',cursors[NAME],SELECT),
            'provided_user_id':         '%s' #a parameter
        }
        cursors[READ].execute(sentence,user_id)
        results = cursors[READ].fetchall()
        user_auths = []
        for auth_name, configuration in results:
            user_auth = UserAuth.UserAuth.create_user_auth(auth_name, configuration)
            user_auths.append(user_auth)

        if len(user_auths) == 0:
            raise DbExceptions.DbNoUserAuthNorPasswordFoundException(
                    "No UserAuth found"
                )

        return user_auths
 
