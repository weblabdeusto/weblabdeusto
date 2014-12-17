import threading
import wsgiref.simple_server
import urlparse
import SocketServer
from collections import OrderedDict

import voodoo.log as log
import voodoo.counter as counter
import weblab.configuration_doc as configuration_doc
from voodoo.resources_manager import CancelAndJoinResourceManager

_resource_manager = CancelAndJoinResourceManager("RemoteFacadeServer")

class WsgiApp(object):
    def __init__(self):
        pass

    def __call__(self, environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/plain')])
        yield 'Hello World\n'

class WsgiProxy(object):
    def __init__(self, ordered_routes = None):
        if ordered_routes:
            self.ordered_routes = ordered_routes
        else:
            self.ordered_routes = OrderedDict()

    def __setitem__(self, route, method):
        self.ordered_routes[route] = method

    def __call__(self, environ, start_response):
        TOKEN = 'weblab'
        path = environ['PATH_INFO']
        relative_path = path[path.find(TOKEN) + len(TOKEN):]

        for route in self.ordered_routes:
            if relative_path.startswith(route):
                return self.ordered_routes[route](environ, start_response)

        start_response('404 Not Found', [('Content-Type', 'text/plain')])
        return 'Path not found'

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

class WsgiHttpServer(SocketServer.ThreadingMixIn, wsgiref.simple_server.WSGIServer):
    daemon_threads      = True
    request_queue_size  = 50 #TODO: parameter!
    allow_reuse_address = True

    def __init__(self, script_name, server_address, handler_class, application):
        self.script_name = script_name
        wsgiref.simple_server.WSGIServer.__init__(self, server_address, handler_class)
        self.set_app(application)

    def setup_environ(self):
        wsgiref.simple_server.WSGIServer.setup_environ(self)
        self.base_environ['SCRIPT_NAME'] = self.script_name

    def get_request(self):
        sock, addr = wsgiref.simple_server.WSGIServer.get_request(self)
        sock.settimeout(None)
        return sock, addr

class ServerThread(threading.Thread):
    """server_foreve is a blocking method. This class runs it in a daemon thread."""
    def __init__(self, server, timeout):
        threading.Thread.__init__(self)
        self.setName(counter.next_name("MainRemoteFacadeServer"))
        self.setDaemon(True)

        self._server = server
        self._timeout = timeout

    def run(self):
        try:
            self._server.serve_forever(poll_interval = self._timeout)
        finally:
            _resource_manager.remove_resource(self)

class WebLabWsgiServer(object):
    def __init__(self, cfg_manager, application):
        the_server_route = cfg_manager.get_doc_value(configuration_doc.CORE_FACADE_SERVER_ROUTE)
        core_server_url  = cfg_manager.get_doc_value(configuration_doc.CORE_SERVER_URL)
        core_server_url_parsed = urlparse.urlparse(core_server_url)

        if core_server_url.startswith('http://') or core_server_url.startswith('https://'):
            the_location = core_server_url_parsed.path 
        else:
            the_location = '/weblab'

        class NewWsgiHttpHandler(WrappedWSGIRequestHandler):
            server_route   = the_server_route
            location       = the_location

        timeout = cfg_manager.get_doc_value(configuration_doc.FACADE_TIMEOUT)
        listen  = cfg_manager.get_doc_value(configuration_doc.CORE_FACADE_BIND)
        port    = cfg_manager.get_doc_value(configuration_doc.CORE_FACADE_PORT)

        script_name = core_server_url_parsed.path.split('/weblab')[0]
        self._server = WsgiHttpServer(script_name, (listen, port), NewWsgiHttpHandler, application)
        self._server.socket.settimeout(timeout)
        self._server_thread = ServerThread(self._server, timeout)

    def start(self):
        self._server_thread.start()
        _resource_manager.add_resource(self._server_thread)

    def cancel(self):
        self.stop()

    def stop(self):
        self._server.shutdown()
        self._server_thread.join()

