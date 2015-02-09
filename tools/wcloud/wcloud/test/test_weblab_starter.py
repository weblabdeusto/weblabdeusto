import os
import unittest
from flask import Flask

import config

from wcloud.weblab_starter import app, start_weblab, check_weblab, stop_weblab
from wcloud.weblab_starter import main

import werkzeug


wcloud_app = Flask(__name__)


wcloud_app.config.from_object(config)
wcloud_app.config.from_envvar('WCLOUD_SETTINGS', silent=True)

FILENAME = os.path.join(wcloud_app.config['DIR_BASE'], 'instances.txt')


# Fix the working directory.
# TODO: Tidy this fix up.
cwd = os.getcwd()
if cwd.endswith(os.path.join("wcloud", "test")):
    cwd = cwd[0:len(cwd)-len(os.path.join("wcloud", "test"))]
    os.chdir(os.path.join(cwd, "wcloud"))



class TestWeblabStarter(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestWeblabStarter, self).__init__(*args, **kwargs)
        self.flask_app = None
        self._process = None

    def _cleanup(self):
        """
        Cleans up left-overs from this or other tests.
        Supposed to be somewhat idempotent.
        """
        lines = open(FILENAME, "r").readlines()
        lines = [line.strip() for line in lines if len(line.strip()) > 0 and "testentity" not in line]
        open(FILENAME, "w").writelines(lines)

    def DISABLED_test_root(self):
        response = self.flask_app.get("/")
        assert response.status_code == 200
        assert "listens in" in response.data

    def DISABLED_start_an_instance(self):
        print "CWD: " + os.getcwd()
        self._process = start_weblab("test/testinstance_sqlite", 15)
        active = check_weblab("test/testinstance_sqlite")
        assert active
        stop_weblab("test/testinstance_sqlite")

    def DISABLED_test_start_existing(self):
        main()

    def setUp(self):
        self._cleanup()
        app.config['DEBUG'] = True
        app.config['TESTING'] = True
        app.config['CSRF_ENABLED'] = False
        app.config["SECRET_KEY"] = 'secret'
        self.flask_app = app.test_client()
        self.flask_app.get("/")

    def tearDown(self):
        if self._process is not None:
            print "Cleaning process: " + str(self._process.pid)
            self._process.kill()

