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

import traceback
import types
import voodoo.log as log

from test.util.module_disposer import uses_module
import voodoo.gen.protocols.XMLRPC.ServerXMLRPC as ServerXMLRPC

PORT = 12345

class ServerXMLRPCTestCase(unittest.TestCase):

    @uses_module(ServerXMLRPC)
    def test_method(self):
        msg1 = "hello"
        msg2 = " world"
        exc_msg = "Haw haw! (with Nelson's voice)"
        methods = ('method1','method2')
        class Fake(object):
            def __init__(self):
                super(Fake, self).__init__()
                self._parent = self
            def do_method1(self,arg1):
                return arg1 + msg2
            def do_method2(self,arg1):
                raise ArithmeticError(exc_msg)
        fake = Fake()

        newfunctions = []
        for i in methods:
            method_values = {'METHOD_NAME' : i, 'SERIALIZE' : True}
            # We add them explicitly (even if not required) to avoid warnings of "unused import"
            new_globals = globals().copy()
            new_globals['log'] = log
            new_globals['types'] = types
            new_globals['traceback'] = traceback
            method_values.update(new_globals)
            method_values.update(locals())
            newfunction = ServerXMLRPC._generate_skeleton(i)
            newfunctions.append(newfunction)

        self.assertEquals(msg1 + msg2,newfunctions[0](fake,msg1))
        self.assertRaises(
                ArithmeticError,
                newfunctions[1],
                fake,
                msg1
            )

def suite():
    return unittest.makeSuite(ServerXMLRPCTestCase)

if __name__ == '__main__':
    unittest.main()

