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

import sys, os
sys.path.append(os.sep.join(("..","..","..","src")))
import libraries

from Db39Gateway import DbGateway as DbOldGateway
from Db40Gateway import DbGateway as DbNewGateway

from weblab.database.Model import *

"""
TABLES TO MIGRATE:

-> wl_Experiment
-> wl_ExperimentCategory
-> wl_Role
-> wl_Group

-> wl_GroupPermissionType
-> wl_GroupPermissionParameterType
-> wl_UserPermissionType
-> wl_UserPermissionParameterType
-> wl_GroupPermissionInstance
-> wl_GroupPermissionParameter

-> wl_UserAuth
-> wl_UserAuthInstance

-> wl_User
-> wl_UserAuthUserRelation

-> wl_UserPermissionInstance
-> wl_UserPermissionParameter

-> wl_UserIsMemberOf

-> wl_UserUsedExperiment
-> wl_UserCommand
-> wl_UserFile
"""

class Migrator(object):
    
    def __init__(self):
        super(Migrator, self).__init__()
        self.db_old = DbOldGateway()
        self.db_new = DbNewGateway("localhost", "WebLab", "weblab", "weblab")
    
    def migrate(self):

        olds = self.db_old.get("SELECT * FROM wl_ExperimentCategory")
        for raw in olds:
            o = self.db_new.insert_experiment_category(raw[0], raw[1])
            print o
            #print ".",
            
        olds = self.db_old.get("SELECT * FROM wl_Experiment")
        for raw in olds:
            o = self.db_new.insert_experiment(raw[0], raw[2], raw[3], raw[4], raw[5])
            print o           
            #print ".",
            
        olds = self.db_old.get("SELECT * FROM wl_Role")
        for raw in olds:
            o = self.db_new.insert_role(raw[0], raw[1])
            print o     
            #print ".",     
            
        olds = self.db_old.get("SELECT * FROM wl_Group")
        for raw in olds:
            o = self.db_new.insert_group(raw[0], raw[1])
            print o     
            #print ".", 
            
        olds = self.db_old.get("SELECT * FROM wl_GroupPermissionType")
        for raw in olds:
            o = self.db_new.insert_permission_type(raw[0], raw[1], raw[2])
            print o 
            #print ".",
            
        olds = self.db_old.get("SELECT * FROM wl_GroupPermissionParameterType")
        for raw in olds:
            o = self.db_new.insert_permission_type_parameter(raw[0], raw[1], raw[2], raw[3], raw[4])
            print o
            #print ".",
            
        olds = self.db_old.get("SELECT * FROM wl_GroupPermissionInstance")
        for raw in olds:
            o = self.db_new.insert_group_permission(raw[0], raw[1], raw[2], raw[4], raw[5], raw[6])
            print o
            #print ".",
            
        olds = self.db_old.get("SELECT * FROM wl_GroupPermissionParameter")
        for raw in olds:
            o = self.db_new.insert_group_permission_parameter(raw[0], raw[1], raw[2], raw[3])
            print o
            #print ".",
            
        olds = self.db_old.get("SELECT * FROM wl_UserAuth")
        for raw in olds:
            o = self.db_new.insert_auth_type(raw[0], raw[1])
            print o
            #print ".",
        # The new AuthType: DB
        o = self.db_new.insert_auth_type(3, "DB")
        print o
        #print ".",
        
        # Hardcoding for us :-)
        olds = self.db_old.get("SELECT * FROM wl_UserAuthInstance")
        for priority, raw in enumerate(olds):
            o = self.db_new.insert_auth(raw[0], raw[1], raw[2], raw[3], priority+1)
            print o
            #print ".",
        o = self.db_new.insert_auth(5, 3, "WebLab DB", None, 0)
        print o
        #print ".",

        olds = self.db_old.get("SELECT * FROM wl_User")
        for raw in olds:
            o = self.db_new.insert_user(raw[0], raw[1], raw[2], raw[3], raw[6])
            print o
            #print ".",

        # Old UserAuthUserRelation's excluding the new 'WebLab DB'
        olds = self.db_old.get("SELECT * FROM wl_UserAuthUserRelation")
        for raw in olds:
            o = self.db_new.insert_user_auth(raw[0], raw[1], None)
            print o
            #print ".",

        # New UserAuth's ('WebLab DB')
        olds = self.db_old.get("SELECT * FROM wl_User")
        for raw in olds:
            if raw[4] is not None:
                o = self.db_new.insert_user_auth(raw[0], 5, raw[4])
                print o      
                #print ".",
                
        olds = self.db_old.get("SELECT * FROM wl_UserPermissionInstance")
        for raw in olds:
            o = self.db_new.insert_user_permission(raw[0], raw[1], raw[2], raw[4], raw[5], raw[6])
            print o
            #print ".",
            
        olds = self.db_old.get("SELECT * FROM wl_UserPermissionParameter")
        for raw in olds:
            o = self.db_new.insert_user_permission_parameter(raw[0], raw[1], raw[2], raw[3])
            print o
            #print ".",

        olds = self.db_old.get("SELECT * FROM wl_UserIsMemberOf")
        for raw in olds:
            o1, o2 = self.db_new.insert_user_is_member_of(raw[0], raw[1])
            print o1, o2    
            #print ".",   
        
        olds = self.db_old.get("SELECT * FROM wl_UserUsedExperiment")
        for raw in olds:
            o = self.db_new.insert_user_used_experiment(raw[0], raw[1], raw[2], raw[3], raw[4], raw[5], raw[6], raw[7], raw[8])
            print o
            #print ".",
        
        olds = self.db_old.get("SELECT * FROM wl_UserCommand")
        for raw in olds:
            o = self.db_new.insert_user_command(raw[0], raw[1], raw[2], raw[3], raw[4], raw[5], raw[6], raw[7])
            print o
            #print ".",
                
        olds = self.db_old.get("SELECT * FROM wl_UserFile")
        for raw in olds:
            o = self.db_new.insert_user_file(raw[0], raw[1], raw[2], raw[3], raw[4], raw[5], raw[6], raw[7], raw[8], raw[9])
            print o
            #print ".",
        
        o = self.db_new.update_auth_config_field("domain=cdk.deusto.es;ldap_uri=ldaps://castor.cdk.deusto.es",
                                                 "ldap_uri=ldaps://castor.cdk.deusto.es;domain=cdk.deusto.es;base=dc=cdk,dc=deusto,dc=es")
        print o
        
        o = self.db_new.update_auth_config_field("domain=deusto.es;ldap_uri=ldaps://castor.cdk.deusto.es",
                                                 "ldap_uri=ldaps://altair.deusto.es;domain=deusto.es;base=dc=deusto,dc=es")
        print o
        
if __name__ == "__main__":
    m = Migrator()
    m.migrate()
