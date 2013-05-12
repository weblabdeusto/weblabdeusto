
import urlparse
import SocketServer
import wsgiref.simple_server

if __name__ == '__main__':
    import sys
    sys.path.insert(0, '.')

from weblab.login.comm.app import LoginApp

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

WEB_FACADE_LISTEN                    = 'login_web_facade_bind'
DEFAULT_WEB_FACADE_LISTEN            = ''

WEB_FACADE_PORT                      = 'login_web_facade_port'

from weblab.login.comm.server import LOGIN_FACADE_SERVER_ROUTE, DEFAULT_LOGIN_SERVER_ROUTE

class LoginWsgiRemoteFacadeServer(abstract_server.AbstractRemoteFacadeServer):
    SERVERS = (RemoteFacadeServerWSGI,)

    FACADE_WSGI_PORT             = WEB_FACADE_PORT
    FACADE_WSGI_LISTEN           = WEB_FACADE_LISTEN
    DEFAULT_FACADE_WSGI_LISTEN   = DEFAULT_WEB_FACADE_LISTEN

    FACADE_SERVER_ROUTE          = LOGIN_FACADE_SERVER_ROUTE
    DEFAULT_SERVER_ROUTE         = DEFAULT_LOGIN_SERVER_ROUTE

    def _create_wsgi_remote_facade_manager(self, server, configuration_manager):
        self.application = LoginApp(configuration_manager, server)
        return self.application

#############################################
# 
# The code below is only used for testing
# 

if __name__ == '__main__':
    from voodoo.configuration import ConfigurationManager
    from weblab.login.server import LoginServer
    cfg_manager = ConfigurationManager()
    cfg_manager.append_path('test/unit/configuration.py')

    ls = LoginServer(None, None, cfg_manager, dont_start = True)

    DEBUG = True
    login_app = LoginApp(cfg_manager, ls, bypass_authz = True)
    login_app.run(debug=True, host = '0.0.0.0')

