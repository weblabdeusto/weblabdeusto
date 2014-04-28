######################################
#
# UNIT TESTS BELOW
#
######################################
import os
import shutil
import unittest
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
        settings = prepare_system("testuser@testuser.com", "admin", "Administrador", "password", "admin@admin.com",
                       self.wcloud_settings)
        self._settings = settings

    def test_create_weblab_environment(self):
        settings = prepare_system("testuser@testuser.com", "admin", "Administrador", "password", "admin@admin.com",
               self.wcloud_settings)
        self._settings = settings
        base_url = os.path.join(flask_app.config["DIR_BASE"], settings[Creation.BASE_URL])
        create_weblab_environment(base_url, settings)

    def test_configure_web_server(self):
        settings = prepare_system("testuser@testuser.com", "admin", "Administrador", "password", "admin@admin.com",
               self.wcloud_settings)
        self._settings = settings
        base_url = os.path.join(flask_app.config["DIR_BASE"], settings[Creation.BASE_URL])
        creation_results = create_weblab_environment(base_url, settings)
        configure_web_server(creation_results)

    def test_register_and_start_instance(self):
        settings = prepare_system("testuser@testuser.com", "admin", "Administrador", "password", "admin@admin.com",
            self.wcloud_settings)
        self._settings = settings
        base_url = os.path.join(flask_app.config["DIR_BASE"], settings[Creation.BASE_URL])
        creation_results = create_weblab_environment(base_url, settings)
        configure_web_server(creation_results)
        register_and_start_instance("testuser@testuser.com", {})

        start_port, end_port = creation_results["start_port"], creation_results["end_port"]

    def test_finish_deployment(self):
        settings = prepare_system("testuser@testuser.com", "admin", "Administrador", "password", "admin@admin.com",
            self.wcloud_settings)
        self._settings = settings
        base_url = os.path.join(flask_app.config["DIR_BASE"], settings[Creation.BASE_URL])
        creation_results = create_weblab_environment(base_url, settings)
        configure_web_server(creation_results)
        register_and_start_instance("testuser@testuser.com", self.wcloud_settings)

        start_port, end_port = creation_results["start_port"], creation_results["end_port"]
        finish_deployment("testuser@testuser.com", settings, start_port, end_port, self.wcloud_settings)

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

