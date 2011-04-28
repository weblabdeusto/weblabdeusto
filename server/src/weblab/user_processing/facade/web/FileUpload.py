#!/usr/bin/env python
#-*-*- encoding: utf-8 -*-*-
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

from weblab.facade.RemoteFacadeManagerCodes import WEBLAB_GENERAL_EXCEPTION_CODE, PYTHON_GENERAL_EXCEPTION_CODE
from voodoo.sessions.SessionId import SessionId
import weblab.facade.WebFacadeServer as WebFacadeServer
import weblab.experiment.Util as Util

FILE_SENT = 'file_sent'
FILE_INFO = 'file_info'
SESSION_ID = 'session_id'

BASE_HTML_TEMPLATE="""<?xml version="1.0"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html>
    <head>
        <title>WebLab upload</title>
    </head>
    <body>%(MESSAGE)s</body>
</html>
"""

SUCCESS_HTML_TEMPLATE = BASE_HTML_TEMPLATE % {
		"MESSAGE" : "SUCCESS@%(RESULT)s"
	}

FAULT_HTML_TEMPLATE = BASE_HTML_TEMPLATE % {
		"MESSAGE" : "ERROR@%(THE_FAULT_CODE)s@%(THE_FAULT_MESSAGE)s"
	}

class FileUploadMethod(WebFacadeServer.Method):
    path = '/upload/'

    def run(self):
        try:
            file_info, file_sent, session_id = self._check_arguments()
            file_content = Util.serialize(file_sent)
            sid = SessionId(session_id)
            result = self.server.send_file(sid, file_content, file_info)
        except FileUploadException, fue:
            code, message = fue.args
            return FAULT_HTML_TEMPLATE % {
                        'THE_FAULT_CODE' : code,
                        'THE_FAULT_MESSAGE' : message
                    }
        except Exception, e:
            message = e.args[0]
            return FAULT_HTML_TEMPLATE % {
                        'THE_FAULT_CODE' : PYTHON_GENERAL_EXCEPTION_CODE,
                        'THE_FAULT_MESSAGE' : message
                    }
        else:
            return SUCCESS_HTML_TEMPLATE % {
                        'RESULT' : result.commandstring
                    }

    def _check_arguments(self):
        file_info = self.get_argument(FILE_INFO)
        if file_info is None:
            raise FileUploadException(WEBLAB_GENERAL_EXCEPTION_CODE, "%s argument not provided!" % FILE_INFO)
        file_sent = self.get_argument(FILE_SENT)
        if file_sent is None:
            raise FileUploadException(WEBLAB_GENERAL_EXCEPTION_CODE, "%s argument not provided!" % FILE_SENT)
        session_id = self.get_argument(SESSION_ID)
        if session_id is None:
            raise FileUploadException(WEBLAB_GENERAL_EXCEPTION_CODE, "%s argument not provided!" % SESSION_ID)
        return file_info, file_sent, session_id 

class FileUploadException(Exception):
    pass

