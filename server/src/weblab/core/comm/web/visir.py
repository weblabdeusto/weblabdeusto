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

import weblab.comm.web_server as WebFacadeServer
__builtins__

# To convert from HTTP date to standard time
import email.utils as eut
import time

import os
import mimetypes

import weblab

VISIR_RELATIVE_PATH = os.sep.join(('..','..','..','client','war','weblabclient','visir')) + os.sep

VISIR_LOCATION = os.path.abspath(os.sep.join((os.path.dirname(weblab.__file__), VISIR_RELATIVE_PATH))) + os.sep

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
        fileonly = self.uri.split('/web/visir/')[1]
        
        file = VISIR_LOCATION + fileonly
        
        if not os.path.abspath(file).startswith(VISIR_LOCATION):
            return FAULT_HTML_TEMPLATE % { 
                                          'THE_FAULT_CODE' : "Invalid URI",  
                                          'THE_FAULT_MESSAGE' : "The URI tried to go outside the scope of VISIR" }

               
        # Intercept the save request
        if fileonly == "save":
            return self.intercept_save()
        
        
        # We did not intercept the request, we will just serve the file.
        
        # We will need to report the Last-Modified date. Otherwise the browser
        # won't send if-modified-since.
        # Getmtime returns a localtime, so we also convert it to gmt. Also, we want
        # a timestamp and not a tuple.
        mod_time = time.mktime(time.gmtime(os.path.getmtime(file)))
        self.add_other_header("Last-Modified", self.time_to_http_date(mod_time))
        
        # Client already has a version of the file. Check whether
        # ours is newer. 
        if self.if_modified_since is not None:
            since_time = self.http_date_to_time(self.if_modified_since)
            
            # The file was not modified. Report as such.
            if mod_time <= since_time:
                self.set_status(304)
                return "304 Not Modified"
        
        try:
            with open(file, "rb") as f:
                content = f.read()
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
    

    def http_date_to_time(self, datestr, want_gmt = True):
        """
        http_date_to_time(datestr)
        Converts an HTTP date string to a localtime timestamp.
        
        @param datestr HTTP date string, generally GMT, which is specified in the
        string itself
        
        @param want_gmt If True (the default) then the timestamp returned will be GMT.
        Otherwise, it will be localtime.
        
        @return Timestamp which corresponds to the specified date. It will be the GMT
        timestamp if want_gmt is set to true (the default), false otherwise.
        """
        t = time.mktime(eut.parsedate(datestr))
        if want_gmt: return time.gmtime(t)
        else: return t
    
    def time_to_http_date(self, tm):
        """
        time_to_http_date(tm)
        Converts a timestamp to an http date string. 
        @param tm The timestamp to convert to an http date. The timestamp should
        represent the GMT time.
        """
        return eut.formatdate(
            timeval     = tm,
            localtime   = False,
            usegmt      = True
        )

    def intercept_save(self):
        save = self.get_argument("save", "", False)
        self.set_content_type("application/download")
        self.add_other_header("Content-Disposition", "attachment; filename=circuit.cir")
        return save

    def intercept_library(self, content, mimetype):
        return content

class VisirException(Exception):
    pass

