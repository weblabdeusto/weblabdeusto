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
        
        # Just deny any request with an URL containing .. to prevent security issues
        if ".." in self.uri:
            return FAULT_HTML_TEMPLATE % { 
                                          'THE_FAULT_CODE' : "Invalid URI",  
                                          'THE_FAULT_MESSAGE' : "The URI should not contain .." }
        
        
        # Find out the location of the file. 
        fileonly = re.sub(r"(/weblab/web/visir/)(.*)", r"\2", self.uri, 1)
        file = VISIR_LOCATION + fileonly
        
                
        # Intercept the save request
        if fileonly == "save":
            return self.intercept_save()
        
        try:
            f = open(file, "rb")
            content = f.read(-1)
        except:
            return FAULT_HTML_TEMPLATE % { 
                              'THE_FAULT_CODE' : "404",  
                              'THE_FAULT_MESSAGE' : "File not found (or not readable)" }
        
        # TODO: Ensure that this is actually done only once.
        mimetypes.init()

        
        # Use the file path to guess the mimetype
        mimetype = mimetypes.guess_type(file)[0]
        if mimetype is None:
            mimetype = "application/octet-stream"
        
        self.set_content_type(mimetype)
        
        if fileonly == "breadboard/library.xml":
            return self.intercept_library(content, mimetype)
        
        return content

    def intercept_save(self):
        save = self.get_argument("save", "", False)
        self.set_content_type("text/html")
        self.add_other_header("Content-Disposition", "attachment; filename=\"circuit.cir\"")
        return save

    def intercept_library(self, content, mimetype):
        return content
        #self.set_content_type("text/html")
        #return "INTERCEPTING LIBRARY XML"

class VisirException(Exception):
    pass

