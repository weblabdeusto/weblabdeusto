import os
import unittest


# Fix the working directory.
from wcloud.tasks import redis_tasks

cwd = os.getcwd()
if cwd.endswith(os.path.join("wcloud", "test")):
    cwd = cwd[0:len(cwd)-len(os.path.join("wcloud", "test"))]
    os.chdir(cwd)


class TestRedisTasks(unittest.TestCase):
    def test_deploy_redis_instance(self):
        result = redis_tasks.deploy_redis_instance.delay("redis_env", 15000)
        result.wait()
        assert os.path.exists("redis_env/redis_15000.conf")

    def test_check_redis_instance(self):
        result = redis_tasks.deploy_redis_instance.delay("redis_env", 15000)
        result.wait()

        result = redis_tasks.check_redis_deployment.delay("redis_env", 15000)
        result.wait()

    def _clearTestDatabases(self):
        pass

    def setUp(self):
        try:
            os.remove("redis_env/redis_15000.conf")
        except:
            pass

    def tearDown(self):
        try:
            os.remove("redis_env/redis_15000.conf")
        except:
            pass

