from __future__ import print_function, unicode_literals
import time
import unittest
from base import SeleniumBaseTest


# Fix the path if we are running with the file's folder as working folder.
# (The actual working folder should be "src")
import os
cur_cwd = os.getcwd()
if cur_cwd.endswith(os.path.sep + "selenium"):
    os.chdir(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))


class TestLogin(SeleniumBaseTest):

    def __init__(self, *args, **kwargs):
        super(TestLogin, self).__init__(*args, **kwargs)

    def setUp(self):
        super(TestLogin, self).setUp()

    def tearDown(self):
        super(TestLogin, self).tearDown()

    def test_load(self):
        pass
        # self.driver.get(self.base_url + "/")
        # time.sleep(10)


if __name__ == "__main__":
    unittest.main()