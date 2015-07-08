import json
import random
import string
from gevent import pywsgi
from lab_bridge.comms.expbridge import BaseConnector


class LongPollingConnector(BaseConnector):
    """
    Class that will listen on a port for Experiment Bridge requests (which will mainly be registration
    requests), and which will rely on LongPolling to forward requests.
    """

    def __init__(self, listen_host, listen_port):
        super(BaseConnector, self).__init__(listen_host, listen_port)
        self.server = pywsgi.WSGIServer((self.listen_host, self.listen_port), self.on_http_request)
        self.session = None

    def _generate_session(self):
        return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(12))

    def _handle_register_request(self, data):
        """
        Handles the register request.
        :param data:
        :return:
        """
        password = data["auth"]
        if password != "0000":
            raise Exception("Auth Failure Exception") # TODO: Replace with a proper exception.

        # Auth succeeded. Create a new session.
        self.session = self._generate_session()

        # Build the response


    def on_http_request(self, environ, start_response):
        """
        This runs in a greenlet. Receives requests often because it uses a polling approach.
        :type environ: dict
        :type start_response:
        :return:
        """
        input = environ.get('wsgi.input')
        raw_data = input.read()

        print "RAW DATA RECEIVED: " + raw_data

        message = json.loads(raw_data)

        if message["type"] == "register":
            data = message["data"]
            start_response('200 OK', [('Content-Type', 'text/html')])
            return [self._handle_register_request(data)]

        else:
            # TODO
            pass

    def on_register(self, auth, experiments):
        """
        Called when a REGISTER request is received from the Exp side.
        Attempts to register a new active ExpBridge.
        This is a gevent-powered pseudo-blocking call.
        :param auth: Authentication data received from the ExpBridge.
        :param experiments: Dictionary containing the experiment information.
        """
        return "ok"

    def send_request(self, experiment):
        """
        Sends a request to the specified experiment AND returns the response.
        This is a gevent-powered pseudo-blocking call.
        :return:
        """
        raise NotImplementedError("Not implemented")

    def start(self):
        """
        Starts listening for connections.
        :return:
        """
        raise NotImplementedError("Not implemented")

    def _send_message(self):
        """
        Replies to the
        :return:
        """
        raise NotImplementedError("Not implemented")

    def start(self):
        """
        Starts listening for connections.
        :return:
        """
        self.server.start()