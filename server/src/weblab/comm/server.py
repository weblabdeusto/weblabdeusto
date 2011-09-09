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
# Author: Pablo Orduña <pablo@ordunya.com>
# 

import sys
import threading
import SocketServer

# ZSI
try:
    import ZSI.ServiceContainer as ServiceContainer
except ImportError:
    ZSI_AVAILABLE = False
else:
    ZSI_AVAILABLE = True

# JSON/HTTP
import BaseHTTPServer
import json

import datetime
import types

# XML-RPC
import SimpleXMLRPCServer

import voodoo.log as log
import voodoo.counter as counter
import voodoo.resources_manager as ResourceManager

import weblab.comm.manager as RemoteFacadeManager
from weblab.comm.context import get_context, create_context, delete_context
from weblab.comm.codes import WEBLAB_GENERAL_EXCEPTION_CODE
import weblab.comm.exc as FacadeExceptions
import voodoo.configuration as ConfigurationExceptions

RFS_TIMEOUT_NAME                      = 'facade_timeout'
DEFAULT_TIMEOUT                       = 0.5

_resource_manager = ResourceManager.CancelAndJoinResourceManager("RemoteFacadeServer")

def strdate(days=0,hours=0,minutes=0,seconds=0):
    return (datetime.datetime.utcnow() + datetime.timedelta(days=days,hours=hours,minutes=minutes,seconds=seconds)).strftime("%a, %d %b %Y %H:%M:%S GMT")

##################
# JSON/HTTP code #
##################

def simplify_response(response, limit = 10, counter = 0):
    """
    Recursively serializes the response into a JSON dictionary. Because the response object could actually
    contain cyclic references, we limit the maximum depth. 
    """
    if counter == limit:
        return None
    if isinstance(response, (basestring, int, long, float, bool)):
        return response
    if isinstance(response, (list, tuple)):
        new_response = []
        for i in response:
            new_response.append(simplify_response(i, limit, counter + 1,))
        return new_response
    if isinstance(response, dict):
        new_response = {}
        for i in response:
            new_response[i] = simplify_response(response[i], limit, counter + 1)
        return new_response
    if isinstance(response, (datetime.datetime, datetime.date, datetime.time)):
        return response.isoformat()
    ret = {}
    for attr in [ a for a in dir(response) if not a.startswith('_') ]:
        if not hasattr(response.__class__, attr):
            attr_value = getattr(response, attr)
            if not isinstance(attr_value, types.FunctionType) and not isinstance(attr_value, types.MethodType):
                ret[attr] = simplify_response(attr_value, limit, counter + 1)
    return ret


class JsonHttpHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    facade_manager = None
    server_route   = None

    def do_GET(self):
        methods = [ method for method in dir(self.facade_manager) if not method.startswith('_') ]
        methods_help = {}
        for method in methods:
            methods_help[method] = getattr(self.facade_manager, method).__doc__ or ''
        _show_help(self, "JSON", methods, methods_help)

    def do_POST(self):
        """
        This do_POST callback handles an HTTP request containing a JSON-encoded RPC request. 
        """
        create_context(self.server, self.headers)
        
        try:
            length = int(self.headers['content-length'])
            post_content = self.rfile.read(length)

            # The contents of the POST contain a string with the JSON-encoded request. Decode that string.
            try:
                decoded = json.loads(post_content)
            except ValueError:
                response = {"is_exception":True,"code":WEBLAB_GENERAL_EXCEPTION_CODE,"message":"Couldn't deserialize message"}
                self.finish_error(response)
                return

            # Retrieve the name of the method being invoked.
            method_name = decoded.get('method')
            if method_name is None:
                response = {"is_exception":True,"code":WEBLAB_GENERAL_EXCEPTION_CODE,"message":"Missing 'method' attr"}
                self.finish_error(response)
                return

            # Retrieve the parameters of the method being invoked. 
            params = decoded.get('params')
            if params is None:
                response = {"is_exception":True,"code":WEBLAB_GENERAL_EXCEPTION_CODE,"message":"Missing 'params' attr"}
                self.finish_error(response)
                return

            # Ensure that we actually have a facade manager, as we should.
            # (The method specified in the JSON request, which we are going to invoke, 
            # is actually located in the facade manager).
            if self.facade_manager is None:
                response = {"is_exception":True,"code":WEBLAB_GENERAL_EXCEPTION_CODE,"message":"Facade manager not set"}
                self.finish_error(response)
                return

            # Ensure that the method that is remotely being called does exist. 
            if not hasattr(self.facade_manager, method_name):
                response = {"is_exception":True,"code":WEBLAB_GENERAL_EXCEPTION_CODE,"message":"Method not recognized"}
                self.finish_error(response)
                return

            # Retrieve a reference to the method.
            method = getattr(self.facade_manager,method_name)

            # Build a standard dictionary with the parameters to call the actual method.
            newparams = {}
            try:
                for param in params:
                    newparams[str(param)] = params[param]
            except Exception as e:
                response = {"is_exception":True,"code":WEBLAB_GENERAL_EXCEPTION_CODE,"message":"unicode not accepted in param names"}
                self.finish_error(response)
                return

            # Call the method specified in the request, 
            # with the parameters from the dictionary we just built.
            try:
                return_value = method(**newparams)
            except RemoteFacadeManager.JSONException as jsone:
                response = jsone.args[0]
                self.finish_error(response)
                return
            except Exception as e:
                response = {"is_exception":True,"code":WEBLAB_GENERAL_EXCEPTION_CODE,"message":"Unexpected exception: %s" % e}
                self.finish_error(response)
                return

            # No exception was raised so the request was successful. We will now return the response to
            # the remote caller. 
            try:
                # Serialize the response to a JSON dictionary.
                parsed_return_value = simplify_response(return_value)
                response = json.dumps({"result":parsed_return_value, "is_exception" : False})
            except Exception as e:
                response = {"is_exception":True,"code":WEBLAB_GENERAL_EXCEPTION_CODE,"message":"Error encoding return value"}
                log.log( JsonHttpHandler, log.level.Error, "Request from %s: %s" % (get_context().get_ip_address(), "Error encoding return value: %s" % e))
                log.log( JsonHttpHandler, log.level.Error, "Message was: %s" % return_value)
                log.log_exc( JsonHttpHandler, log.level.Warning )
                self.finish_error(response)
                return
                
            self.finish_post(response)
        finally:
            delete_context()

    def finish_error(self, error):
        """
        Finishes a JSON POST request when an error occurred, reporting the result to the caller.
        @param error The error that occurred. It will be serialized to JSON.
        """
        self.finish_post(json.dumps(error))

    def finish_post(self, response):
        """
        Finishes a JSON POST request that was successful, reporting the result to the caller.
        @param response JSON-encoded response to the successfully executed JSON request.
        """
        self.send_response(200)
        self.send_header("Content-type", "text/xml")
        self.send_header("Content-length", str(len(response)))
        if self.server_route is not None:
            route = get_context().route
            if route is None:
                route = self.server_route
            self.send_header("Set-Cookie", "weblabsessionid=anythinglikeasessid.%s; path=/; Expires=%s" % (route, strdate(days=100)))
            self.send_header("Set-Cookie", "loginweblabsessionid=anythinglikeasessid.%s; path=/; Expires=%s" % (route, strdate(hours=1)))
        self.end_headers()
        self.wfile.write(response)
        self.wfile.flush()
        try:
            self.connection.shutdown(1)
        except:
            pass

    def log_message(self, format, *args):
        #args: ('POST /weblab/json/ HTTP/1.1', '200', '-')
        log.log(
            JsonHttpHandler,
            log.level.Info,
            "Request from %s: %s" % (get_context().get_ip_address(), format % args)
        )

class JsonHttpServer(SocketServer.ThreadingMixIn, BaseHTTPServer.HTTPServer):
    daemon_threads      = True
    request_queue_size  = 50 #TODO: parameter!
    allow_reuse_address = True

    def __init__(self, server_address, handler_class):
        BaseHTTPServer.HTTPServer.__init__(self, server_address, handler_class)

    def get_request(self):
        sock, addr = BaseHTTPServer.HTTPServer.get_request(self)
        sock.settimeout(None)
        return sock, addr

######################
# SMARTGWT/JSON code #
######################



################
# XML-RPC code #
################

class XmlRpcRequestHandler(SimpleXMLRPCServer.SimpleXMLRPCRequestHandler):

    rpc_paths    = ('/','/RPC2','/weblab/xmlrpc','/weblab/xmlrpc/', '/weblab/login/xmlrpc', '/weblab/login/xmlrpc/')
    server_route = None

    def do_GET(self):
        methods = self.server.system_listMethods()
        methods_help = {}
        for method in methods:
            methods_help[method] = self.server.system_methodHelp(method)
        _show_help(self, "XML-RPC", methods, methods_help)

    def do_POST(self, *args, **kwargs):
        create_context(self.server, self.headers)
        try:
            SimpleXMLRPCServer.SimpleXMLRPCRequestHandler.do_POST(self, *args, **kwargs)
        finally:
            delete_context()

    def end_headers(self):
        if self.server_route is not None:
            route = get_context().route
            if route is None:
                route = self.server_route
            self.send_header("Set-Cookie","weblabsessionid=anythinglikeasessid.%s; path=/" % route)
            self.send_header("Set-Cookie", "loginweblabsessionid=anythinglikeasessid.%s; path=/; Expires=%s" % (route, strdate(hours=1)))
        SimpleXMLRPCServer.SimpleXMLRPCRequestHandler.end_headers(self)

    def log_message(self, format, *args):
        #args: ('POST /weblab/xmlrpc/ HTTP/1.1', '200', '-')
        log.log(
            XmlRpcRequestHandler,
            log.level.Info,
            "Request from %s: %s" % (get_context().get_ip_address(), format % args)
        )

class XmlRpcServer(SocketServer.ThreadingMixIn, SimpleXMLRPCServer.SimpleXMLRPCServer):
    daemon_threads = True
    request_queue_size = 50 #TODO: parameter!
    allow_reuse_address = True
    
    def __init__(self, server_address, manager, the_server_route):
        class NewXmlRpcRequestHandler(XmlRpcRequestHandler):
            server_route = the_server_route
        
        SimpleXMLRPCServer.SimpleXMLRPCServer.__init__(self, server_address, NewXmlRpcRequestHandler, allow_none = True)
        self.register_instance(manager)

    def get_request(self):
        sock, addr = SimpleXMLRPCServer.SimpleXMLRPCServer.get_request(self)
        sock.settimeout(None)
        return sock, addr

############
# ZSI code #
############

if ZSI_AVAILABLE:
    class WebLabRequestHandlerClass(ServiceContainer.SOAPRequestHandler):
        server_route = None

        def do_POST(self, *args, **kwargs):
            create_context(self.server, self.headers)
            try:
                ServiceContainer.SOAPRequestHandler.do_POST(self, *args, **kwargs)
            finally:
                delete_context()

        def end_headers(self):
            if self.server_route is not None:
                route = get_context().route
                if route is None:
                    route = self.server_route
                self.send_header("Set-Cookie","weblabsessionid=anythinglikeasessid.%s; path=/" % route)
                self.send_header("Set-Cookie","loginweblabsessionid=anythinglikeasessid.%s; path=/; Expires=%s" % (route, strdate(hours=1)))
            ServiceContainer.SOAPRequestHandler.end_headers(self)

        def log_message(self, format, *args):
            #args: ('POST /weblab/soap/ HTTP/1.1', '200', '-')
            log.log(
                WebLabRequestHandlerClass,
                log.level.Info,
                "Request from %s: %s" % (get_context().get_ip_address(), format % args)
            )

    class _AvoidTimeoutServiceContainer(SocketServer.ThreadingMixIn, ServiceContainer.ServiceContainer):

        daemon_threads = True
        request_queue_size = 50 #TODO: parameter!
        allow_reuse_address = True

        def __init__(self, *args, **kargs):
            ServiceContainer.ServiceContainer.__init__(self, *args, **kargs)

        def get_request(self):
            sock, addr = ServiceContainer.ServiceContainer.get_request(self)
            sock.settimeout(None)
            return sock, addr

###############
# COMMON CODE #
###############

def _show_help(request_inst, protocol, methods, methods_help):
        response = """<html>
        <head>
            <title>WebLab-Deusto %s service</title>
        </head>
        <body>
            Welcome to the WebLab-Deusto service through %s. Available methods:
            <ul>
        """ % (protocol, protocol)

        for method in methods:
            response += """<li><b>%s</b>: %s</li>\n""" % (method, methods_help[method])
        
        response += """</ul>
        </body>
        </html>
        """
        request_inst.send_response(200)
        request_inst.send_header("Content-type", "text/html")
        request_inst.send_header("Content-length", str(len(response)))
        request_inst.end_headers()
        request_inst.wfile.write(response)
        request_inst.wfile.flush()
        try:
            request_inst.connection.shutdown(1)
        except:
            pass

class AbstractProtocolRemoteFacadeServer(threading.Thread):
    protocol_name = 'FILL_ME!' # For instance: zsi

    def __init__(self, server, configuration_manager, remote_facade_server):
        threading.Thread.__init__(self)
        self.setName(counter.next_name("RemoteFacadeServer_" + self.protocol_name))
        self.setDaemon(True)
        self._configuration_manager = configuration_manager
        self._stopped               = False
        self._rfm                   = getattr(remote_facade_server,'_create_%s_remote_facade_manager' % self.protocol_name)(
                            server,
                            configuration_manager
                        )
        self._rfs                   = remote_facade_server

    def run(self):
        try:
            while not self._rfs._get_stopped():
                self._server.handle_request()
            self._server = None
        finally:
            _resource_manager.remove_resource(self)

    def get_timeout(self):
        return self._configuration_manager.get_value(RFS_TIMEOUT_NAME, DEFAULT_TIMEOUT)

    def parse_configuration(self, *args, **kargs):
        try:
            return self._configuration_manager.get_values(*args, **kargs)
        except ConfigurationExceptions.ConfigurationException as ce:
            raise FacadeExceptions.MisconfiguredException("Missing params: " + ce.args[0])

class AbstractRemoteFacadeServerZSI(AbstractProtocolRemoteFacadeServer):
    protocol_name = "zsi"

    def _retrieve_configuration(self):
        values = self.parse_configuration(
                self._rfs.FACADE_ZSI_PORT,
                **{
                    self._rfs.FACADE_ZSI_LISTEN: self._rfs.DEFAULT_FACADE_ZSI_LISTEN,
                    self._rfs.FACADE_ZSI_SERVICE_NAME: self._rfs.DEFAULT_FACADE_ZSI_SERVICE_NAME
                } 
           )
        listen       = getattr(values, self._rfs.FACADE_ZSI_LISTEN)
        port         = getattr(values, self._rfs.FACADE_ZSI_PORT)
        service_name = getattr(values, self._rfs.FACADE_ZSI_SERVICE_NAME)
        return listen, port, service_name

    def _create_service_container(self, listen, port, the_server_route):

        class NewWebLabRequestHandlerClass(WebLabRequestHandlerClass):
            server_route = the_server_route

        return _AvoidTimeoutServiceContainer(
                (listen,port), 
                RequestHandlerClass=NewWebLabRequestHandlerClass
            )

    def initialize(self):
        if not ZSI_AVAILABLE:
            msg = "The optional library 'ZSI' is not available, so the server will not support SOAP clients. However, it's being used so problems will arise." 
            print >> sys.stderr, msg
            log.log( self, log.level.Error, msg)

        listen, port, service_name = self._retrieve_configuration()
        self._interface = self.WebLabDeusto(impl = self._rfm)
        server_route = self._configuration_manager.get_value( self._rfs.FACADE_SERVER_ROUTE, self._rfs.DEFAULT_SERVER_ROUTE )
        self._server = self._create_service_container(listen,port,server_route)
        self._server.server_name = self._configuration_manager.get_value( self._rfs.FACADE_ZSI_PUBLIC_SERVER_HOST, self._rfs.DEFAULT_FACADE_ZSI_PUBLIC_SERVER_HOST )
        self._server.server_port = self._configuration_manager.get_value( self._rfs.FACADE_ZSI_PUBLIC_SERVER_PORT, self._rfs.DEFAULT_FACADE_ZSI_PUBLIC_SERVER_PORT )
        self._server.setNode(self._interface, url=service_name)

        timeout = self.get_timeout()
        self._server.socket.settimeout(timeout)

class RemoteFacadeServerJSON(AbstractProtocolRemoteFacadeServer):
    protocol_name = "json"

    JSON_HANDLER = JsonHttpHandler

    def _retrieve_configuration(self):
        values = self.parse_configuration(
                self._rfs.FACADE_JSON_PORT,
                **{
                    self._rfs.FACADE_JSON_LISTEN: self._rfs.DEFAULT_FACADE_JSON_LISTEN
                } 
           )
        listen = getattr(values, self._rfs.FACADE_JSON_LISTEN)
        port   = getattr(values, self._rfs.FACADE_JSON_PORT)
        return listen, port

    def initialize(self):
        listen, port = self._retrieve_configuration()
        the_server_route = self._configuration_manager.get_value( self._rfs.FACADE_SERVER_ROUTE, self._rfs.DEFAULT_SERVER_ROUTE )
        timeout = self.get_timeout()
        class NewJsonHttpHandler(self.JSON_HANDLER):
            facade_manager = self._rfm
            server_route   = the_server_route
        self._server = JsonHttpServer((listen, port), NewJsonHttpHandler)
        self._server.socket.settimeout(timeout)

class RemoteFacadeServerXMLRPC(AbstractProtocolRemoteFacadeServer):
    protocol_name = "xmlrpc"

    def _retrieve_configuration(self):
        values = self.parse_configuration(
                self._rfs.FACADE_XMLRPC_PORT,
                **{
                    self._rfs.FACADE_XMLRPC_LISTEN: self._rfs.DEFAULT_FACADE_XMLRPC_LISTEN
                } 
           )
        listen = getattr(values, self._rfs.FACADE_XMLRPC_LISTEN)
        port   = getattr(values, self._rfs.FACADE_XMLRPC_PORT)
        return listen, port

    def initialize(self):
        timeout = self.get_timeout()
        listen, port = self._retrieve_configuration()
        server_route = self._configuration_manager.get_value( self._rfs.FACADE_SERVER_ROUTE, self._rfs.DEFAULT_SERVER_ROUTE )
        self._server = XmlRpcServer((listen, port), self._rfm, server_route)
        self._server.socket.settimeout(timeout)


class AbstractRemoteFacadeServer(object):
    SERVERS = (RemoteFacadeServerJSON, RemoteFacadeServerXMLRPC)

    def __init__(self, server, configuration_manager):
        self._configuration_manager = configuration_manager
        self._stopped               = False
        self._stop_lock             = threading.Lock()

        self._servers               = []

        for ServerClass in self.SERVERS:
            self._servers.append(
                    ServerClass(server, configuration_manager, self)
                )

    def start(self):
        for server in self._servers:
            server.initialize()

        # And, if all of them are correctly configured...
        for server in self._servers:
            server.start()
            _resource_manager.add_resource(server)

    def cancel(self):
        # Used by the _resource_manager
        self.stop()

    def _get_stopped(self):
        self._stop_lock.acquire()
        try:
            return self._stopped
        finally:
            self._stop_lock.release()

    def stop(self):
        self._stop_lock.acquire()
        try:
            self._stopped = True
        finally:
            self._stop_lock.release()

        for server in self._servers:
            server.join()

