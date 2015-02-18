import os
import unittest
import shutil
import wcloud.tasks.wcloud_tasks as wcloud_tasks
from weblab.admin.script import Creation


# Fix the working directory.
# TODO: Tidy this fix up.
cwd = os.getcwd()
if cwd.endswith(os.path.join("wcloud", "test")):
    cwd = cwd[0:len(cwd)-len(os.path.join("wcloud", "test"))]
    os.chdir(os.path.join(cwd, "wcloud"))



class TestWcloudTasks(unittest.TestCase):

    wcloud_settings = {
        "DB_USERNAME": "wcloud",
        "DB_PASSWORD": "password",
        "DB_NAME": "wcloudtest",
        "REDIS_FOLDER": "redis_env"
    }

    def test_nothing(self):
        pass

    def test_prepare_system(self):
        settings = wcloud_tasks.prepare_system.delay("testuser@testuser.com", "admin", "Administrador", "password", "admin@admin.com",
                       self.wcloud_settings).get()
        self._settings = settings

    def test_create_weblab_environment(self):
        settings = wcloud_tasks.prepare_system.delay("testuser@testuser.com", "admin", "Administrador", "password", "admin@admin.com",
               self.wcloud_settings).get()
        self._settings = settings
        base_url = os.path.join(wcloud_tasks.flask_app.config["DIR_BASE"], settings[Creation.BASE_URL])
        wcloud_tasks.create_weblab_environment.delay(base_url, settings).get()

    def test_configure_web_server(self):
        settings = wcloud_tasks.prepare_system.delay("testuser@testuser.com", "admin", "Administrador", "password", "admin@admin.com",
               self.wcloud_settings).get()
        self._settings = settings
        base_url = os.path.join(wcloud_tasks.flask_app.config["DIR_BASE"], settings[Creation.BASE_URL])
        creation_results = wcloud_tasks.create_weblab_environment.delay(base_url, settings).get()
        wcloud_tasks.configure_web_server.delay(creation_results).get()

    def test_register_and_start_instance(self):
        settings = wcloud_tasks.prepare_system.delay("testuser@testuser.com", "admin", "Administrador", "password", "admin@admin.com",
            self.wcloud_settings).get()
        self._settings = settings
        base_url = os.path.join(wcloud_tasks.flask_app.config["DIR_BASE"], settings[Creation.BASE_URL])
        creation_results = wcloud_tasks.create_weblab_environment.delay(base_url, settings).get()
        wcloud_tasks.configure_web_server.delay(creation_results).get()
        wcloud_tasks.register_and_start_instance.delay("testuser@testuser.com", {}).get()

        start_port, end_port = creation_results["start_port"], creation_results["end_port"]

    def test_finish_deployment(self):
        settings = wcloud_tasks.prepare_system.delay("testuser@testuser.com", "admin", "Administrador", "password", "admin@admin.com",
            self.wcloud_settings).get()
        self._settings = settings
        base_url = os.path.join(wcloud_tasks.flask_app.config["DIR_BASE"], settings[Creation.BASE_URL])
        creation_results = wcloud_tasks.create_weblab_environment.delay(base_url, settings).get()
        wcloud_tasks.configure_web_server.delay(creation_results).get()
        wcloud_tasks.register_and_start_instance.delay("testuser@testuser.com", self.wcloud_settings).get()

        start_port, end_port = creation_results["start_port"], creation_results["end_port"]
        wcloud_tasks.finish_deployment.delay("testuser@testuser.com", settings, start_port, end_port, self.wcloud_settings).get()

    def setUp(self):
        import wcloud.test.prepare as prepare

        prepare.prepare_test_database("root", "password")

    def tearDown(self):

        # Delete the deployed directory.
        try:
            pass
            #shutil.rmtree("weblabtest")
        except:
            pass

        # Remove the testentity line if present. Otherwise, the next attempt to start-weblab will fail
        # because its folder will be removed.
        try:
            instances_file = os.path.join(wcloud_tasks.flask_app.config["DIR_BASE"], "instances.txt")
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
        apacheconf = os.path.join(wcloud_tasks.flask_app.config["DIR_BASE"], "apache.conf")
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
            base_url = os.path.join(wcloud_tasks.flask_app.config["DIR_BASE"], self._settings[Creation.BASE_URL])
            shutil.rmtree(base_url)
        except:
            pass

