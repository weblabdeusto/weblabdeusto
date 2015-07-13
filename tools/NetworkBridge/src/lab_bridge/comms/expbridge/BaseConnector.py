import json
import random
import string
from gevent import pywsgi
from lab_bridge.comms import forwarder


class NotAuthorizedException(Exception):
    pass

class BaseConnector(object):
    """
    Class that will listen on a port for Experiment Bridge requests (which will mainly be registration
    requests).
    """

    def __init__(self, listen_host, listen_port):
        super(BaseConnector, self).__init__()
        self.listen_host = listen_host
        self.listen_port = listen_port
        self.session = None

    def _generate_session(self):
        """Generate the session identifier"""
        return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(12))

    def _generate_reqid(self):
        """Generate the session identifier"""
        return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(12))

    def on_register(self, auth, experiments):
        """
        Called when a REGISTER request is received from the Exp side.
        Attempts to register a new active ExpBridge.
        This is a gevent-powered pseudo-blocking call.
        The session is stored in the class and returned as well.
        :param auth: Authentication data received from the ExpBridge.
        :type auth: str
        :param experiments: Dictionary containing the experiment information.
        :type experiments: dict
        :return: session
        :rtype: str
        """
        if auth != "0000":
            raise Exception("Auth Failure Exception") # TODO: Replace with a proper exception.

        # Auth succeeded. Create a new session.
        self.session = self._generate_session()

        # Register the experiments in the forwarder, so that we can send the requests received by the LabListener
        # through the right connector.
        for exp in experiments:
            forwarder.add_connector(exp, self)

        return self.session

    def check_authenticated(self, sid):
        """
        Checks that the SID is the currently authenticated one. Otherwise raises a NotAuthorizedException.
        :param sid:
        :return:
        """
        if self.session != sid:
            raise NotAuthorizedException()

    def send_request(self, experiment, request):
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

    def stop(self):
        """
        Stops listening for connections.
        :return:
        """
        raise NotImplementedError("Not implemented")

