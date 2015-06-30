from __future__ import print_function, unicode_literals
import time
from base import SeleniumBaseTest


class TestLogin(SeleniumBaseTest):

    def test_load(self):
        self.driver.get(self.base_url + "/")
        time.sleep(10)