import gevent
import grequests
from lab_bridge.comms.expbridge import BaseConnector

from nose.tools import *

bc = None


def test_instance():
    bc = BaseConnector.BaseConnector("127.0.0.1", 10500)

def test_session_generation():
    bc = BaseConnector.BaseConnector("127.0.0.1", 10500)
    s = bc._generate_session()
    r = bc._generate_reqid()
    assert type(s) is str
    assert type(r) is str
    assert len(s) > 4
    assert len(r) > 4
    assert s != r

def test_on_register_success():
    bc = BaseConnector.BaseConnector("127.0.0.1", 10500)
    result = bc.on_register("0000", ["exp1", "exp2"])
    assert bc.session is not None
    assert type(bc.session) is str
    assert result is not None
    assert type(bc.session) is str
    assert bc.session == result

@raises(Exception)
def test_on_register_failure():
    bc = BaseConnector.BaseConnector("127.0.0.1", 10500)
    result = bc.on_register("WRONG PASS", ["exp1", "exp2"])
