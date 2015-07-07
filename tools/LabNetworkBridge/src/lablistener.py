
from gevent import pywsgi
import gevent
import time
import xmlrpclib
import urllib2

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

    def on_http_request(self, environ, start_response):
        start_response('404 Not Found', [('Content-Type', 'text/html')])
        print "ON HTTP REQUEST"
        return ['<b>Hello world!!!!</b>\n']

    def test_me(self, message):
        return message

    def is_up_and_running(self):
        return True

    def start_experiment(self, client_initial_data, server_initial_data):
        return "{}"

    def send_file(self, content, file_info):
        return "ok"

    def send_command(self, command_string):
        print "AT SEND_COMMAND"
        gevent.sleep(5)
        print "AT SEND COMMAND (2)"
        gevent.sleep(5)
        print "AT SEND COMMAND (3)"
        gevent.sleep(5)
        return "ok"

    def dispose(self):
        return "{}"

    def should_finish(self):
        return 0

    def get_api(self):
        return "2"

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