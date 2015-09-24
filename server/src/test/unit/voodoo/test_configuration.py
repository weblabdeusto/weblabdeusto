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
from __future__ import print_function, unicode_literals

import os
import os.path as path
import tempfile
import unittest


import voodoo.configuration as ConfigurationManager
import voodoo.configuration as ConfigurationErrors

module1_code = """
mynumber = 5
mystr = "hello world"
"""

module2_code = """
mynumber = 6
mystr = "bye world"
"""

class ConfigurationManagerTestCase(unittest.TestCase):
    def _create_module(self):
        fd, file_name = tempfile.mkstemp(prefix="conf_",suffix=".py",dir='.')
        os.write(fd, module1_code)
        os.close(fd)
        return file_name
    def _refill_module(self, file_name):
        # Few times, reference counters rock
        os.remove(file_name)
        os.remove(file_name + 'c')
        open(file_name,'w').write(module2_code)

    def test_simple_module(self):
        module_name = self._create_module()
        confManager = ConfigurationManager.ConfigurationManager()
        the_module_name = path.basename(module_name)[:-3] # .py
        the_module = __import__(the_module_name)
        confManager.append_modules((the_module,))

        self.assertEquals(
            confManager.get_value('mynumber'),
            5
        )

        self.assertEquals(
            confManager.get_value('mystr'),
            "hello world"
        )
        os.remove(module_name)
        os.remove(module_name + 'c')

    def test_simple_path(self):
        module_name = self._create_module()
        confManager = ConfigurationManager.ConfigurationManager()
        confManager.append_paths((module_name,))

        self.assertEquals(
            confManager.get_value('mynumber'),
            5
        )

        self.assertEquals(
            confManager.get_value('mystr'),
            "hello world"
        )
        os.remove(module_name)

    def test_general(self):
        module_name = self._create_module()
        confManager = ConfigurationManager.ConfigurationManager()
        the_module_name = path.basename(module_name)[:-3] # .py
        the_module = __import__(the_module_name)
        confManager.append_modules((the_module,))

        #
        # Without a provided default value
        #
        self.assertEquals( confManager.get_value('mynumber'), 5)

        self.assertEquals( confManager.get_value('mystr'), "hello world")

        self._refill_module(module_name)

        confManager.reload()

        self.assertEquals( confManager.get_value('mynumber'), 6)

        self.assertEquals( confManager.get_value('mystr'), "bye world")

        self.assertRaises( ConfigurationErrors.KeyNotFoundError, confManager.get_value, 'not_found')

        #
        # With a provided default value
        #
        self.assertEquals( 'expected_value', confManager.get_value('not_found','expected_value'))

        self.assertRaises( ConfigurationErrors.NotAModuleError, confManager.append_modules, 'os')

        os.remove(module_name)
        os.remove(module_name + 'c')
        confManager.reload()

    def test_get_values(self):
        module_name = self._create_module()
        confManager = ConfigurationManager.ConfigurationManager()
        the_module_name = path.basename(module_name)[:-3] # .py
        the_module = __import__(the_module_name)
        confManager.append_modules((the_module,))

        #
        # Without a provided default value
        #
        self.assertRaises(
            ConfigurationErrors.KeysNotFoundError,
            confManager.get_values,
            'this.does.not.exist', 'this.neither'
        )

        values = confManager.get_values('mynumber','mystr')
        self.assertEquals(
            values.mynumber,
            5
        )

        self.assertEquals(
            values.mystr,
            "hello world"
        )

        #
        # With a provided default value
        #

        # 1st way: As a known key in the source code
        values = confManager.get_values(not_found='expected_value')
        self.assertEquals(
            'expected_value',
            values.not_found
        )

        # 2nd way: As an unknown key in the source code
        values = confManager.get_values( **{"not_found": 'expected_value'})
        self.assertEquals(
            'expected_value',
            getattr(values, "not_found")
        )

        os.remove(module_name)
        os.remove(module_name + 'c')

def suite():
    return unittest.makeSuite(ConfigurationManagerTestCase)

if __name__ == '__main__':
    unittest.main()

