from __future__ import print_function, unicode_literals
import time
import unittest
from base import SeleniumBaseTest


class TestLogin(SeleniumBaseTest):

    def __init__(self, *args, **kwargs):
        super(TestLogin, self).__init__(*args, **kwargs)

    def test_load(self):
        pass
        # self.driver.get(self.base_url + "/")
        # time.sleep(10)


if __name__ == "__main__":
    unittest.main()