#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2005 onwards University of Deusto
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

from sqlalchemy.orm.exc import NoResultFound

from weblab.db.session import ValidDatabaseSessionId
from weblab.db.model import DbUser, DbGroup, DbAuthType, DbRole, DbUserAuth

from voodoo.log import logged
import voodoo.log as log

import weblab.db.exc as DbErrors
import weblab.db.gateway as dbGateway

#TODO: capture MySQL Exceptions!!!

class AuthDatabaseGateway(dbGateway.AbstractDatabaseGateway):

    def __init__(self, cfg_manager):
        super(AuthDatabaseGateway, self).__init__(cfg_manager)

    @logged()
    def retrieve_role_and_user_auths(self, username):
        """ Retrieve the role and user auths for a given username."""
        session = self.Session()
        try:
            try:
                user = session.query(DbUser).filter_by(login=username).one()
            except NoResultFound:
                raise DbErrors.DbUserNotFoundError("User '%s' not found in database" % username)

            all_user_auths = session.query(DbUserAuth).filter_by(user=user).all()
            
            # 
            sorted_user_auths = sorted(all_user_auths, lambda x, y: cmp(x.auth.priority, y.auth.priority))
            if len(sorted_user_auths) > 0:
                return user.role.name, [ user_auth.to_business() for user_auth in sorted_user_auths ]
            else:
                raise DbErrors.DbNoUserAuthNorPasswordFoundError(
                        "No UserAuth found"
                    )
        finally:
            session.close()

    @logged()
    def check_external_credentials(self, external_id, system):
        """ Given an External ID, such as the ID in Facebook or Moodle or whatever, and selecting
        the system, return the first username that matches with that user_id. The method will
        expect that the system uses something that starts by the id"""
        session = self.Session()
        try:
            try:
                auth_type = session.query(DbAuthType).filter_by(name=system).one()
                if len(auth_type.auths) == 0:
                    raise DbErrors.DbUserNotFoundError("No instance of system '%s' found in database." % system)
            except NoResultFound:
                raise DbErrors.DbUserNotFoundError("System '%s' not found in database" % system)

            try:
                user_auth = session.query(DbUserAuth).filter(DbUserAuth.auth.in_(auth_type.auths), DbUserAuth.configuration==external_id).one()
            except NoResultFound:
                raise DbErrors.DbUserNotFoundError("User '%s' not found in database" % external_id)

            user = user_auth.user
            return ValidDatabaseSessionId( user.login, user.role.name)
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
                auth_type = session.query(DbAuthType).filter_by(name=system).one()
                auth = auth_type.auths[0]
            except (NoResultFound, KeyError):
                raise DbErrors.DbUserNotFoundError("System '%s' not found in database" % system)

            try:
                user = session.query(DbUser).filter_by(login=username).one()
            except NoResultFound:
                raise DbErrors.DbUserNotFoundError("User '%s' not found in database" % user)

            for user_auth in user.auths:
                if user_auth.auth == auth:
                    raise DbErrors.DbUserNotFoundError("User '%s' already has credentials in system %s" % (username, system))

            user_auth = DbUserAuth(user = user, auth = auth, configuration=str(external_id))
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
                auth_type = session.query(DbAuthType).filter_by(name=system).one()
                auth = auth_type.auths[0]
            except (NoResultFound, KeyError):
                raise DbErrors.DbUserNotFoundError("System '%s' not found in database" % system)

            groups = []
            for group_name in group_names:
                try:
                    group = session.query(DbGroup).filter_by(name=group_name).one()
                except NoResultFound:
                    raise DbErrors.DbUserNotFoundError("Group '%s' not found in database" % group_name)
                groups.append(group)

            try:
                role = session.query(DbRole).filter_by(name=external_user.role.name).one()
                user = DbUser(external_user.login, external_user.full_name, external_user.email, role = role)
                user_auth = DbUserAuth(user, auth, configuration = external_id)
                for group in groups:
                    group.users.append(user)
                session.add(user)
                session.add(user_auth)
                session.commit()
            except Exception as e:
                log.log( AuthDatabaseGateway, log.level.Warning, "Couldn't create user: %s" % e)
                log.log_exc(AuthDatabaseGateway, log.level.Info)
                raise DbErrors.DatabaseError("Couldn't create user! Contact administrator")
        finally:
            session.close()

def create_auth_gateway(cfg_manager):
    return AuthDatabaseGateway(cfg_manager)

