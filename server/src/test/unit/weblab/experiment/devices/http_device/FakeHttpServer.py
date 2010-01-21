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
 
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from threading import Thread, RLock
import socket
import time

TIMEOUT = 0.05

class _AvoidTimeoutHTTPServer(HTTPServer):
    def __init__(self, *args, **kargs):
        HTTPServer.__init__(self, *args, **kargs)
    def get_request(self):
        sock, addr = HTTPServer.get_request(self)
        sock.settimeout(None)
        return sock, addr


class FakeHttpServer(Thread):
    
    DEFAULT_RESPONSE = "text of the response"
    
    def __init__(self, port):
        Thread.__init__(self)
        
        class FakeHttpHandler(BaseHTTPRequestHandler):
            answer = 200
            
            def __init__(self, *args, **kargs):
                BaseHTTPRequestHandler.__init__(self, *args, **kargs)

            def do_POST(self):
                self.rfile.read(int(self.headers['Content-Length']))
                self.send_response(self.answer)
                self.end_headers()
                self.wfile.write(FakeHttpServer.DEFAULT_RESPONSE)

            def log_message(self, *args, **kargs):
                pass
                        
        self.running = True
        self.request_handler = FakeHttpHandler
        self.server = _AvoidTimeoutHTTPServer( ('', port), FakeHttpHandler )
        self.server.socket.settimeout(TIMEOUT)

        self.handling_lock = RLock()
        self.handling = False

    def wait_until_handling(self):
        # Improve this with threading.Event / threading.Condition
        n = 50
        while n > 0:
            self.handling_lock.acquire()
            try:
                if self.handling:
                    return
            finally:
                self.handling_lock.release()
            n -= 1
            time.sleep(TIMEOUT)
        raise Exception("Still waiting for the http server to handle requests...")

    def run(self):
        self.handling_lock.acquire()
        try:
            self.handling = True
        finally:
            self.handling_lock.release()

        try:
            while self.running:
                try:
                    self.server.handle_request()
                except socket.timeout:
                    pass
        except:
            pass

    def stop(self):
        self.running = False
        self.server.socket.close()
        
    def set_answer(self, code):
        self.request_handler.answer = code

