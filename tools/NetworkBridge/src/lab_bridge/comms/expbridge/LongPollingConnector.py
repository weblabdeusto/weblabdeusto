import json

from gevent import pywsgi
from gevent.event import AsyncResult
from gevent.queue import Queue, Empty

from lab_bridge.comms.expbridge import BaseConnector


class LongPollingConnector(BaseConnector.BaseConnector):
    """
    Class that will listen on a port for Experiment Bridge requests (which will mainly be registration
    requests), and which will rely on LongPolling to forward requests.

    DOC: The protocol that this class implements is described in the file: LongPollingConnector.protocol.doc.txt
    """

    def __init__(self, listen_host, listen_port):
        super(LongPollingConnector, self).__init__(listen_host, listen_port)
        self.server = pywsgi.WSGIServer((self.listen_host, self.listen_port), self._on_http_request)
        self.session = None
        self.outgoing_requests = Queue()  # Store pending outgoing requests.
        self.awaited_responses = {}  # Store the async responses for the commands.

    def _handle_register_request(self, data):
        """
        Handles the register request.
        :param data:
        :return:
        """
        auth = data["auth"]
        experiments = data["experiments"]

        try:
            self.on_register(auth, experiments)
        except:
            response = {"type": "register", "data": {"result": "fail"}}
            responsejson = json.dumps(response)
            return [responsejson]

        response = {"type": "register", "data": {"result": "ok", "sid": self.session}}
        responsejson = json.dumps(response)
        return [responsejson]

    def _send_pending_requests(self):
        """
        Sends the requests that are pending. They are sent within an actual HTTP tick-request reply.
        :return: List containing the raw bytes to send back.
        :rtype: list
        """
        response = []

        requests = []
        reply = {"type": "tick", "data": {"requests": requests}}

        try:
            req = self.outgoing_requests.get_nowait()
            reqbuilt = {"id": req[0], "experiment": req[1], "data": req[2]}
            requests.append(reqbuilt)
        except Empty:
            pass

        # JSON-encode the response itself.
        responsejson = json.dumps(reply)
        response.append(responsejson)

        return response

    def _on_http_request(self, environ, start_response):
        """
        This runs in a greenlet. Receives requests often because it uses a polling approach.
        :type environ: dict
        :type start_response:
        :return:
        """
        input = environ.get('wsgi.input')
        raw_data = input.read()

        message = json.loads(raw_data)

        # "register me and my experiments" request from the Experiment side
        if message["type"] == "register":
            data = message["data"]
            start_response('200 OK', [('Content-Type', 'text/html')])
            return self._handle_register_request(data)

        # "give me requests and here you have responses" request from the Experiment side
        # Reply with: "Here you have the requests"
        elif message["type"] == "tick":
            data = message["data"]
            self.check_authenticated(message["sid"])
            if "responses" in data:
                for response in data["responses"]:
                    id = response["id"]
                    reqdata = response["data"]
                    self._on_request_response(id, reqdata)

            # Either way, we need to reply with our own new requests.
            start_response('200 OK', [('Content-Type', 'text/html')])
            return self._send_pending_requests()

        # Currently we do not support other requests.
        else:
            raise Exception("Unrecognized experiment-side request")

    def _on_request_response(self, id, responsedata):
        """
        We have received a reply to a request. We notify the greenlet that is probably listening.
        """
        aresult = self.awaited_responses[id]
        aresult.set(responsedata)

    # Overrides
    def send_request(self, experiment, request):
        """
        Sends a request to the specified experiment AND returns the response.
        This is a gevent-powered pseudo-blocking call.
        :return:
        """
        # Generate a request and add it to the queue and await the response.
        reqid = self._generate_reqid()
        reqresult = self.awaited_responses[reqid] = AsyncResult()
        self.outgoing_requests.put((reqid, experiment, request))

        # Wait for the response. TODO: Set a timeout?
        response = reqresult.get()
        return response

    def start(self):
        """
        Starts listening for connections.
        :return:
        """
        self.server.start()

    def stop(self):
        """
        Stops listening for connections.
        :return:
        """
        self.server.stop()
