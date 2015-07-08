
from gevent import pywsgi
import gevent
import time
import xmlrpclib
import urllib2
import sys
from util import _get_type_name


class LabListener(object):
    """
    Class that will listen on a port for a labserver-initiated XMLRPC connection, and which will
    receive the commands themselves. It will essentially have the same interface as an ExperimentServer.
    """

    def __init__(self, listen_host, listen_port):
        super(LabListener, self).__init__()
        self.listen_host = listen_host
        self.listen_port = listen_port
        self.server = pywsgi.WSGIServer((self.listen_host, self.listen_port), self.on_http_request)

        # For now we will not use a method registry because we will just forward any method.
        self.methods_registry = {
        }

    def on_http_request(self, environ, start_response):
        if environ['REQUEST_METHOD'] == 'GET':
            start_response('200', [('Content-Type', 'text/html')])
            return ["This server accepts ExperimentServer-like methods"]

        input = environ.get('wsgi.input')
        raw_data = input.read()
        params, method_name = xmlrpclib.loads(raw_data)
        if method_name.startswith('Util.'):
            method_name = method_name[len('Util.'):]

        # We do not check that the method exists here.
        # if method_name not in self.methods_list:
        #     start_response('404', [('Content-Type', 'text/html')])
        #     return [xmlrpclib.dumps(xmlrpclib.Fault("Method not found", "Method not found"))]

        try:
            if method_name == 'test_bridge':
                result = params[0]
            else:
                method = getattr(self, method_name)
                result = method(*params)
        except:
            start_response('500', [('Content-Type', 'text/html')])
            exc_type, exc_instance, _ = sys.exc_info()
            remote_exc_type = _get_type_name(exc_type)
            fault = xmlrpclib.Fault(remote_exc_type, repr(exc_instance.args))
            # TODO: Log errors
            # log.error(__name__, 'Error on %s' % method_name)
            # log.error_exc(__name__)
            return [xmlrpclib.dumps(fault)]

        start_response('200 OK', [('Content-Type', 'text/html')])
        content = xmlrpclib.dumps((result,))
        return [content]

    def forward_request(self, raw_data):

    def start(self):
        """
        Registers all experiment server - like methods and starts the XMLRPC server.
        :return:
        """
        # self.server.start()
        self.server.serve_forever()

        # print self.listen_host
        # self.server = ThreadedXMLRPCServer( (self.listen_host, self.listen_port), WebLabHandler)
        # self.server.register_function(self.test_me, "Util.test_me")
        # self.server.register_function(self.is_up_and_running, "Util.is_up_and_running")
        # self.server.register_function(self.start_experiment, "Util.start_experiment")
        # self.server.register_function(self.send_file, "Util.send_file_to_device")
        # self.server.register_function(self.send_command, "Util.send_command_to_device")
        # self.server.register_function(self.dispose, "Util.dispose")
        # self.server.register_function(self.get_api, "Util.get_api")
        # self.server.register_function(self.should_finish, "Util.should_finish")
        # print "Running FAKE XML-RPC server on port %i" % self.listen_port
        # self.server.serve_forever()