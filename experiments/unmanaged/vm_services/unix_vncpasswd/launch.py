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
#		  Luis Rodríguez <luis.rodriguez@opendeusto.es>
# 

####################################################
#
# This script must be run as root in a UNIX system.
# Any call to http://(this-host):PORT/?sessionid=foo
# Will cause the current user to have foo as a Vino 
# password. This is useful for sharing the session
# with the user through SSH or other systems based
# on the systems password.
# 

PORT        = 18080
PASSWD_PATH = "/usr/bin/vino-passwd"

####################################################

import pexpect
import time
import urllib
import traceback
import BaseHTTPServer

def change_password(new_passwd):
    passwd = pexpect.spawn("%s" % (PASSWD_PATH))
	
    # wait for password: to come out of passwd's stdout
    passwd.expect("password: ")
    # send pass to passwd's stdin
    passwd.sendline(new_passwd)
    
    time.sleep(0.1)
    
    passwd.expect("password: ")
    passwd.sendline(new_passwd)
	
    time.sleep(0.1)
	
    #passwd.expect(" (y/n)?")
    #passwd.sendline("n");
    
    #time.sleep(0.1)

class Handler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(self):
        _, query_args = urllib.splitquery(self.path)
        arguments = dict([ urllib.splitvalue(query_arg) for query_arg in query_args.split('&') ])
        session_id = arguments.get('sessionid')

        if session_id is None:
            self.send_error(400)
            self.end_headers()
            self.wfile.write("fail: sessionid argument is required")
        else:
            try:
                change_password(session_id)
            except Exception, e:
                traceback.print_exc()
                self.send_error(500)
                self.end_headers()
                self.wfile.write("Internal error: %s" % str(e))
            else:
                self.send_response(200)
                self.end_headers()
                self.wfile.write("ok")
        self.wfile.close()

server = BaseHTTPServer.HTTPServer(('',PORT), RequestHandlerClass = Handler)
server.serve_forever()

