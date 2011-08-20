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

import hashlib
from voodoo.log import logged
import voodoo.log as log

import weblab.database.exc as DbExceptions
import weblab.database.DatabaseMySQLGateway as dbMySQLGateway

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
        self.Session = sessionmaker(bind=create_engine(connection_url, echo=False, convert_unicode=True, pool = self.pool))

    ###########################################################################
    ##################   check_external_credentials   #########################
    ###########################################################################
    @logged()
    def check_external_credentials(self, external_id, system):
        """ Given an External ID, such as the ID in Facebook or Moodle or whatever, and selecting 
        the system, return the first username that matches with that user_id. The method will 
        expect that the system uses something that starts by the id"""
        session = self.Session()
        try:
            try:
                auth_type = session.query(Model.DbAuthType).filter_by(name=system).one()
                auth = auth_type.auths[0]
            except (NoResultFound, KeyError):
                raise DbExceptions.DbUserNotFoundException("System '%s' not found in database" % system)

            try:
                user_auth = session.query(Model.DbUserAuth).filter_by(auth = auth, configuration=external_id).one()
            except NoResultFound:
                raise DbExceptions.DbUserNotFoundException("User '%s' not found in database" % external_id)

            user = user_auth.user
            return user.login, user.role
        finally:
            session.close()

    ###########################################################################
    ##################   grant_external_credentials   #########################
    ###########################################################################
    @logged()
    def grant_external_credentials(self, username, external_id, system):
        """ Given a system and an external_id, grant access with those credentials for user user_id. Before calling
        this method, the system has checked that this user is the owner of external_id and of user_id"""
        session = self.Session()
        try:
            try:
                auth_type = session.query(Model.DbAuthType).filter_by(name=system).one()
                auth = auth_type.auths[0]
            except (NoResultFound, KeyError):
                raise DbExceptions.DbUserNotFoundException("System '%s' not found in database" % system)

            try:
                user = session.query(Model.DbUser).filter_by(login=username).one()
            except NoResultFound:
                raise DbExceptions.DbUserNotFoundException("User '%s' not found in database" % user)

            for user_auth in user.auths:
                if user_auth.auth == auth:
                    raise DbExceptions.DbUserNotFoundException("User '%s' already has credentials in system %s" % (username, system))

            user_auth = Model.DbUserAuth(user = user, auth = auth, configuration=str(external_id))
            session.add(user_auth)
            session.commit()
        finally:
            session.close()

    #####################################################################
    ##################   create_external_user   #########################
    #####################################################################
    @logged()
    def create_external_user(self, external_user, external_id, system, group_names):
        session = self.Session()
        try:
            try:
                auth_type = session.query(Model.DbAuthType).filter_by(name=system).one()
                auth = auth_type.auths[0]
            except (NoResultFound, KeyError):
                raise DbExceptions.DbUserNotFoundException("System '%s' not found in database" % system)

            groups = []
            for group_name in group_names:
                try:
                    group = session.query(Model.DbGroup).filter_by(name=group_name).one()
                except NoResultFound:
                    raise DbExceptions.DbUserNotFoundException("Group '%s' not found in database" % group_name)
                groups.append(group)

            try:
                role = session.query(Model.DbRole).filter_by(name=external_user.role.name).one()
                user = Model.DbUser(external_user.login, external_user.full_name, external_user.email, role = role)
                user_auth = Model.DbUserAuth(user, auth, configuration = external_id)
                for group in groups:
                    group.users.append(user)
                session.add(user)
                session.add(user_auth)
                session.commit()
            except Exception as e:
                log.log( AuthDatabaseGateway, log.LogLevel.Warning, "Couldn't create user: %s" % e)
                log.log_exc(AuthDatabaseGateway, log.LogLevel.Info)
                raise DbExceptions.DatabaseException("Couldn't create user! Contact administrator")
        finally:
            session.close()

    ####################################################################
    ##################   check_user_password   #########################
    ####################################################################
    @logged(except_for='passwd')
    def check_user_password(self,username,passwd):
        """check_user_password(credentials,username,passwd) -> role, user_id, auth_required

        Provided user and password, the method returns the Role
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
                has_password = True
            except IndexError:
                has_password = False

            if has_password:
                if not self._check_password(retrieved_password, passwd):
                    raise DbExceptions.DbInvalidUserOrPasswordException("Invalid password: '%s'" % passwd)
                auth_info = None
            else:
                auth_info = self._retrieve_auth_information(user, session)
            
            return user.role, user.id, auth_info
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
        except Exception:
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

