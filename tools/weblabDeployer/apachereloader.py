# -*- coding: utf-8 -*-
#
# Copyright (C) 2012 onwards University of Deusto
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#
# This software consists of contributions made by many individuals,
# listed below:
#
# Author: Xabier Larrakoetxea <xabier.larrakoetxea@deusto.es>
# Author: Pablo Orduña <pablo.orduna@deusto.es>
#
# These authors would like to acknowledge the Spanish Ministry of science
# and innovation, for the support in the project IPT-2011-1558-430000
# "mCloud: http://innovacion.grupogesfor.com/web/mcloud"
#


import sys
import subprocess
import BaseHTTPServer

PORT = 22110

class RequestHandler (BaseHTTPServer.BaseHTTPRequestHandler):
    
    def do_GET (self):
        
        try:
            subprocess.Popen(['/etc/init.d/apache2', 'reload'],
                    stdout = subprocess.PIPE, stderr = subprocess.PIPE)
            self.send_response(200)
            self.end_headers()
            self.wfile.write('Apache reloaded')
        except:
            self.send_response(500)
            self.end_headers()
            self.wfile.write('Error: Apache not reloaded')
        return

if __name__ == "__main__":
    httpd = BaseHTTPServer.HTTPServer(('127.0.0.1', PORT), RequestHandler)
    httpd.serve_forever()