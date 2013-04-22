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

import os
import sys
import subprocess
import traceback
import BaseHTTPServer
APACHE_RELOADER_PORT = 1662

class RequestHandler (BaseHTTPServer.BaseHTTPRequestHandler):
    
    def do_GET (self):        
        try:
            # subprocess.Popen(['/etc/init.d/apache2', 'reload'], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
            os.system("/etc/init.d/apache2 reload")
            self.send_response(200)
            self.end_headers()
            self.wfile.write('Apache reloaded')
        except:
            traceback.print_exc()
            self.send_response(500)
            self.end_headers()
            self.wfile.write('Error: Apache not reloaded')
        return

if __name__ == "__main__":
    if os.getuid() != 0:
        print >> sys.stderr, "This script reloads apache automatically. It needs to be run as root."
        sys.exit(-1)
    httpd = BaseHTTPServer.HTTPServer(('127.0.0.1', APACHE_RELOADER_PORT), RequestHandler)
    print "Listening on port %s for HTTP requests (any request will reload apache)..." % APACHE_RELOADER_PORT
    httpd.serve_forever()
