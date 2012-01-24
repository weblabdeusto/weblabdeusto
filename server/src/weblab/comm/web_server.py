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

import cgi
import urllib
import SocketServer
import BaseHTTPServer

import weblab.comm.server as RFS
from weblab.comm.server import strdate

from weblab.comm.context import get_context, create_context, delete_context

import voodoo.log as log

class MethodException(Exception):
    def __init__(self, status, msg):
        super(MethodException, self).__init__((status, msg))
        self.status = status
        self.msg    = msg

class RequestManagedException(Exception):
    pass

class Method(object):

    path = ""

    def __init__(self, request_handler, cfg_manager, server):
        self.req         = request_handler
        self.cfg_manager = cfg_manager
        self.server      = server
        self.post_read   = False

    def run(self):
        return "Method %s does not implement run method!" % self.__class__.__name__

    def get_argument(self, name, default_value = None, avoid_post = False):
        for arg_name, value in self.get_arguments():
            if arg_name == name:
                return value
        if not avoid_post:
            self.read_post_arguments()
            postvar = self.postvars.get(name, None)
            if postvar is None:
                return default_value
            if len(postvar) == 0:
                return default_value
            return postvar[0]
        return default_value

    def get_status(self):
        return 200

    def get_other_cookies(self):
        return []

    def get_content_type(self):
        return "text/html"

    def get_GET_argument(self, name, default_value = None):
        for arg_name, value in self.get_arguments():
            if arg_name == name:
                return value
        return default_value

    def get_POST_argument(self, name, default_value = None):
        self.read_post_arguments()
        postvar = self.postvars.get(name, None)
        if postvar is None or len(postvar) == 0:
            return default_value
        return postvar[0]

    def get_arguments(self):
        if self.relative_path.find('?') < 0:
            return []
        query = self.relative_path[self.relative_path.find('?') + 1:]
        return [ (arg[:arg.find('=')], arg[arg.find('=')+1:]) for arg in query.split('&') if arg.find('=') > 0]


    def raise_exc(self, status, message):
        raise MethodException(status, message)

    def get_context(self):
        return get_context()

    @property
    def relative_path(self):
        return Method.get_relative_path(self.req.path)

    @property
    def weblab_cookie(self):
        return self.req.weblab_cookie

    @property
    def uri(self):
        return self.req.path.split('?')[0]

    @property
    def method(self):
        return self.req.command

    def read_post_arguments(self):
        if self.post_read:
            return # Already read
        self.post_read = True
        if self.method == 'POST':
            ctype, pdict = cgi.parse_header(self.req.headers.getheader('content-type'))
            if ctype == 'multipart/form-data':
                self.postvars = cgi.parse_multipart(self.req.rfile, pdict)
            elif ctype == 'application/x-www-form-urlencoded':
                length = int(self.req.headers.getheader('content-length'))
                self.postvars = cgi.parse_qs(self.req.rfile.read(length), keep_blank_values=1)
            else:
                self.postvars = {}
        else:
            self.postvars = {}

    @staticmethod
    def get_relative_path(path):
        # If coming from /weblab001/web/login/?foo=bar will return
        # /login/?foo=bar
        # 
        # If coming from /foo/?bar will return
        # /foo/?bar
        finder = '/web/'
        if path.find(finder) >= 0:
            return path[path.find(finder) + len(finder) - 1:]
        return path

    @classmethod
    def matches(klass, absolute_path):
        relative_path = Method.get_relative_path(absolute_path)
        return relative_path.startswith(klass.path)

    @classmethod
    def initialize(klass, cfg_manager, route):
        pass # Not required

class NotFoundMethod(Method):
    def run(self):
        self.raise_exc(404, "Path %s not found!" % urllib.quote(self.req.path))

class WebHttpHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    methods         = None
    server_route    = None
    cfg_manager     = None
    original_server = None

    def do_GET(self):
        self.weblab_cookie = None
        for current_cookie in (self.headers.getheader('cookie') or '').split('; '):
            if current_cookie.startswith('weblabsessionid'):
                self.weblab_cookie = current_cookie

        if self.weblab_cookie is None:
            if self.server_route is not None:
                route = self.server_route
                self.weblab_cookie = "weblabsessionid=anythinglikeasessid.%s" % route
            else:
                self.weblab_cookie = "weblabsessionid=sessid.not.found"

        create_context(self.server, self.headers)
        try:
            for method in self.methods:
                if method.matches(self.path):
                    m = method(self, self.cfg_manager, self.original_server)
                    message = m.run()
                    self._write(m.get_status(), m.get_content_type(), m.get_other_cookies(), message)
                    break
            else:
                NotFoundMethod(self, self.cfg_manager, self.original_server).run()
        except RequestManagedException as e:
            return
        except MethodException as e:
            log.log( self, log.level.Error, str(e))
            log.log_exc( self, log.level.Warning)
            self._write(e.status, 'text/html', [], e.msg)
        except Exception as e:
            import traceback
            traceback.print_exc()

            log.log( self, log.level.Error, str(e))
            log.log_exc( self, log.level.Warning)
            self._write(500, 'text/html', [], 'Error in server. Contact administrator')
        finally:
            delete_context()

    do_POST = do_GET

    def _write(self, status, content_type, other_cookies, response):
        self.send_response(status)
        self.send_header("Content-type", content_type)
        self.send_header("Content-length", str(len(response)))
        if self.server_route is not None:
            route = get_context().route
            if route is None:
                route = self.server_route
            self.send_header("Set-Cookie", "%s; path=/" % self.weblab_cookie)
            self.send_header("Set-Cookie", "loginweblabsessionid=anythinglikeasessid.%s; path=/; Expires=%s" % (route, strdate(hours=1)))
            for cookie in other_cookies:
                self.send_header("Set-Cookie", cookie)

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
            log.level.Info,
            "Request from %s: %s" % (get_context().get_ip_address(), format % args)
        )

class WebHttpServer(SocketServer.ThreadingMixIn, BaseHTTPServer.HTTPServer):
    daemon_threads      = True
    request_queue_size  = 50 #TODO: parameter!
    allow_reuse_address = True

    def __init__(self, server_address, server_methods, route, configuration_manager, server):
        class NewWebHttpHandler(WebHttpHandler):
            methods         = server_methods
            server_route    = route
            cfg_manager     = configuration_manager
            original_server = server
        BaseHTTPServer.HTTPServer.__init__(self, server_address, NewWebHttpHandler)
        for method in server_methods:
            method.initialize(configuration_manager, route)

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
        server = self._rfm
        self._server = WebHttpServer((listen, port), self.METHODS, the_server_route, self._configuration_manager, server)
        self._server.socket.settimeout(timeout)

class WebRemoteFacadeServer(RFS.AbstractRemoteFacadeServer):
    SERVERS = ()
    def _create_web_remote_facade_manager(self, server, cfg_manager):
        return server

