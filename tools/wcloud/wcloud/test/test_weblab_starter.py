import os
import unittest

from wcloud.weblab_starter import app, start_weblab, test_weblab, stop_weblab
from wcloud.weblab_starter import main


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

    def _cleanup(self):
        pass

    def test_root(self):
        response = self.flask_app.get("/")
        assert response.status_code == 200
        assert "listens in" in response.data

    def test_start_test_instance(self):
        start_weblab("test/testinstance", 5)
        active = test_weblab("test/testinstance")
        assert active
        stop_weblab("test/testinstance")

    def test_start_existing(self):
        main()


    def setUp(self):
        app.config['DEBUG'] = True
        app.config['TESTING'] = True
        app.config['CSRF_ENABLED'] = False
        app.config["SECRET_KEY"] = 'secret'
        self.flask_app = app.test_client()
        self.flask_app.get("/")
