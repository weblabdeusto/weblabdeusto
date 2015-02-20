import os
import unittest
from nose.tools import assert_is_not_none
from sqlalchemy import text
from wcloud.tasks.db_tasks import connect, create_db, destroy_db


# Fix the working directory.
cwd = os.getcwd()
if cwd.endswith(os.path.join("wcloud", "test")):
    cwd = cwd[0:len(cwd)-len(os.path.join("wcloud", "test"))]
    os.chdir(cwd)


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

        result = create_db.delay("root", "password", "wcloudtest", "wcloud", "password")
        db_name = result.get()
        assert db_name.startswith("wcloudtest")

    def test_destroy_db(self):
        db = create_db.delay("root", "password", "wcloudtest", "wcloud", "password").get()
        destroy_db.delay("root", "password", db).get()

        engine = connect("root", "password")
        dbs = engine.execute("SHOW databases LIKE '%s'" % db).fetchall()
        assert len(dbs) == 0

    def _clearTestDatabases(self):
        engine = connect("root", "password")
        dbs = engine.execute(text("SHOW databases LIKE :bn"), bn="%s%%" % "wcloudtest")
        dbs = dbs.fetchall()
        dbs = [db[0] for db in dbs]
        for db in dbs:
            engine.execute("DROP DATABASE %s" % db)

    def setUp(self):
        self._clearTestDatabases()

    def tearDown(self):
        self._clearTestDatabases()

