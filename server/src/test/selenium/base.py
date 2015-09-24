# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from selenium import webdriver
from selenium.webdriver import FirefoxProfile
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import unittest, time, re

import os
from voodoo.gen import load_dir
from voodoo.gen.registry import GLOBAL_REGISTRY


class SeleniumBaseTest(unittest.TestCase):

    def start_test_weblab_deployment(self):
        # Load the configuration of the weblab instance that we have set up for just this test.
        self.global_config = load_dir('test/deployments/webclient_dummy')

        # Start the weblab instance. Because we have activated the dont-start flag it won't actually
        # start listening on the port, but let us use the Flask test methods instead.
        self.handler = self.global_config.load_process('myhost', 'myprocess')

        self.core_server = GLOBAL_REGISTRY['mycore:myprocess@myhost']

    @classmethod
    def setUpClass(self):

        # Starts a test deployment.
        self.start_test_weblab_deployment()

        if os.environ.get("SELENIUM_HEADLESS") and False:
            self.driver = webdriver.PhantomJS()
        else:
            self.profile = FirefoxProfile()
            self.profile.set_preference("intl.accept_languages", "en")
            self.driver = webdriver.Firefox(self.profile)

        self.driver.set_window_size(1400, 1000)

        # self.driver.implicitly_wait(30)

        self.base_url = "http://localhost:5000/"
        self.verificationErrors = []
        self.accept_next_alert = True

    def is_element_present(self, how, what):
        try: self.driver.find_element(by=how, value=what)
        except NoSuchElementException, e: return False
        return True

    def is_alert_present(self):
        try: self.driver.switch_to_alert()
        except NoAlertPresentException, e: return False
        return True

    def close_alert_and_get_its_text(self):
        try:
            alert = self.driver.switch_to_alert()
            alert_text = alert.text
            if self.accept_next_alert:
                alert.accept()
            else:
                alert.dismiss()
            return alert_text
        finally: self.accept_next_alert = True

    @classmethod
    def tearDownClass(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()