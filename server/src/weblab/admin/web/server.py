
import urlparse
import SocketServer
import wsgiref.simple_server

from flask import redirect

if __name__ == '__main__':
    import sys
    sys.path.insert(0, '.')

from weblab.admin.web.app import AdministrationApplication

import voodoo.log as log

import weblab.comm.server as abstract_server


#####################################################################################
# 
# TODO: All this code below depends on the old and deprecated communication system of 
# WebLab-Deusto, which should be refactored to be less complex.
# 

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

class RemoteFacadeServerWSGI(abstract_server.AbstractProtocolRemoteFacadeServer):
    
    protocol_name = "wsgi"

    WSGI_HANDLER = WrappedWSGIRequestHandler

    def _retrieve_configuration(self):
        values = self.parse_configuration(
                self._rfs.FACADE_WSGI_PORT,
                **{
                    self._rfs.FACADE_WSGI_LISTEN: self._rfs.DEFAULT_FACADE_WSGI_LISTEN
                }
           )
        listen = getattr(values, self._rfs.FACADE_WSGI_LISTEN)
        port   = getattr(values, self._rfs.FACADE_WSGI_PORT)
        return listen, port

    def initialize(self):
        listen, port = self._retrieve_configuration()
        the_server_route = self._configuration_manager.get_value( self._rfs.FACADE_SERVER_ROUTE, self._rfs.DEFAULT_SERVER_ROUTE )
        core_server_url  = self._configuration_manager.get_value( 'core_server_url', '' )
        if core_server_url.startswith('http://') or core_server_url.startswith('https://'):
            without_protocol = '//'.join(core_server_url.split('//')[1:])
            the_location = '/' + ( '/'.join(without_protocol.split('/')[1:]) )
        else:
            the_location = '/weblab'
        timeout = self.get_timeout()

        class NewWsgiHttpHandler(self.WSGI_HANDLER):
            server_route   = the_server_route
            location       = the_location

        script_name = urlparse.urlparse(core_server_url).path.split('/weblab')[0]
        self._server = WsgiHttpServer(script_name, (listen, port), NewWsgiHttpHandler, self._rfm)
        self._server.socket.settimeout(timeout)

ADMIN_FACADE_JSON_LISTEN                    = 'admin_facade_json_bind'
DEFAULT_ADMIN_FACADE_JSON_LISTEN            = ''
ADMIN_FACADE_JSON_PORT                      = 'admin_facade_json_port'

from weblab.core.comm.user_server import USER_PROCESSING_FACADE_SERVER_ROUTE, DEFAULT_USER_PROCESSING_SERVER_ROUTE

class AdminRemoteFacadeServer(abstract_server.AbstractRemoteFacadeServer):
    SERVERS = (RemoteFacadeServerWSGI,)

    FACADE_WSGI_PORT             = ADMIN_FACADE_JSON_PORT
    FACADE_WSGI_LISTEN           = ADMIN_FACADE_JSON_LISTEN
    DEFAULT_FACADE_WSGI_LISTEN   = DEFAULT_ADMIN_FACADE_JSON_LISTEN

    FACADE_SERVER_ROUTE          = USER_PROCESSING_FACADE_SERVER_ROUTE
    DEFAULT_SERVER_ROUTE         = DEFAULT_USER_PROCESSING_SERVER_ROUTE

    def _create_wsgi_remote_facade_manager(self, server, configuration_manager):
        self.application = AdministrationApplication(configuration_manager, server)
        return self.application.app

#############################################
# 
# The code below is only used for testing
# 

if __name__ == '__main__':
    from voodoo.configuration import ConfigurationManager
    from weblab.core.server import UserProcessingServer
    cfg_manager = ConfigurationManager()
    cfg_manager.append_path('test/unit/configuration.py')

    ups = UserProcessingServer(None, None, cfg_manager, dont_start = True)

    DEBUG = True
    admin_app = AdministrationApplication(cfg_manager, ups, bypass_authz = True)

    @admin_app.app.route('/')
    def index():
        return redirect('/weblab/administration/admin')

    admin_app.app.run(debug=True, host = '0.0.0.0')

