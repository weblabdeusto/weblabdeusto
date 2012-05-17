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

import tempfile
import traceback
from voodoo.log import logged
from weblab.data.command import Command
from voodoo.sessions.session_id import SessionId
# To convert from HTTP date to standard time
import email.utils as eut
import time

import os
import mimetypes

import hashlib
import weblab

import re

VISIR_RELATIVE_PATH = os.sep.join(('..','..','..','client','war','weblabclient','visir')) + os.sep

VISIR_LOCATION = os.path.abspath(os.sep.join((os.path.dirname(weblab.__file__), VISIR_RELATIVE_PATH))) + os.sep
VISIR_TEMP_FILES = os.sep.join((VISIR_LOCATION, 'temp')) + os.sep

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

DEBUG = False

class UploadExtractor(object):
    """
    Utility class for being able to easily extract parts from multipart
    HTTP requests. There seem to be some issues with the standard cgi library
    alternatives which limit their usage.
    """
    
    def __init__(self, data, boundary):
        """
        Initializes the UploadExtractor object.
        @param data Contents of the multipart POST, from which the files will be
        extracted.
        @param boundary Boundary delimiting each part, as specified by the Content-type
        header.
        @return A (headers, filedata) tuple. Headers is a dictionary containing the
        headers of the part. Filedata is the actual content of that part.
        """
        self.data = data
        self.boundary = boundary
        self._index = 0 # To indicate how far we have parsed into the string.
    
    def extract_file(self):
        """
        Extracts the next file from the stream. Returns None if no more
        files are present.
        """
        ind_start = self.data.find(self.boundary, self._index)
        if ind_start == -1:
            return None
        # We take into account the new-line characters.
        ind_start += len(self.boundary) + 2
        ind_end = self.data.find(self.boundary, ind_start)
        ind_end -= 2
        rawdata = self.data[ind_start:ind_end-2]
        self._index = ind_end
        
        # rawdata now contains the headers and content of each part.
        # Extract the headers off it.
        headers_end = rawdata.find("\r\n\r\n")
        if headers_end == -1:
            return None
        
        # Use a regex to extract the headers.
        headers = dict(re.findall(r"(?P<name>.*?): (?P<value>.*?)\r\n", rawdata[0:headers_end+2]))
        
        # Separate the data from the headers
        filedata = rawdata[headers_end+4 :]
        
    
        return headers, filedata



class  VisirMethod(WebFacadeServer.Method):
    path = '/visir/'
    mimetypes_loaded = False

    @logged()
    def run(self):
        """
        run()
        This will redirect every request to serve the VISIR files.
        """
        
        # Just deny any request with an URL containing .. to prevent security issues
        if ".." in self.uri:
            self.set_status(403)
            if DEBUG: print "Forbidden"
            return "403 Forbidden: The URI should not contain .."
        
        # Find out the location of the file. 
        fileonly = self.uri.split('/web/visir/')[1]
        
        fname = VISIR_LOCATION + fileonly

        if DEBUG: print "Loading %s..." % fname,
        
        if not os.path.abspath(fname).startswith(VISIR_LOCATION):
            self.set_status(403)
            if DEBUG: print "Forbidden"
            return "403 Forbidden: The URI tried to go outside the scope of VISIR"

               
        # Intercept the save request
        if fileonly == "save":
            content = self.intercept_save()
            if DEBUG: print "Intercepted %s" % len(content)
            return content
        
        if fileonly == "store_temporary.php":
            content = self.intercept_store()
            if DEBUG: print "Intercepted %s" % len(content)
            return content

        if fileonly.startswith("temp/"):
            content = self.intercept_temp(fileonly[len('temp/'):])
            if DEBUG: print "Intercepted %s" % len(content)
            return content
        
        # We did not intercept the request, we will just serve the file.
        
        # We will need to report the Last-Modified date. Otherwise the browser
        # won't send if-modified-since.
        # Getmtime returns a localtime, so we also convert it to gmt. Also, we want
        # a timestamp and not a tuple.
        if os.path.exists(fname):
            mod_time = time.mktime(time.gmtime(os.path.getmtime(fname)))
            if fileonly != "breadboard/library.xml":
                self.add_other_header("Last-Modified", self.time_to_http_date(mod_time))
            else:
                mod_time = None
        else:
            mod_time = None
        
        # Client already has a version of the file. Check whether
        # ours is newer. 
        if self.if_modified_since is not None:
            since_time = self.http_date_to_time(self.if_modified_since)
            
            # The file was not modified. Report as such.
            if mod_time is not None and mod_time <= since_time:
                self.set_status(304)
                if DEBUG: print "Not modified"
                return "304 Not Modified"
        
        try:
            with open(fname, "rb") as f:
                content = f.read()
        except:
            self.set_status(404)
            if DEBUG: print "Not found"
            return "404 Not found"
        
        if not VisirMethod.mimetypes_loaded:
            mimetypes.init()
            VisirMethod.mimetypes_loaded = True

        
        # Use the file path to guess the mimetype
        mimetype = mimetypes.guess_type(fname)[0]
        if mimetype is None:
            mimetype = "application/octet-stream"
        
        self.set_content_type(mimetype)
        
        if fileonly == "breadboard/library.xml":
            content = self.intercept_library(content, mimetype)
            if DEBUG: print "Intercepted %s; md5: %s" % (len(content), hashlib.new("md5", content).hexdigest())
            return content

        
        if DEBUG: print "Returning %s bytes" % len(content)
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
        cookies = self.req.headers.getheader('cookie')
        
        sess_id = None
        reservation_id = None
        for cur_cookie in (cookies or '').split('; '):
            if cur_cookie.startswith("weblabsessionid="):
                sess_id = SessionId('.'.join(cur_cookie[len('weblabsessionid='):].split('.')[:-1]))
            if cur_cookie.startswith('weblab_reservation_id='):
                reservation_id = SessionId(cur_cookie[len('weblab_reservation_id='):].split('.')[0])

        try:
            response = self.server.send_command( sess_id, Command("GIVE_ME_LIBRARY") )
        except:
            pass
        else:
            if response.commandstring is not None and response.commandstring != 'failed':
                return response.commandstring

        if reservation_id is None and sess_id is not None:
            try:
                reservation_id_str = self.server.get_reservation_id_by_session_id(sess_id)
                if reservation_id_str is not None:
                    reservation_id = SessionId(reservation_id_str)
            except:
                traceback.print_exc()
                reservation_id = None

        if reservation_id is not None:
            try:
                response = self.server.send_command( reservation_id, Command("GIVE_ME_LIBRARY") )
            except:
                failed = True
                traceback.print_exc()
            else:
                failed = response.commandstring is None or response.commandstring == 'failed'
        else:
            print "Can not request library since reservation_id is None"
            failed = True

        if failed:
            return content
        else:
            return response.commandstring
    
    def intercept_store(self):
        ctype = self.req.headers.gettype()
        boundary = self.req.headers.getparam("boundary")
        length = int(self.req.headers.getheader('content-length'))
        data = self.req.rfile.read(length)
        
        if ctype != "multipart/form-data":
            return "Unexpected mimetype"
        
        extractor = UploadExtractor(data, boundary)
        
        partheaders, filename = extractor.extract_file() #@UnusedVariable
        partheaders, filedata = extractor.extract_file() #@UnusedVariable
        
        if not os.path.exists(VISIR_TEMP_FILES):
            os.makedirs(VISIR_TEMP_FILES)
        fd, name = tempfile.mkstemp(suffix='.cir.tmp', prefix='weblab_visir_', dir=VISIR_TEMP_FILES)
        os.close(fd)

        fo = file(name, "wb")
        fo.write(filedata)
        fo.close()

        self.set_content_type("text/xml")
        
        return "<result><filename>%s</filename></result>" % os.path.basename(name)

    def intercept_temp(self, fileonly):
        # Avoid weird characters, .., etc.
        filename = os.path.basename(fileonly)
        full_filename = os.sep.join((VISIR_TEMP_FILES, filename))
        if not os.path.exists(full_filename):
            self.set_status(404)
            if DEBUG: print "Not found"
            return "404: Temporal file not found"

        content = open(full_filename, 'rb').read()
        self.set_content_type("text/xml")
        return content


class VisirException(Exception):
    pass




    

## TODO: Make this a real test.
#f = file("c:/tmp/out.txt", "r")
#f.readline()
#data = f.read()        
#boundary = """------------KM7gL6cH2KM7Ij5GI3ae0ei4ei4gL6"""
#u = UploadExtractor(data, boundary)
#
#print "DATA:  \n", u.extract_file()
#print "DATA:  \n", u.extract_file()
#print "DATA:  \n", u.extract_file()
#print "DATA:  \n", u.extract_file()

