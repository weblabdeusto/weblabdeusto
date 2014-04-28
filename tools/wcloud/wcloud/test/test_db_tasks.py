

######################################
#
# UNIT TESTS BELOW
#
######################################
import unittest

from nose.tools import assert_is_not_none
from sqlalchemy import text
from wcloud.tasks.db_tasks import connect, create_db, destroy_db


class TestDatabaseTasks(unittest.TestCase):

    def test_connect(self):
        """
        Test that we can connect to the database.
        """
        engine = connect("root", "password")
        assert_is_not_none(engine, "Engine is None")

    def test_create_db(self):
        """
        Test that we can successfully create a database.
        """
        db = create_db("root", "password", "wcloudtest", "weblab", "weblab")
        assert db.startswith("wcloudtest")

    def test_destroy_db(self):
        db = create_db("root", "password", "wcloudtest", "weblab", "weblab")
        destroy_db("root", "password", db)
        engine = connect("root", "password")
        dbs = engine.execute("SHOW databases LIKE '%s'" % db).fetchall()
        assert len(dbs) == 0

    def _clearTestDatabases(self):
        engine = connect("root", "password")
        dbs = engine.execute(text("SHOW databases LIKE :bn"), bn="%s%%" % "wcloud_test")
        dbs = dbs.fetchall()
        dbs = [db[0] for db in dbs]
        for db in dbs:
            engine.execute("DROP DATABASE %s" % db)

    def setUp(self):
        self._clearTestDatabases()

    def tearDown(self):
        self._clearTestDatabases()