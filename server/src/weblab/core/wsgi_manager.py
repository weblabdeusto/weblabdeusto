from __future__ import print_function, unicode_literals
import sys
import threading
import wsgiref.simple_server
import urlparse

from six.moves import socketserver

import voodoo.log as log
import voodoo.counter as counter
import weblab.configuration_doc as configuration_doc
from voodoo.resources_manager import CancelAndJoinResourceManager, is_testing

_resource_manager = CancelAndJoinResourceManager("RemoteFacadeServer")

class WsgiApp(object):
    def __init__(self):
        pass

    def __call__(self, environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/plain')])
        yield 'Hello World\n'

class WrappedWSGIRequestHandler(wsgiref.simple_server.WSGIRequestHandler):

    def get_environ(self):
        env = wsgiref.simple_server.WSGIRequestHandler.get_environ(self)
        script_name = self.server.script_name
        if script_name and env['PATH_INFO'].startswith(script_name):
            env['PATH_INFO'] = env['PATH_INFO'].split(script_name,1)[1]
        return env

    def log_message(self, format, *args):
        #args: ('POST /weblab/json/ HTTP/1.1', '200', '-')
        log.log(
            WrappedWSGIRequestHandler,
            log.level.Info,
            "Request: %s" %  (format % args)
        )

class WsgiHttpServer(socketserver.ThreadingMixIn, wsgiref.simple_server.WSGIServer):
    daemon_threads      = True
    request_queue_size  = 50 #TODO: parameter!
    allow_reuse_address = True

    def __init__(self, script_name, server_address, handler_class, application, timeout):
        self.script_name = script_name
        wsgiref.simple_server.WSGIServer.__init__(self, server_address, handler_class)
        self.set_app(application)
        self.socket.settimeout(timeout)

    def setup_environ(self):
        wsgiref.simple_server.WSGIServer.setup_environ(self)
        self.base_environ['SCRIPT_NAME'] = self.script_name

    def get_request(self):
        sock, addr = wsgiref.simple_server.WSGIServer.get_request(self)
        sock.settimeout(None)
        return sock, addr

class ServerThread(threading.Thread):
    """server_foreve is a blocking method. This class runs it in a daemon thread."""
    def __init__(self, server_creator, timeout, wsgi_server):
        threading.Thread.__init__(self)
        self.setName(counter.next_name("MainRemoteFacadeServer"))
        self.setDaemon(True)

        self._server_creator = server_creator
        self._timeout = timeout
        self._wsgi_server = wsgi_server

    def run(self):
        server = self._server_creator()
        self._wsgi_server.core_server = server
        try:
            server.serve_forever(poll_interval = self._timeout)
        finally:
            _resource_manager.remove_resource(self)

class WebLabWsgiServer(object):
    def __init__(self, config, application):
        the_server_route = config[configuration_doc.CORE_FACADE_SERVER_ROUTE]
        core_server_url  = config[configuration_doc.CORE_SERVER_URL]
        core_server_url_parsed = urlparse.urlparse(core_server_url)

        if core_server_url.startswith('http://') or core_server_url.startswith('https://'):
            the_location = core_server_url_parsed.path 
        else:
            the_location = '/weblab'

        class NewWsgiHttpHandler(WrappedWSGIRequestHandler):
            server_route   = the_server_route
            location       = the_location

        script_name = core_server_url_parsed.path.split('/weblab')[0]
        timeout = config[configuration_doc.FACADE_TIMEOUT]

        listen  = config[configuration_doc.CORE_FACADE_BIND]
        port    = config[configuration_doc.CORE_FACADE_PORT]

        self.core_server = None
        if config.get_value('flask_debug', False):
            if not is_testing():
                print("Using a different server (relying on Flask rather than on Python's WsgiHttpServer)", file=sys.stderr)

            self.core_server_thread = threading.Thread(target = application.run, kwargs = { 'port' : port, 'debug' : True, 'use_reloader' : False })
        else:
            server_creator = lambda : WsgiHttpServer(script_name, (listen, port), NewWsgiHttpHandler, application, timeout)
            self.core_server_thread = ServerThread(server_creator, timeout, self)

    def start(self):
        self.core_server_thread.start()
        _resource_manager.add_resource(self.core_server_thread)

    def cancel(self):
        self.stop()

    def stop(self):
        if self.core_server is not None:
            self.core_server.shutdown()
            self.core_server.socket.close()

        self.core_server_thread.join()

