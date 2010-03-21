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
#         Jaime Irurzun <jaime.irurzun@gmail.com>
# 

import re

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

import weblab.database.Model as Model

import voodoo.hashing as hashlib
from voodoo.log import logged

import weblab.exceptions.database.DatabaseExceptions as DbExceptions
import weblab.database.DatabaseMySQLGateway as dbMySQLGateway
import weblab.data.UserType as UserType

WEBLAB_DB_USERNAME_PROPERTY = 'weblab_db_username'
DEFAULT_WEBLAB_DB_USERNAME  = 'weblab'

WEBLAB_DB_PASSWORD_PROPERTY = 'weblab_db_password'

def getconn():
    import MySQLdb as dbi
    return dbi.connect(user = AuthDatabaseGateway.user, passwd = AuthDatabaseGateway.password,
            host = AuthDatabaseGateway.host, db = AuthDatabaseGateway.dbname, client_flag = 2)

#TODO: capture MySQL Exceptions!!!

class AuthDatabaseGateway(dbMySQLGateway.AbstractDatabaseGateway):

    user     = None
    password = None
    host     = None
    dbname   = None

    pool = sqlalchemy.pool.QueuePool(getconn, pool_size=15, max_overflow=20)

    def __init__(self, cfg_manager):
        super(AuthDatabaseGateway, self).__init__(cfg_manager)

        AuthDatabaseGateway.user     = cfg_manager.get_value(WEBLAB_DB_USERNAME_PROPERTY, DEFAULT_WEBLAB_DB_USERNAME)
        AuthDatabaseGateway.password = cfg_manager.get_value(WEBLAB_DB_PASSWORD_PROPERTY)
        AuthDatabaseGateway.host     = self.host
        AuthDatabaseGateway.dbname   = self.database_name

        connection_url = "mysql://%(USER)s:%(PASSWORD)s@%(HOST)s/%(DATABASE)s" % \
                            { "USER":     self.user,
                              "PASSWORD": self.password,
                              "HOST":     self.host,
                              "DATABASE": self.dbname }
        self.Session = sessionmaker(bind=create_engine(connection_url, echo=False, pool = self.pool))

    ####################################################################
    ##################   check_user_password   #########################
    ####################################################################
    @logged(except_for='passwd')
    def check_user_password(self,username,passwd):
        """check_user_password(credentials,username,passwd) -> UserType, user_id, auth_required

        Provided user and password, the method returns the UserType
        of the user if user and password are correct, and a if not.
        """
        session = self.Session()
        try:
            try:
                user = session.query(Model.DbUser).filter_by(login=username).one()
            except NoResultFound:
                raise DbExceptions.DbUserNotFoundException("User '%s' not found in database" % username)

            try:
                retrieved_password = [ userauth.configuration for userauth in user.auths if userauth.auth.auth_type.name == "DB" ][0]
                user_authenticated = self._check_password(retrieved_password, passwd)
            except IndexError:
                user_authenticated = False            
            
            if user_authenticated:
                auth_info = None
            else:
                auth_info = self._retrieve_auth_information(user, session)
            
            return UserType.getUserTypeEnumerated(user.role.name), user.id, auth_info
        finally:
            session.close()

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

    def _retrieve_auth_information(self, p_user, session):
        # Kludge: We exclude the "WebLab DB" Auth, since it has already been checked when checking user/password.
        weblab_db_auth = session.query(Model.DbAuth).filter_by(name="WebLab DB").one()
        user_auths = session.query(Model.DbUserAuth).filter_by(user=p_user).filter(Model.DbUserAuth.auth != weblab_db_auth).all()
        if len(user_auths) > 0:
            return [ user_auth.to_business() for user_auth in user_auths ]
        else:
            raise DbExceptions.DbNoUserAuthNorPasswordFoundException(
                    "No UserAuth found"
                )
