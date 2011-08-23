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
import sys
import unittest

from test.util.optional_modules import OptionalModuleTestCase
import voodoo.gen.loader.schema_checker as SchemaChecker
import voodoo.gen.exceptions.loader.LoaderExceptions as LoaderExceptions

class WrappedSchemaChecker(SchemaChecker.SchemaChecker):
    def __init__(self, xml_content, xsd_content):
        self.__xml_content = xml_content
        self.__xsd_content = xsd_content
    def _read_xml_file(self, xmlfile):
        return self.__xml_content
    def _read_xsd_file(self, xsdfile):
        return self.__xsd_content

SAMPLE_XML_SCHEMA = """<?xml version="1.0"?>
    <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema" 
        elementFormDefault="qualified"
        >
        <xs:element name="root_element">
            <xs:complexType>
                <xs:sequence>
                    <xs:element name="element" type="xs:string"/>
                </xs:sequence>
            </xs:complexType>
        </xs:element>
    </xs:schema>"""
VALID_XML_CONTENT = """<?xml version="1.0"?>
    <root_element>
        <element>This is a valid XML</element>
    </root_element>"""

INVALID_WELL_FORMED_XML_CONTENT = """<?xml version="1.0"?>
    <whatever>
        <element>This is a well formed invalid XML</element>
    </whatever>"""

INVALID_XML_CONTENT = """This is not a well formed xml"""

class SchemaCheckerTestCase(unittest.TestCase):
    if SchemaChecker.LXML_AVAILABLE:
        def test_correct_check_schema(self):
            schema_checker = WrappedSchemaChecker(
                    VALID_XML_CONTENT,
                    SAMPLE_XML_SCHEMA
                )
            schema_checker.check_schema('whatever','whatever')
        def test_invalid_well_formed(self):
            schema_checker = WrappedSchemaChecker(
                    INVALID_WELL_FORMED_XML_CONTENT,
                    SAMPLE_XML_SCHEMA
                )
            self.assertRaises(
                LoaderExceptions.InvalidSyntaxFileConfigurationException,
                schema_checker.check_schema,
                'whatever',
                'whatever'
            )
        def test_invalid_xml(self):
            schema_checker = WrappedSchemaChecker(
                    INVALID_XML_CONTENT,
                    SAMPLE_XML_SCHEMA
                )
            self.assertRaises(
                LoaderExceptions.InvalidSyntaxFileConfigurationException,
                schema_checker.check_schema,
                'whatever',
                'whatever'
            )
    else:
        print >> sys.stderr, "SchemaChecker tests skipped since lxml is not available"

class LxmlNotAvailableTestCase(OptionalModuleTestCase):
    MODULE    = SchemaChecker
    ATTR_NAME = 'LXML_AVAILABLE'

    def test_lxml_not_available(self):
        def func():
            sc = SchemaChecker.SchemaChecker()
            sc.check_schema("foo","bar")

        self._test_func_without_module(func)

def suite():
    return unittest.TestSuite((
                        unittest.makeSuite(LxmlNotAvailableTestCase),
                        unittest.makeSuite(SchemaCheckerTestCase)
                    ))

if __name__ == '__main__':
    unittest.main()

