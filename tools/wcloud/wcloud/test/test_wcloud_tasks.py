######################################
#
# UNIT TESTS BELOW
#
######################################
import json
import os
import shutil
import unittest
import time
import subprocess
import requests
from wcloud.tasks.wcloud_tasks import flask_app, prepare_system, create_weblab_environment, configure_web_server, register_and_start_instance, finish_deployment
from weblab.admin.script import Creation

# These tests are meant to be run from the root wcloud folder. Fix the path
# so it is so.
cwd = os.getcwd()
if cwd.endswith(os.path.join("wcloud", "test")):
    cwd = cwd[0:len(cwd)-len(os.path.join("wcloud", "test"))]
os.chdir(cwd)

class TestWcloudTasks(unittest.TestCase):

    wcloud_settings = {
        "DB_USERNAME": "wcloud",
        "DB_PASSWORD": "password",
        "DB_NAME": "wcloudtest",
        "REDIS_FOLDER": "redis_env",
        "WEBLAB_STARTUP_TIME": 2
    }

    def test_prepare_system(self):
        """
        Tests that the first step (prepare system) works as expected.

        Prerrequisites: mysql running, redis running.
        """
        settings = prepare_system("testuser@testuser.com", "admin", "Administrador", "password", "admin@admin.com",
                       self.wcloud_settings)
        self._settings = settings

    def test_create_weblab_environment(self):
        settings = prepare_system("testuser@testuser.com", "admin", "Administrador", "password", "admin@admin.com",
               self.wcloud_settings)
        self._settings = settings
        base_url = os.path.join(flask_app.config["DIR_BASE"], settings[Creation.BASE_URL])
        create_weblab_environment(base_url, settings)

    def test_create_weblab_environment_thorough(self):

        settings = prepare_system("testuser@testuser.com", "admin", "Administrador", "password", "admin@admin.com",
               self.wcloud_settings)
        self._settings = settings
        base_url = os.path.join(flask_app.config["DIR_BASE"], settings[Creation.BASE_URL])
        create_weblab_environment(base_url, settings)

        # Start a local server on that config to check whether it works as expected.
        from weblab.comm.proxy_server import start as start_proxy
        g = globals()
        l = locals()
        execfile(os.path.join(base_url, 'httpd/simple_server_config.py'), g, l)
        print "FILE: " + base_url
        p = g.get("PATHS") or l.get("PATHS")
        start_proxy(8001, p)

        time.sleep(1)

        r = requests.get("http://localhost:8001/testentity/weblab/client/index.html")
        assert r.status_code == 200
        assert "Deusto" in r.text


    def test_configure_web_server(self):
        """
        Checks whether the Apache server can be configured correctly.
        PRERREQUISITE: Apache Reloader script must previously be running.
        """
        settings = prepare_system("testuser@testuser.com", "admin", "Administrador", "password", "admin@admin.com",
               self.wcloud_settings)
        self._settings = settings
        base_url = os.path.join(flask_app.config["DIR_BASE"], settings[Creation.BASE_URL])
        creation_results = create_weblab_environment(base_url, settings)
        configure_web_server(creation_results)

        assert os.path.isfile(os.path.join(base_url, "../", "apache.conf"))
        content = open(os.path.join(base_url, "../", "apache.conf"), "r").read()
        assert "testentity" in content
        lines = content.split("\n")
        line = [line.strip() for line in lines if "testentity" in line][0]
        assert os.path.isfile(line.split("\"")[1])

    def test_register_and_start_instance(self):
        """
        Test whether the weblab instance can be started successfully.
        PRERREQUISITE: weblabstarter script needs to be running in the background.
        """
        time.sleep(2)
        settings = prepare_system("testuser@testuser.com", "admin", "Administrador", "password", "admin@admin.com",
            self.wcloud_settings)
        self._settings = settings
        base_url = os.path.join(flask_app.config["DIR_BASE"], settings[Creation.BASE_URL])
        creation_results = create_weblab_environment(base_url, settings)
        configure_web_server(creation_results)
        register_and_start_instance("testuser@testuser.com", {})

        start_port, end_port = creation_results["start_port"], creation_results["end_port"]

    def test_finish_deployment(self):
        """
        test_finish_deployment: Tests that every step can be done, and the deployment finished.
        PRERREQUISITES: apache-reloader and weblab-starter scripts running.
        """
        settings = prepare_system("testuser@testuser.com", "admin", "Administrador", "password", "admin@admin.com",
            self.wcloud_settings)
        self._settings = settings
        base_url = os.path.join(flask_app.config["DIR_BASE"], settings[Creation.BASE_URL])
        creation_results = create_weblab_environment(base_url, settings)
        configure_web_server(creation_results)
        register_and_start_instance("testuser@testuser.com", self.wcloud_settings)

        start_port, end_port = creation_results["start_port"], creation_results["end_port"]
        finish_deployment("testuser@testuser.com", settings, start_port, end_port, self.wcloud_settings)
        pass

    def test_finish_deployment_thorough(self):
        """
        test_finish_deployment_thorough: Tests that every step can be done, and the deployment finished.
        Checks that after being configured, Apache is indeed serving the new instance correctly.
        PRERREQUISITES: apache-reloader and weblab-starter scripts running; apache2 configured correctly to load the instances.
        """
        settings = prepare_system("testuser@testuser.com", "admin", "Administrador", "password", "admin@admin.com",
            self.wcloud_settings)
        self._settings = settings
        base_url = os.path.join(flask_app.config["DIR_BASE"], settings[Creation.BASE_URL])
        creation_results = create_weblab_environment(base_url, settings)
        configure_web_server(creation_results)
        register_and_start_instance("testuser@testuser.com", self.wcloud_settings)

        start_port, end_port = creation_results["start_port"], creation_results["end_port"]
        finish_deployment("testuser@testuser.com", settings, start_port, end_port, self.wcloud_settings)

        # Check that the new instance is being served correctly.
        bot = requests.Session()
        r = bot.get("http://localhost/testentity/weblab/client/index.html")
        text = r.text
        print text
        assert "weblabclientlab" in text
        assert "input" in text
        assert "hiddenPassword" in text

        # Check that we can login with admin/password.
        r = bot.post("http://localhost/testentity/weblab/login/json/", data="""{"params":{"username":"admin", "password":"password"}, "method":"login"}""")
        str = r.text
        print "The request returned: " + str
        j = json.loads(str)
        assert not j["is_exception"]
        assert "id" in j["result"]

    def setUp(self):
        import wcloud.test.prepare as prepare

        prepare.prepare_test_database("root", "password")

        # Remove running weblab instances.
        os.system("kill $(ps aux | grep 'python -OO.*wcloud' | awk '{print $2}')")

    def tearDown(self):

        # Delete the deployed directory.
        try:
            pass
            #shutil.rmtree("weblabtest")
        except:
            pass

        # Remove running weblab instances.
        os.system("kill $(ps aux | grep 'python -OO.*wcloud' | awk '{print $2}')")

        # Remove the testentity line if present. Otherwise, the next attempt to start-weblab will fail
        # because its folder will be removed.
        try:
            instances_file = os.path.join(flask_app.config["DIR_BASE"], "instances.txt")
            f = file(instances_file)
            lines = f.readlines()
            lines = [line.replace("\n", "") + "\n" for line in lines if not "testentity" in line]
            f.close()
            f = file(instances_file, "w")
            f.writelines(lines)
            f.close()
        except:
            pass

        # Remove the include from apache.conf
        apacheconf = os.path.join(flask_app.config["DIR_BASE"], "apache.conf")
        lines = open(apacheconf, "r").readlines()
        cleared_lines = [line.strip() + "\n" for line in lines if "testentity" not in line]
        open(apacheconf, "w").writelines(cleared_lines)

        # Make sure all the instances are stopped. DANGEROUS: This will kill all running instances of WebLab.
        # This is done, specifically, so that "testentity" instance is killed after being run, so that
        # the test can be run again without issues.l
        try:
            os.system("killall weblab-admin")
        except:
            pass

        # TODO: Careful with this. It is dangerous, in production if configured wrongly it would
        # erase the whole deployments directory.
        try:
            base_url = os.path.join(flask_app.config["DIR_BASE"], self._settings[Creation.BASE_URL])
            shutil.rmtree(base_url)
        except:
            pass

        # Give it some time. It seems to be necessary.
        time.sleep(1.5)

