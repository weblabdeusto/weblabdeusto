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



import voodoo.gen.coordinator.CoordAddress as CoordAddress
import voodoo.gen.exceptions.coordinator.CoordinatorExceptions as CoordExceptions

class CoordAddressTestCase(unittest.TestCase):
    def test_hashable(self):
        coord_address1  = CoordAddress.CoordAddress.translate_address("a:b@c")
        coord_address2  = CoordAddress.CoordAddress.translate_address("a:b@c")
        self.assertEquals(hash(coord_address1), hash(coord_address2))

    def test_coord_address(self):
        machine     = 'machine_example'
        instance    = 'instance_example'
        server      = 'server_example'
        coordAddress    = CoordAddress.CoordAddress(machine,instance,server)

        self.assertEqual(machine,coordAddress.machine_id)
        self.assertEqual(instance,coordAddress.instance_id)
        self.assertEqual(server,coordAddress.server_id)

        coordAddress2 = CoordAddress.CoordAddress.translate_address(
                    coordAddress.address
                )

        self.assertEqual(coordAddress,coordAddress2)
        self.assertRaises(
                CoordExceptions.CoordInvalidAddressName,
                CoordAddress.CoordAddress.translate_address,
                'whatever'
            )

def suite():
    return unittest.makeSuite(CoordAddressTestCase)

if __name__ == '__main__':
    unittest.main()

