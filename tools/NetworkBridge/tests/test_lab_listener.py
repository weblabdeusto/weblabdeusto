
import xmlrpclib
import grequests

import gevent.socket
import mock

from lab_bridge.comms import forwarder
from lab_bridge.comms.lab.LabListener import LabListener


def _start_server():
    ll = LabListener("exp1", "127.0.0.1", 10501, "exp1")
    ll.start()
    return ll

class TestLabListener(object):

    def setup(self):
        forwarder._reset()
        self.ll = _start_server()
        self.client = xmlrpclib.ServerProxy("http://127.0.0.1:10501", )
        print "Started"

    def teardown(self):
        self.ll.stop()
        print "Stopped"

    def test_connect(self):
        s = gevent.socket.create_connection(("127.0.0.1", 10501))
        assert s is not None

    def _test_bridge(self, param):
        data = xmlrpclib.dumps((param,), methodname="test_bridge")
        response = grequests.post("http://127.0.0.1:10501", data=data).send()
        response = xmlrpclib.loads(response.content)
        return response[0]

    def test_test_bridge_request(self):
        """
        Ensure that the LabListener responds to the test_bridge testing command.
        """
        response = self._test_bridge("hello")
        assert response == ("hello",)

    def test_send_command_notfound(self):
        """
        Ensure that trying to carry out a send_command raises a specific exception if
        a forwarder has not been added.
        """
        try:
            result = self.client.send_command_to_device("TURNLED ON")
        except xmlrpclib.Fault as exc:
            assert exc.faultCode == "lab_bridge.comms.forwarder.ExperimentNotFound"
        else:
            assert False

    def _get_expbridge_mock(self):
        m = mock.MagicMock(name="ConnectorMock")
        m.send_request = self._fake_forward_request
        return m

    def _fake_forward_request(self, exp, req):
        return xmlrpclib.dumps(("ON",), methodresponse=True)

    def test_send_command_forwarding(self):
        """
        Ensure that the LabListener attempts to forward the command through the specified connector.
        """

        m = self._get_expbridge_mock()

        # Register our mock as if it was our connector.
        forwarder.add_connector("exp1", m)

        response = self.client.send_command_to_device("TURNLED ON")

        # Ensure that the send_request in our mock was invoked.
        assert response == "ON"