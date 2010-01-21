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

import voodoo.hashing

class HashingTestCase(unittest.TestCase):
    def test_wrong_algorithm(self):
        self.assertRaises(
            voodoo.hashing.AlgorithmNotFoundException,
            voodoo.hashing.new,
            'whatever'
        )

    def test_good_algorithm(self):
        md = voodoo.hashing.new('md5')
        md.update("whatever".encode())
        self.assertEquals(
            '008c5926ca861023c1d2a36653fd88e2',
            md.hexdigest()
        )

        sh = voodoo.hashing.new('sha1')
        sh.update("whatever".encode())
        self.assertEquals(
            'd869db7fe62fb07c25a0403ecaea55031744b5fb',
            sh.hexdigest()
        )


def suite():
    return unittest.makeSuite(HashingTestCase)

if __name__ == '__main__':
    unittest.main()

