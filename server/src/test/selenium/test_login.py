from __future__ import print_function, unicode_literals
import unittest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
        self.driver.get_screenshot_as_file('last_screenshot.png')

    def _login(self):
        self.driver.get(self.core_server_url)

        username = self.driver.find_element_by_id("username")
        password = self.driver.find_element_by_id("password")
        login = self.driver.find_element_by_id("login")

        # Login
        username.send_keys("any")
        password.send_keys("password")
        login.click()

        WebDriverWait(self.driver, 10).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, ".rotating-ball"))
        )

    def test_login(self):
        self._login()

        # Verify that we landed in My Experiments
        my_exps_h3 = self.driver.find_element_by_css_selector("center h2")
        self.assertEqual(my_exps_h3.text, "My Experiments")

        # Verify that we have several Experiments in the page
        my_exps = self.driver.find_elements_by_css_selector(".lab-block")
        self.assertGreater(len(my_exps), 0)

    def test_logout(self):

        # We need to login first.
        self._login()

        # Logout
        logout = self.driver.find_element_by_css_selector('a[href="/weblab/logout"')
        logout.click()

        # Ensure that we have managed to logout
        password = self.driver.find_element_by_id("password")


if __name__ == "__main__":
    unittest.main()