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
        db = Model.DbAuthType("DB")
        
        experiment_allowed = Model.DbPermissionType(
                'experiment_allowed',
                'This type has a parameter which is the permanent ID (not a INT) of an Experiment. Users which have this permission will have access to the experiment defined in this parameter',
                user_applicable = True,
                group_applicable = True,
                ee_applicable = True
        )
        experiment_allowed_p1 = Model.DbPermissionTypeParameter(experiment_allowed, 'experiment_permanent_id', 'string', 'the unique name of the experiment')
        experiment_allowed_p2 = Model.DbPermissionTypeParameter(experiment_allowed, 'experiment_category_id', 'string', 'the unique name of the category of experiment')
        experiment_allowed_p3 = Model.DbPermissionTypeParameter(experiment_allowed, 'time_allowed', 'float', 'Time allowed (in seconds)')
        
        weblab_db = Model.DbAuth(db, "WebLab DB", 1)
        
        administrator = Model.DbRole("administrator")
        
        admin1 = Model.DbUser("admin1", "Name of administrator 1", "weblab@deusto.es", None, administrator)
        
        ee1 = Model.DbExternalEntity("ee1", "Country of ee1", "Description of ee1", "weblab@other.es", "password")
        
        user_auth = Model.DbUserAuth(admin1, weblab_db, "aaaa{sha}a776159c8c7ff8b73e43aa54d081979e72511474")
        
        group5A = Model.DbGroup("5A")
        
        dummy_cat = Model.DbExperimentCategory("Dummy experiments")
        
        dummy = Model.DbExperiment("ud-dummy", dummy_cat, datetime.datetime.utcnow(), datetime.datetime.utcnow())
        
        up_student2_pld_allowed = Model.DbUserPermission(
            admin1,
            experiment_allowed.group_applicable,
            "student2::weblab-pld",
            datetime.datetime.utcnow(),
            "Permission for student2 to use WebLab-PLD"
        )
        up_student2_pld_allowed_p1 = Model.DbUserPermissionParameter(up_student2_pld_allowed, experiment_allowed_p1, "ud-pld")
        up_student2_pld_allowed_p2 = Model.DbUserPermissionParameter(up_student2_pld_allowed, experiment_allowed_p2, "PLD experiments")
        up_student2_pld_allowed_p3 = Model.DbUserPermissionParameter(up_student2_pld_allowed, experiment_allowed_p3, "100")   
          
        gp_5A_dummy_allowed = Model.DbGroupPermission(
            group5A,
            experiment_allowed.group_applicable,
            "5A::weblab-dummy",
            datetime.datetime.utcnow(),
            "Permission for group 5A to use WebLab-Dummy"
        )
        gp_5A_dummy_allowed_p1 = Model.DbGroupPermissionParameter(gp_5A_dummy_allowed, experiment_allowed_p1, "ud-dummy")
        gp_5A_dummy_allowed_p2 = Model.DbGroupPermissionParameter(gp_5A_dummy_allowed, experiment_allowed_p2, "Dummy experiments")
        gp_5A_dummy_allowed_p3 = Model.DbGroupPermissionParameter(gp_5A_dummy_allowed, experiment_allowed_p3, "300")           

        #
        # Method __repr__
        #        
        variables = locals()
        variables.pop("self")
        for k in variables.keys():
            repr(eval(k))
            

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