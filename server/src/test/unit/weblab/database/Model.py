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

import unittest
import datetime

import weblab.database.Model as Model


class ModelTestCase(unittest.TestCase):
    
    def test_link_relation(self):
        
        class EntityA(object):
            def __init__(self):
                self.b = None
                self.b_id = None
                self.b_fk = None
        
        class EntityB(object):
            def __init__(self, id=None):
                self.id = id

        # Linking b to a.b not having b being persisted
        a = EntityA()
        b = EntityB()
        Model.link_relation(a, b, "b")
        self.assertEquals(a.b, b)
        
        # Linking b to a.b having b being persisted (specific fkfield)
        a = EntityA()
        b = EntityB(3)
        Model.link_relation(a, b, "b", "bfk")
        self.assertEquals(getattr(a, "bfk"), b.id)
        
        # Linking b to a.b having b being persisted (default fkfield)
        a = EntityA()
        b = EntityB(3)
        Model.link_relation(a, b, "b")
        self.assertEquals(a.b_id, b.id)
        
    
    def test_model(self):
        
        #
        # Create objects
        #
        auth_type = Model.DbAuthType("DB")
        
        permission_type = Model.DbPermissionType(
                'experiment_allowed',
                'This type has a parameter which is the permanent ID (not a INT) of an Experiment. Users which have this permission will have access to the experiment defined in this parameter',
                user_applicable = True,
                group_applicable = True,
                role_applicable = True,
                ee_applicable = True
        )
        permission_type_p1 = Model.DbPermissionTypeParameter(permission_type, 'experiment_permanent_id', 'string', 'the unique name of the experiment')
        permission_type_p2 = Model.DbPermissionTypeParameter(permission_type, 'experiment_category_id', 'string', 'the unique name of the category of experiment')
        permission_type_p3 = Model.DbPermissionTypeParameter(permission_type, 'time_allowed', 'float', 'Time allowed (in seconds)')
        
        auth = Model.DbAuth(auth_type, "WebLab DB", 1)
        
        role = Model.DbRole("administrator")
        
        user = Model.DbUser("admin1", "Name of administrator 1", "weblab@deusto.es", None, role)
        
        ee = Model.DbExternalEntity("ee1", "Country of ee1", "Description of ee1", "weblab@other.es", "password")
        
        user_auth = Model.DbUserAuth(user, auth, "aaaa{sha}a776159c8c7ff8b73e43aa54d081979e72511474")
        
        group = Model.DbGroup("5A")
        
        experiment_category = Model.DbExperimentCategory("Dummy experiments")
        
        experiment = Model.DbExperiment("ud-dummy", experiment_category, datetime.datetime.utcnow(), datetime.datetime.utcnow())
        
        user_permission = Model.DbUserPermission(
            user,
            permission_type.group_applicable,
            "student2::weblab-pld",
            datetime.datetime.utcnow(),
            "Permission for student2 to use WebLab-PLD"
        )
        user_permission_p1 = Model.DbUserPermissionParameter(user_permission, permission_type_p1, "ud-pld")
        user_permission_p2 = Model.DbUserPermissionParameter(user_permission, permission_type_p2, "PLD experiments")
        user_permission_p3 = Model.DbUserPermissionParameter(user_permission, permission_type_p3, "100")   
          
        group_permission = Model.DbGroupPermission(
            group,
            permission_type.group_applicable,
            "5A::weblab-dummy",
            datetime.datetime.utcnow(),
            "Permission for group 5A to use WebLab-Dummy"
        )
        group_permission_p1 = Model.DbGroupPermissionParameter(group_permission, permission_type_p1, "ud-dummy")
        group_permission_p2 = Model.DbGroupPermissionParameter(group_permission, permission_type_p2, "Dummy experiments")
        group_permission_p3 = Model.DbGroupPermissionParameter(group_permission, permission_type_p3, "300")    
          
        role_permission = Model.DbRolePermission(
            role,
            permission_type.role_applicable,
            "administrator::weblab-dummy",
            datetime.datetime.utcnow(),
            "Permission for administrator to use WebLab-Dummy"
        )
        role_permission_p1 = Model.DbRolePermissionParameter(role_permission, permission_type_p1, "ud-dummy")
        role_permission_p2 = Model.DbRolePermissionParameter(role_permission, permission_type_p2, "Dummy experiments")
        role_permission_p3 = Model.DbRolePermissionParameter(role_permission, permission_type_p3, "300")        
          
        ee_permission = Model.DbExternalEntityPermission(
            ee,
            permission_type.ee_applicable,
            "ee1::weblab-dummy",
            datetime.datetime.utcnow(),
            "Permission for ee1 to use WebLab-Dummy"
        )
        ee_permission_p1 = Model.DbExternalEntityPermissionParameter(ee_permission, permission_type_p1, "ud-dummy")
        ee_permission_p2 = Model.DbExternalEntityPermissionParameter(ee_permission, permission_type_p2, "Dummy experiments")
        ee_permission_p3 = Model.DbExternalEntityPermissionParameter(ee_permission, permission_type_p3, "300")                   

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
        # Method DbPermissionType.get_parameter()
        #
        self.assertEquals(permission_type_p1, permission_type.get_parameter("experiment_permanent_id"))
        self.assertEquals(permission_type_p2, permission_type.get_parameter("experiment_category_id"))
        self.assertEquals(permission_type_p3, permission_type.get_parameter("time_allowed"))
        
        #
        # Method Db(User|Group|Role|ExternalEntity)Permission.get_permission_type()
        #
        self.assertEquals(permission_type, user_permission.get_permission_type())
        self.assertEquals(permission_type, group_permission.get_permission_type())
        self.assertEquals(permission_type, role_permission.get_permission_type())
        self.assertEquals(permission_type, ee_permission.get_permission_type())
        
        #
        # Method Db(User|Group|Role|ExternalEntity)Permission.get_parameter()
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
        self.assertEquals(ee_permission_p1, ee_permission.get_parameter("experiment_permanent_id"))
        self.assertEquals(ee_permission_p2, ee_permission.get_parameter("experiment_category_id"))
        self.assertEquals(ee_permission_p3, ee_permission.get_parameter("time_allowed"))
        
        #
        # Method Db(User|Group|Role|ExternalEntity)PermissionParameter.get_name()
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
        self.assertEquals("experiment_permanent_id", ee_permission_p1.get_name())
        self.assertEquals("experiment_category_id", ee_permission_p2.get_name())
        self.assertEquals("time_allowed", ee_permission_p3.get_name())
        
        #
        # Method Db(User|Group|Role|ExternalEntity)PermissionParameter.get_datatype()
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
        self.assertEquals("string", ee_permission_p1.get_datatype())
        self.assertEquals("string", ee_permission_p2.get_datatype())
        self.assertEquals("float", ee_permission_p3.get_datatype())
                

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