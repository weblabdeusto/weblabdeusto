from flaskclient.weblabweb import WeblabWeb
from nose.tools import *

class TestWeblabWeb:
    def setUp(self):
        self.weblabweb = WeblabWeb()
        pass

    def test_login(self):
        response = self.weblabweb._login("demo", "demo")
        assert_equal(unicode, type(response))