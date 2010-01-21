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

import unittest

import voodoo.gen.coordinator.CoordVersion as CoordVersion
import voodoo.gen.coordinator.CoordAddress as CoordAddress
import voodoo.gen.exceptions.coordinator.CoordVersionExceptions as CoordVersionExceptions

class VersionTestCase(unittest.TestCase):
    def test_version_change(self):
        address = CoordAddress.CoordAddress('machine_id')
        self.assertRaises(
                CoordVersionExceptions.CoordVersionNotAnActionException,
                CoordVersion.CoordVersionChange,
                address,
                'NEW'
            )
        self.assertRaises(
                CoordVersionExceptions.CoordVersionNotAnAddressException,
                CoordVersion.CoordVersionChange,
                'machine_id',
                CoordVersion.ChangeActions.NEW
            )
    
def suite():
    return unittest.makeSuite(VersionTestCase)

if __name__ == '__main__':
    unittest.main()

