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
# Author: Pablo Orduña <pablo@ordunya.com>
#
import unittest

import voodoo.gen.locator.ServerTypeHandler as ServerTypeHandler
import voodoo.gen.exceptions.locator.LocatorErrors as LocatorErrors

import test.unit.voodoo.gen.locator.ServerTypeSample as ServerTypeSample

class ServerTypeHandlerTestCase(unittest.TestCase):
    def test_exceptions(self):
        self.assertRaises(
            LocatorErrors.InvalidListOfMethodsError,
            ServerTypeHandler.ServerTypeHandler,
            ServerTypeSample,
            {
                #:-) and :-( are not a list of methods
                'Login' : ':-)',
                'Coordinator' : ':-('
            }
        )

#         self.assertRaises(
#             LocatorErrors.MoreServersThanExpectedError,
#             ServerTypeHandler.ServerTypeHandler,
#             ServerTypeSample,
#             {
#                 'Login' : ('method1','method2'),
#                 'Coordinator' : ('method1','method2'),
#                 'DoesntExist': ('method1','method2')
#             }
#         )
        server_type_handler = ServerTypeHandler.ServerTypeHandler(
                    ServerTypeSample,
                    {
                        'Login' : ('method1','method2'),
                        'Coordinator' : ('method3','method4')
                    }
                )
        self.assertRaises(
            LocatorErrors.NoSuchServerTypeFoundError,
            server_type_handler.retrieve_methods,
            ':-)'
        )


    def test_variables(self):
        server_type_handler = ServerTypeHandler.ServerTypeHandler(
                    ServerTypeSample,
                    {
                        'Login' : ('method1','method2'),
                        'Coordinator' : ('method3','method4')
                    }
                )
        self.assertEquals(server_type_handler.isMember(ServerTypeSample.Login),True)
        self.assertEquals(server_type_handler.isMember(5),False)

        self.assertEquals(
                server_type_handler.retrieve_methods('Login'),
                ('method1','method2')
            )
        self.assertEquals(
                server_type_handler.module,
                ServerTypeSample
            )


def suite():
    return unittest.makeSuite(ServerTypeHandlerTestCase)

if __name__ == '__main__':
    unittest.main()

