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

import test.unit.configuration as configuration
        
import voodoo.configuration.ConfigurationManager as ConfigurationManager

import weblab.database.Model as Model

import weblab.user_processing.database.DatabaseGateway as DatabaseGateway


class ModelTestCase(unittest.TestCase):
    
    def setUp(self):
        cfg_manager= ConfigurationManager.ConfigurationManager()
        cfg_manager.append_module(configuration)
        self.gateway = DatabaseGateway.create_gateway(cfg_manager)
    
    def test_repr(self):
        session = self.gateway.Session()        
        
        for i in dir(Model):
            if i.startswith("Db"):
                repr(session.query(getattr(Model, i)).first())


def suite():
    return unittest.makeSuite(ModelTestCase)

if __name__ == '__main__':
    unittest.main()