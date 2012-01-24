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
#         Luis Rodriguez <luis.rodriguez@opendeusto.es>
# 

from weblab.comm.codes import WEBLAB_GENERAL_EXCEPTION_CODE, PYTHON_GENERAL_EXCEPTION_CODE
from voodoo.sessions.session_id import SessionId
import weblab.comm.web_server as WebFacadeServer
import weblab.experiment.util as Util

import os
import re
import mimetypes

FILE_SENT = 'file_sent'
FILE_INFO = 'file_info'
SESSION_ID = 'session_id'
IS_ASYNC = 'is_async'


VISIR_LOCATION = "C:/shared/weblab-hg/weblabdeusto/client/war/weblabclient/visir/"

BASE_HTML_TEMPLATE="""<?xml version="1.0"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html>
    <head>
        <title>WebLab visir</title>
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



class  VisirMethod(WebFacadeServer.Method):
    path = '/visir/'

    def run(self):
        """
        run()
        This will redirect every request to serve the VISIR files.
        """
        
        file = re.sub(r"(/weblab/web/visir/)(.*)", VISIR_LOCATION + r"\2", self.uri, 1)
        
        f = open(file, "rb")
        content = f.read(-1)
        
        # TODO: Ensure that this is actually done only once.
        mimetypes.init()
        mimetype = mimetypes.guess_type(file)[0]
        if mimetype is None:
            mimetype = "application/octet-stream"
        
        self.set_content_type(mimetype)
        
        return content
        
        return SUCCESS_HTML_TEMPLATE % {
                    'RESULT' : self.uri + " | " + os.getcwd() + " | " + file + " | " + self.get_content_type()
                }


class VisirException(Exception):
    pass

