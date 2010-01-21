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
import pmock
import StringIO
import xmlrpclib

import weblab.experiment.Util     as ExperimentUtil
import webserver.fileUpload as fileUpload
import weblab.facade.RemoteFacadeManagerCodes as RFCodes

class MockRequest(object):
    def __init__(self, initial_dict):
        super(MockRequest,self).__init__()
        self.form = initial_dict

class MockForm(object):
    def __init__(self, f):
        super(MockForm,self).__init__()
        self.file = f

def extract_message(message):
    return message[message.find('<body>'):message.find('</body>')]

def extract_fault_code(message):
    message = extract_message(message)
    _, code, message = message.split('@')
    return code

def extract_fault_string(message):
    message = extract_message(message)
    _, code, message = message.split('@')
    return message

def extract_success_message(message):
    message = extract_message(message)
    _, message = message.split('@')
    return message

class FileUploadTestCase(unittest.TestCase):
    def setUp(self):
        self.file_content = "content of the file"
        self.serialized_file_content = ExperimentUtil.serialize(self.file_content)
        self.session_id   = fileUpload.SessionId('session_id')
        self.file_info    = 'program'
        f = StringIO.StringIO(self.file_content)
        mf = MockForm(f)
        self.req = MockRequest({
                fileUpload.SESSION_ID_ATTR : 'session_id',
                fileUpload.FILE_SENT_ATTR  : mf,
                fileUpload.FILE_INFO_ATTR  : self.file_info
            })
        self.req.headers_in = {"Cookie" : "foo1=bar1; weblabsessionid=anything.myroute; foo=bar"}

        self.old_create_weblab_client = fileUpload._create_weblab_client
        def fake_create_weblab_client(url, session_id):
            return self.weblab_client
        fileUpload._create_weblab_client = fake_create_weblab_client

    def test_wrong_attributes(self):
        initial_dict = {}
        req = MockRequest(initial_dict)

        message = fileUpload.index(req)
        fault_code = extract_fault_code(message)
        self.assertEquals(
                RFCodes.WEBLAB_GENERAL_EXCEPTION_CODE,
                fault_code
            )

    def test_index(self):
        return_message = "success!!!"
        return_value   = { "commandstring" : return_message }
        self.weblab_client = pmock.Mock()
        self.weblab_client.expects(pmock.at_least_once()).send_file(
                pmock.eq(self.session_id),
                pmock.eq(self.serialized_file_content),
                pmock.eq(self.file_info)
            ).will( pmock.return_value(return_value) )
        result = fileUpload.index(self.req)
        message = extract_success_message(result)
        self.assertTrue(return_message, message)

    def test_raise_exception(self):
        self.weblab_client = pmock.Mock()
        self.weblab_client.expects(pmock.at_least_once()).send_file(
                pmock.eq(self.session_id),
                pmock.eq(self.serialized_file_content),
                pmock.eq(self.file_info)
            ).will(
                pmock.raise_exception(
                    Exception('whatever')
                )
            )
        result = fileUpload.index(self.req)
        fault_code = extract_fault_code(result)
        fault_string = extract_fault_string(result)
        self.assertEquals(
                RFCodes.PYTHON_GENERAL_EXCEPTION_CODE,
                fault_code
            )
        self.assertEquals(
                'whatever',
                fault_string
            )

    def test_raise_xmlrpc_fault(self):
        self.weblab_client = pmock.Mock()
        self.weblab_client.expects(pmock.at_least_once()).send_file(
                pmock.eq(self.session_id),
                pmock.eq(self.serialized_file_content),
                pmock.eq(self.file_info)
            ).will(
                pmock.raise_exception( xmlrpclib.Fault( 'my code','whatever2' ) )
            )
        result = fileUpload.index(self.req)
        fault_code = extract_fault_code(result)
        fault_string = extract_fault_string(result)
        self.assertEquals(
                'my code',
                fault_code
            )
        self.assertEquals(
                'whatever2',
                fault_string
            )

    def tearDown(self):
        fileUpload._create_weblab_client = self.old_create_weblab_client

def suite():
    return unittest.makeSuite(FileUploadTestCase)

if __name__ == '__main__':
    unittest.main()

