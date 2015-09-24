
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
        # self.client = xmlrpclib.ServerProxy("http://127.0.0.1:10501", )
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
        response = self._test_bridge("hello")
        assert response == ("hello",)

        # assert result == "testparam"

    def _tsest_send_command_notfound(self):
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

    def _tsest_send_command_forwarding(self):
        pass

        # m = self._get_expbridge_mock()

        # Register our mock as if it was our connector.
        # forwarder.add_connector("exp1", m)

        # response = self.client.send_command_to_device("TURNLED ON")

        # assert response == "ON"