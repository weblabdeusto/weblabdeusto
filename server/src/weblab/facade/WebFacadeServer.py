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

import urllib
import SocketServer
import BaseHTTPServer

import weblab.facade.RemoteFacadeServer as RFS
from weblab.facade.RemoteFacadeServer import strdate

from weblab.facade.RemoteFacadeContext import get_context, create_context, delete_context

import voodoo.log as log

class MethodException(Exception):
    def __init__(self, status, msg):
        super(MethodException, self).__init__((status, msg))
        self.status = status
        self.msg    = msg

class Method(object):

    path = ""

    def __init__(self, request_handler, cfg_manager):
        self.request_handler = request_handler
        self.cfg_manager     = cfg_manager

    def run(self):
        return "Hello world"

    def raise_exc(self, status, message):
        raise MethodException(status, message)

    def get_context(self):
        return get_context()

    @classmethod
    def matches(klass, path):
        return path == klass.path

class NotFoundMethod(Method):
    def run(self):
        self.raise_exc(404, "Path %s not found!" % urllib.quote(self.request_handler.path))

class WebHttpHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    methods        = None
    server_route   = None
    cfg_manager    = None

    def do_GET(self):
        create_context(self.server, self.headers)
        try:
            for method in self.methods:
                if method.matches(self.path):
                    m = method(self, self.cfg_manager)
                    message = m.run()
                    self._write(200, message)
            NotFoundMethod(self, self.cfg_manager).run()
        except MethodException, e:
            log.log( self, log.LogLevel.Error, str(e))
            log.log_exc( self, log.LogLevel.Warning)
            self._write(e.status, e.msg)
        except Exception, e:
            import traceback
            traceback.print_exc()

            log.log( self, log.LogLevel.Error, str(e))
            log.log_exc( self, log.LogLevel.Warning)
            self._write(500, 'Error in server. Contact administrator')
        finally:
            delete_context()

    def _write(self, status, response):
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-length", str(len(response)))
        if self.server_route is not None:
            route = get_context().route
            if route is None:
                route = self.server_route
            self.send_header("Set-Cookie", "weblabsessionid=anythinglikeasessid.%s; path=/" % route)
            self.send_header("Set-Cookie", "loginweblabsessionid=anythinglikeasessid.%s; path=/; Expires=%s" % (route, strdate(hours=1)))

        self.end_headers()
        self.wfile.write(response)
        self.wfile.flush()
        try:
            self.connection.shutdown(1)
        except:
            pass

    def log_message(self, format, *args):
        #args: ('POST /foo/bar/ HTTP/1.1', '200', '-')
        log.log(
            WebHttpHandler,
            log.LogLevel.Info,
            "Request from %s: %s" % (get_context().get_ip_address(), format % args)
        )

class WebHttpServer(SocketServer.ThreadingMixIn, BaseHTTPServer.HTTPServer):
    daemon_threads      = True
    request_queue_size  = 50 #TODO: parameter!
    allow_reuse_address = True

    def __init__(self, server_address, server_methods, route, configuration_manager):
        class NewWebHttpHandler(WebHttpHandler):
            methods      = server_methods
            server_route = route
            cfg_manager  = configuration_manager
        BaseHTTPServer.HTTPServer.__init__(self, server_address, NewWebHttpHandler)

    def get_request(self):
        sock, addr = BaseHTTPServer.HTTPServer.get_request(self)
        sock.settimeout(None)
        return sock, addr

class WebProtocolRemoteFacadeServer(RFS.AbstractProtocolRemoteFacadeServer):
    protocol_name = 'web'
    METHODS       = []

    def _retrieve_configuration(self):
        values = self.parse_configuration(
                self._rfs.FACADE_WEB_PORT,
                **{
                    self._rfs.FACADE_WEB_LISTEN: self._rfs.DEFAULT_FACADE_WEB_LISTEN
                } 
           )
        listen = getattr(values, self._rfs.FACADE_WEB_LISTEN)
        port   = getattr(values, self._rfs.FACADE_WEB_PORT)
        return listen, port

    def initialize(self):
        listen, port = self._retrieve_configuration()
        the_server_route = self._configuration_manager.get_value( self._rfs.FACADE_SERVER_ROUTE, self._rfs.DEFAULT_SERVER_ROUTE )
        timeout = self.get_timeout()
        self._server = WebHttpServer((listen, port), self.METHODS, the_server_route, self._configuration_manager)
        self._server.socket.settimeout(timeout)

class WebRemoteFacadeServer(RFS.AbstractRemoteFacadeServer):
    SERVERS = ()
    def _create_web_remote_facade_manager(self, server, cfg_manager):
        pass

