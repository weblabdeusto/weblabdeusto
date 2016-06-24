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
# Author: Jaime Irurzun <jaime.irurzun@gmail.com>
#
from __future__ import print_function, unicode_literals

import unittest
import datetime

import weblab.db.model as Model

import weblab.permissions as permissions

class ModelTestCase(unittest.TestCase):

    def test_model_invitations(self):

        #
        # Create objects.
        #
        group = Model.DbGroup("InvGroup")
        role = Model.DbRole("student")
        user = Model.DbUser("InvUser", "Name of Invitation User", "weblab@deusto.es", None, role)
        invitation = Model.DbInvitation(group, 5, True)
        invitation_accept = Model.DbAcceptedInvitation(invitation, user, True)


    def test_model(self):

        #
        # Create objects
        #
        auth_type = Model.DbAuthType("DB")

        permission_type = permissions.EXPERIMENT_ALLOWED
        permission_type_p1 = permissions.EXPERIMENT_PERMANENT_ID 
        permission_type_p2 = permissions.EXPERIMENT_CATEGORY_ID 
        permission_type_p3 = permissions.TIME_ALLOWED 

        auth = Model.DbAuth(auth_type, "WebLab DB", 1)

        role = Model.DbRole("administrator")

        user = Model.DbUser("admin1", "Name of administrator 1", "weblab@deusto.es", None, role)

        group = Model.DbGroup("5A")

        user_permission = Model.DbUserPermission(
            user,
            permission_type,
            "student2::weblab-pld",
            datetime.datetime.utcnow(),
            "Permission for student2 to use WebLab-PLD"
        )
        user_permission_p1 = Model.DbUserPermissionParameter(user_permission, permission_type_p1, "ud-pld")
        user_permission_p2 = Model.DbUserPermissionParameter(user_permission, permission_type_p2, "PLD experiments")
        user_permission_p3 = Model.DbUserPermissionParameter(user_permission, permission_type_p3, "100")

        group_permission = Model.DbGroupPermission(
            group,
            permission_type,
            "5A::weblab-dummy",
            datetime.datetime.utcnow(),
            "Permission for group 5A to use WebLab-Dummy"
        )
        group_permission_p1 = Model.DbGroupPermissionParameter(group_permission, permission_type_p1, "ud-dummy")
        group_permission_p2 = Model.DbGroupPermissionParameter(group_permission, permission_type_p2, "Dummy experiments")
        group_permission_p3 = Model.DbGroupPermissionParameter(group_permission, permission_type_p3, "300")

        role_permission = Model.DbRolePermission(
            role,
            permission_type,
            "administrator::weblab-dummy",
            datetime.datetime.utcnow(),
            "Permission for administrator to use WebLab-Dummy"
        )
        role_permission_p1 = Model.DbRolePermissionParameter(role_permission, permission_type_p1, "ud-dummy")
        role_permission_p2 = Model.DbRolePermissionParameter(role_permission, permission_type_p2, "Dummy experiments")
        role_permission_p3 = Model.DbRolePermissionParameter(role_permission, permission_type_p3, "300")

        #
        # Method __repr__()
        #
        variables = locals()
        variables.pop("self")
        for k in variables.keys():
            repr(eval(k))

        #
        # Method DbAuth.get_config_value()
        #
        auth.configuration = "param1=value1;param2=value2"
        self.assertEquals("value1", auth.get_config_value("param1"))
        self.assertEquals("value2", auth.get_config_value("param2"))

        #
        # Method Db(User|Group|Role)Permission.get_permission_type()
        #
        self.assertEquals(permission_type, user_permission.get_permission_type())
        self.assertEquals(permission_type, group_permission.get_permission_type())
        self.assertEquals(permission_type, role_permission.get_permission_type())

        #
        # Method Db(User|Group|Role)Permission.get_parameter()
        #
        self.assertEquals(user_permission_p1, user_permission.get_parameter("experiment_permanent_id"))
        self.assertEquals(user_permission_p2, user_permission.get_parameter("experiment_category_id"))
        self.assertEquals(user_permission_p3, user_permission.get_parameter("time_allowed"))
        self.assertEquals(group_permission_p1, group_permission.get_parameter("experiment_permanent_id"))
        self.assertEquals(group_permission_p2, group_permission.get_parameter("experiment_category_id"))
        self.assertEquals(group_permission_p3, group_permission.get_parameter("time_allowed"))
        self.assertEquals(role_permission_p1, role_permission.get_parameter("experiment_permanent_id"))
        self.assertEquals(role_permission_p2, role_permission.get_parameter("experiment_category_id"))
        self.assertEquals(role_permission_p3, role_permission.get_parameter("time_allowed"))

        #
        # Method Db(User|Group|Role)PermissionParameter.get_name()
        #
        self.assertEquals("experiment_permanent_id", user_permission_p1.get_name())
        self.assertEquals("experiment_category_id", user_permission_p2.get_name())
        self.assertEquals("time_allowed", user_permission_p3.get_name())
        self.assertEquals("experiment_permanent_id", group_permission_p1.get_name())
        self.assertEquals("experiment_category_id", group_permission_p2.get_name())
        self.assertEquals("time_allowed", group_permission_p3.get_name())
        self.assertEquals("experiment_permanent_id", role_permission_p1.get_name())
        self.assertEquals("experiment_category_id", role_permission_p2.get_name())
        self.assertEquals("time_allowed", role_permission_p3.get_name())

        #
        # Method Db(User|Group|Role)PermissionParameter.get_datatype()
        #
        self.assertEquals("string", user_permission_p1.get_datatype())
        self.assertEquals("string", user_permission_p2.get_datatype())
        self.assertEquals("float", user_permission_p3.get_datatype())
        self.assertEquals("string", group_permission_p1.get_datatype())
        self.assertEquals("string", group_permission_p2.get_datatype())
        self.assertEquals("float", group_permission_p3.get_datatype())
        self.assertEquals("string", role_permission_p1.get_datatype())
        self.assertEquals("string", role_permission_p2.get_datatype())
        self.assertEquals("float", role_permission_p3.get_datatype())


    def test_splitted_utc_datetime_to_timestamp(self):
        dt = datetime.datetime(2010, 06, 14, 15, 45, 00)
        ms = 12345
        timestamp = Model._splitted_utc_datetime_to_timestamp(dt, ms)
        self.assertEquals(1276530300.0123451, timestamp)

    def test_splitted_utc_datetime_to_timestamp_with_none_dt(self):
        dt = None
        ms = 12345
        timestamp = Model._splitted_utc_datetime_to_timestamp(dt, ms)
        self.assertEquals(None, timestamp)


    def test_timestamp_to_splitted_utc_datetime(self):
        dt, ms = Model._timestamp_to_splitted_utc_datetime(1276530300.0123451)
        self.assertEquals(datetime.datetime(2010, 06, 14, 15, 45, 00, 12345), dt)
        self.assertEquals(12345, ms)

    def test_timestamp_to_splitted_utc_datetime_with_none_timestamp(self):
        dt, ms = Model._timestamp_to_splitted_utc_datetime(None)
        self.assertEquals(None, dt)
        self.assertEquals(None, ms)


def suite():
    return unittest.makeSuite(ModelTestCase)

if __name__ == '__main__':
    unittest.main()
