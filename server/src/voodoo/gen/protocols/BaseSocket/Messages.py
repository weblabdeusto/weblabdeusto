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
# Author: Jaime Irurzun <jaime.irurzun@gmail.com>
#

import voodoo.mapper as mapper

import cPickle
import base64

class FunctionCall(object):

    def __init__(self, name, *args, **kargs):
        super(FunctionCall, self).__init__()
        self.name = name
        self.args = args
        self.kargs = kargs

    def __repr__(self):
        result = self.name+"( "
        for a in self.args:
            result += a + ", "
        for k in self.kargs:
            result += k
        return result + " )"

class FunctionResult(object):

    def __init__(self):
        super(FunctionResult, self).__init__()

class FunctionResultOK(FunctionResult):

    def __init__(self, result):
        super(FunctionResultOK, self).__init__()
        self.result = result

    def answer(self):
        return self.result

class FunctionResultNotFound(FunctionResult):

    def __init__(self):
        super(FunctionResultNotFound, self).__init__()

    def answer(self):
        raise Exception("Requested function does not exist")

class FunctionResultError(FunctionResult):

    def __init__(self, exception):
        super(FunctionResultError, self).__init__()
        self.exception = exception

    def answer(self):
        raise self.exception

class MessageFormatter(object):

    def __init__(self):
        super(MessageFormatter, self).__init__()

    def _data2message(self, data):
        encoded_data = base64.encodestring(data)
        message_length = str(len(encoded_data)).zfill(10)
        message = '%(MESSAGE_LENGTH)s%(PAYLOAD)s\n' % {
            'MESSAGE_LENGTH' : message_length,
            'PAYLOAD'        : encoded_data
        }
        return message

    def pack_call(self, name, *args, **kargs):
        call = FunctionCall(name, *args, **kargs)
        call_dto = mapper.dto_generator(call)
        data = cPickle.dumps(call_dto)
        message = self._data2message(data)
        return message

    def pack_result(self, result):
        result_dto = mapper.dto_generator(result)
        data = cPickle.dumps(result_dto)
        message = self._data2message(data)
        return message

    def unpack_call(self, data):
        encoded_data = data[10:-1]
        decoded_data = base64.decodestring(encoded_data)
        call_dto = cPickle.loads(decoded_data)
        call = mapper.load_from_dto(call_dto)
        if not isinstance(call, FunctionCall):
            pass # TODO: raise something
        return call

    def unpack_result(self, data):
        encoded_data = data[10:-1]
        decoded_data = base64.decodestring(encoded_data)
        result_dto = cPickle.loads(decoded_data)
        result = mapper.load_from_dto(result_dto)
        if not isinstance(result, FunctionResult):
            pass #TODO: raise an exception or something
        return result
