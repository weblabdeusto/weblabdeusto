import json
import gevent.socket
import grequests
from lab_bridge.comms.expbridge import LongPollingConnector

def _start_server():
    bc = LongPollingConnector.LongPollingConnector("127.0.0.1", 10500)
    bc.start()
    return bc

class TestLongPollingConnectorBasics():

    def setup(self):
        self.bc = _start_server()

    def teardown(self):
        self.bc.stop()

    def test_connect(self):
        s = gevent.socket.create_connection(("127.0.0.1", 10500))
        assert s is not None

    def test_handle_register_request(self):

        req = {
            "type": "register",
            "data": {
                "auth": "0000",
                "experiments": ["exp1", "exp2"]
            }
        }

        reqdata = json.dumps(req)

        response = grequests.post("http://127.0.0.1:10500", data=reqdata).send()

        assert response is not None
        msg = response.json()

        assert msg["type"] == "register"
        assert msg["data"]["result"] == "ok"
        assert msg["data"]["sid"] is not None

    def test_handle_register_failure(self):

        req = {
            "type": "register",
            "data": {
                "auth": "fakepassword",
                "experiments": ["exp1", "exp2"]
            }
        }

        reqdata = json.dumps(req)

        rr = grequests.post("http://127.0.0.1:10500", data=reqdata)
        result = grequests.map([rr])

        response = result[0]

        assert response is not None
        msg = response.json()

        assert msg["type"] == "register"
        assert msg["data"]["result"] == "fail"
        assert "sid" not in msg["data"]

class TestLongPollingConnectorAuthenticated():

    def setup(self):
        self.bc = _start_server()

        # Fake a register call.
        self.bc.on_register("0000", ["exp1", "exp2"])

        self.session = self.bc.session

    def teardown(self):
        self.bc.stop()

    def test_connect(self):
        s = gevent.socket.create_connection(("127.0.0.1", 10500))
        assert s is not None

    def _g_tick_sending(self):
        # Sends a tick and ensures that the request we send is received and replied to.

        # Send tick.
        req = {"type": "tick", "sid": self.bc.session, "data": {"responses": []}}
        reqdata = json.dumps(req)
        tickresult = grequests.post("http://127.0.0.1:10500", data=reqdata).send()
        tickresult = tickresult.json()

        assert tickresult is not None
        assert tickresult["type"] == "tick"
        assert tickresult["data"] is not None

        # Ensure that we have received a request.
        assert len(tickresult["data"]["requests"]) == 1
        request = tickresult["data"]["requests"][0]
        assert request is not None

        assert request["id"] is not None
        assert request["data"] == "REQUEST1"

        # Reply to the request as if we had handled it (with another tick)
        responses = []
        req = {"type": "tick", "sid": self.bc.session, "data": {"responses": responses}}
        responses.append({
            "id": request["id"],
            "data": "RESPONSE1"
        })

        reqdata = json.dumps(req)
        tickresult = grequests.post("http://127.0.0.1:10500", data=reqdata).send()
        tickresult = tickresult.json()

        assert tickresult is not None

        # Ensure there are no requests (becasue we haven't queued any)
        assert len(tickresult["data"]["requests"]) == 0

    def test_send_request(self):
        gevent.spawn(self._g_tick_sending)

        response = self.bc.send_request("exp1", "REQUEST1")
        assert response is not None
        assert response == "RESPONSE1"