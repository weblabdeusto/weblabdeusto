from flaskclient.weblabweb import WeblabWeb
from nose.tools import *
import time

class TestWeblabWeb:
    def setUp(self):
        self.weblabweb = WeblabWeb()
        pass

    def test_login(self):
        """
        Tests that the Weblab login method is called successfully.
        """
        response = self.weblabweb._login("demo", "demo")
        assert_equal(unicode, type(response))

    def test_get_user_information(self):
        """
        Tests that the Weblab get_user_information method is called successfully.
        """
        sessionid = self.weblabweb._login("demo", "demo")
        time.sleep(2)
        response = self.weblabweb._get_user_information(sessionid)

        assert_is_not_none(response)
        assert_equal(response["login"], "demo")
        assert_equal(response["email"], "weblab@deusto.es")
        assert_equal(response["full_name"], "Demo User")
        assert_in("role", response)

    def test_list_experiments(self):
        """
        Tests that the Weblab list_experiments method is caled successfully.
        """
        sessionid = self.weblabweb._login("demo", "demo")
        time.sleep(2)
        response = self.weblabweb._list_experiments(sessionid)
        print response

        assert_is_not_none(response)