import json
from gevent import pywsgi


class BaseConnector(object):
    """
    Class that will listen on a port for Experiment Bridge requests (which will mainly be registration
    requests).
    """

    def __init__(self, listen_host, listen_port):
        super(BaseConnector, self).__init__()
        self.listen_host = listen_host
        self.listen_port = listen_port
        self.server = pywsgi.WSGIServer((self.listen_host, self.listen_port), self.on_http_request)

        # For now we will not use a method registry because we will just forward any method.
        self.methods_registry = {
        }

    def on_http_request(self, environ, start_response):
        """
        This should be handled in a Greenlet. It registers an alive ExpBridge and the
        experiments it provides.
        :type environ: dict
        :type start_response:
        :return:
        """
        if environ['REQUEST_METHOD'] == 'GET':
            start_response('200', [('Content-Type', 'text/html')])
            return ["This server accepts registration request from exp bridges"]

        input = environ.get('wsgi.input')
        raw_data = input.read()

        request = json.loads(raw_data)

        start_response('200 OK', [('Content-Type', 'text/html')])
        return ["Registered"]

    def start(self):
        """
        Starts listening for connections.
        :return:
        """
        return self.server.start()