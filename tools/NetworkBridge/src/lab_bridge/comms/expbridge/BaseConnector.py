import json
from gevent import pywsgi


class BaseConnector(object):
    """
    Class that will listen on a port for Experiment Bridge requests (which will mainly be registration
    requests).
    """

    def __init__(self, listen_host, listen_port):
        super(BaseConnector, self).__init__()

    def on_register(self, auth, experiments):
        """
        Called when a REGISTER request is received from the Exp side.
        Attempts to register a new active ExpBridge.
        This is a gevent-powered pseudo-blocking call.
        :param auth: Authentication data received from the ExpBridge.
        :param experiments: Dictionary containing the experiment information.
        """
        password = data["password"]
        if password != "0000":
            raise Exception("Auth Failure Exception") # TODO: Replace with a proper exception.

        # Auth succeeded. Create a new session.
        self.session = self._generate_session()

        # Build the response

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

