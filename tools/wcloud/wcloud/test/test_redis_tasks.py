
######################################
#
# UNIT TESTS BELOW
#
# REQUIREMENTS:
#   - Redis-server installed and accessible from cmd.
#
######################################
import os
import unittest

from wcloud.tasks.redis_tasks import deploy_redis_instance, check_redis_deployment

# These tests are meant to be run from the root wcloud folder. Fix the path
# so it is so.
cwd = os.getcwd()
if cwd.endswith(os.path.join("wcloud", "test")):
    cwd = cwd[0:len(cwd)-len(os.path.join("wcloud", "test"))]
os.chdir(cwd)


class TestRedisTasks(unittest.TestCase):
    def test_deploy_redis_instance(self):
        deploy_redis_instance("redis_env", 15000)
        assert os.path.exists("redis_env/redis_15000.conf")

    def test_check_redis_instance(self):
        deploy_redis_instance("redis_env", 15000)
        check_redis_deployment("redis_env", 15000)

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

