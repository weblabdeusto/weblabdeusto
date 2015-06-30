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

import sys
import unittest

import weblab.admin.bot.data   as Data
import weblab.admin.bot.user   as User

class DataTestCase(unittest.TestCase):
    def test_botexception(self):
        botexc = Data.BotError((Exception("foo"), "foobar"), 2,4,6)
        self.assertTrue(repr(botexc).find('instances') > 0)

    def test_botiteration(self):
        botexc  = Data.BotError((Exception("foo"), "foobar"), 2,4,6)
        botuser = User.StandardBotUser({"JSON":("http://foo","http://foo/login")},"JSON","user","passwd","exp_name","cat_name","bar", 0.05)
        botit   = Data.BotIteration(100, [botexc], [botuser], "stdout", "stderr")
        self.assertTrue(repr(botit).find('botusers') > 0)

    def test_bottrial(self):
        botexc  = Data.BotError((Exception("foo"), "foobar"), 2,4,6)
        botuser = User.StandardBotUser({"JSON": ("http://foo", "http://foo/login")},"JSON","user","passwd","exp_name","cat_name","bar", 0.05)
        botit   = Data.BotIteration(100, {"Exception":botexc}, [botuser], "stdout", "stderr")

        bottri  = Data.BotTrial([botit])
        self.assertTrue(repr(bottri).find('iterations') > 0)

#    def test_dto(self):
#        import voodoo.mapper as mapper
#
#        client = Client.Bot(url="http://localhost/weblab/soap/")
#        binding = client.ws.binding
#
#        dto = mapper.dto_generator(binding)
#        obj = mapper.load_from_dto(dto)

if Data.NUMPY_AVAILABLE:
    def suite():
        return unittest.makeSuite(DataTestCase)
else:
    print("numpy not available. Disabling weblab.admin.bot tests.", file=sys.stderr)

def suite():
    return unittest.makeSuite(DataTestCase)

if __name__ == '__main__':
    unittest.main()

