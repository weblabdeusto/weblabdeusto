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
import os
import unittest

import xml.dom.minidom as minidom
import StringIO
import voodoo.gen.loader.util as LoaderUtilities
import voodoo.gen.exceptions.loader.LoaderExceptions as LoaderExceptions

class LoaderUtilitiesTestCase(unittest.TestCase):
    def test_obtain_text(self):
        xml_text = """<?xml version="1.0" encoding="UTF-8"?>
        <some_node>the text</some_node>
        """
        xml_file = StringIO.StringIO(xml_text)
        xml_doc  = minidom.parse(xml_file)
        xml_node = xml_doc.childNodes[0]
        self.assertEquals(
                "the text",
                LoaderUtilities.obtain_text(xml_node)
            )

    def test_obtain_text_empty(self):
        xml_text = """<?xml version="1.0" encoding="UTF-8"?>
        <some_node />
        """
        xml_file = StringIO.StringIO(xml_text)
        xml_doc  = minidom.parse(xml_file)
        xml_node = xml_doc.childNodes[0]
        self.assertEquals(
                None,
                LoaderUtilities.obtain_text(xml_node)
            )

    def test_find_node_success(self):
        sample = """<?xml version="1.0" encoding="utf-8"?>
            <server></server>
            """
        root_node = minidom.parse(StringIO.StringIO(sample))
        result = LoaderUtilities.find_node("file_name",root_node, "server")
        self.assertEquals('server', result.tagName)

    def test_find_node_not_found(self):
        sample = """<?xml version="1.0" encoding="utf-8"?>
            <server></server>
            """
        root_node = minidom.parse(StringIO.StringIO(sample))
        self.assertRaises(
            LoaderExceptions.InvalidSyntaxFileConfigurationException,
            LoaderUtilities.find_node,
            "file_name",
            root_node,
            "server2"
        )

    def test_find_node_too_many(self):
        sample = """<?xml version="1.0" encoding="utf-8"?>
            <server>
                <configuration/>
                <configuration/>
            </server>
            """
        root_node = minidom.parse(StringIO.StringIO(sample))
        server_node = LoaderUtilities.find_node('file_name',root_node,'server')
        self.assertRaises(
            LoaderExceptions.InvalidSyntaxFileConfigurationException,
            LoaderUtilities.find_node,
            "file_name",
            server_node,
            "configuration"
        )

    def test_find_nodes_zero_nodes(self):
        sample = """<?xml version="1.0" encoding="utf-8"?>
            <server></server>
            """

        root_node = minidom.parse(StringIO.StringIO(sample))
        nodes = LoaderUtilities.find_nodes(
                'file_name',root_node,'server2'
            )
        self.assertEquals(0, len(nodes))

    def test_find_nodes_at_least_one_not_found(self):
        sample = """<?xml version="1.0" encoding="utf-8"?>
            <server></server>
            """
        root_node = minidom.parse(StringIO.StringIO(sample))
        self.assertRaises(
            LoaderExceptions.InvalidSyntaxFileConfigurationException,
            LoaderUtilities.find_nodes_at_least_one,
            "file_name",
            root_node,
            "server2"
        )

    def test_last_point(self):
        self.assertEquals(LoaderUtilities.last_point('os.path.sep'),'os.path')
        self.assertEquals(LoaderUtilities.last_point('os.path'),'os')
        self.assertEquals(LoaderUtilities.last_point('os'),'')

    def test_obtain_module(self):
        self.assertEquals(
                os,
                LoaderUtilities.obtain_module('os.path.sep')
            )
        self.assertEquals(
                os,
                LoaderUtilities.obtain_module('os.path')
            )
        self.assertEquals(
                None,
                LoaderUtilities.obtain_module('I guess this does not exist')
            )

    def test_obtain_from_python_path(self):
        self.assertEquals(
                os.path.sep,
                LoaderUtilities.obtain_from_python_path('os.path.sep')
            )
        self.assertEquals(
                os.open,
                LoaderUtilities.obtain_from_python_path('os.open')
            )
        self.assertEquals(
                os.path,
                LoaderUtilities.obtain_from_python_path('os.path')
            )
        self.assertRaises(
                LoaderExceptions.InvalidConfigurationException,
                LoaderUtilities.obtain_from_python_path,
                'I guess this does not exist'
            )
        self.assertRaises(
                LoaderExceptions.InvalidConfigurationException,
                LoaderUtilities.obtain_from_python_path,
                'os.path.thisdoesnt'
            )

def suite():
    return unittest.makeSuite(LoaderUtilitiesTestCase)

if __name__ == '__main__':
    unittest.main()


