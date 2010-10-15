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
# Author: Luis Rodriguez <luis.rodriguez@opendeusto.es>
# 

import unittest
import mocker
import weblab.experiment.experiments.vm_experiment


class VMExperimentTestCase(mocker.MockerTestCase):
                
    def setUp(self):
        pass

    def tearDown(self):
        pass
        

        
def suite():
    return unittest.makeSuite(VMExperimentTestCase)

if __name__ == '__main__':
    unittest.main()