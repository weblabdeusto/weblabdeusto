

######################################
#
# UNIT TESTS BELOW
#
# REQUIREMENTS:
#   - mysql-server should be running.
#   - An account should exist with the privileges to create accounts: root / password.
#   - Unless different account / passwords are specified through.
#
######################################
import unittest
from flask import Flask

from nose.tools import assert_is_not_none
from sqlalchemy import text
from wcloud.tasks.db_tasks import connect, create_db, destroy_db


# TODO: Remove the dependency on this.
import wcloud.config.wcloud_settings_default as wcloud_settings_default
import wcloud.config.wcloud_settings as wcloud_settings

flask_app = Flask(__name__)
flask_app.config.from_object(wcloud_settings_default)
flask_app.config.from_object(wcloud_settings)
flask_app.config.from_envvar('WCLOUD_SETTINGS', silent=True)


class TestDatabaseTasks(unittest.TestCase):

    def test_connect(self):
        """
        Test that we can connect to the database.
        """
        engine = connect(flask_app.config["DB_USERNAME"], flask_app.config["DB_PASSWORD"])
        assert_is_not_none(engine, "Engine is None")

    def test_create_db(self):
        """
        Test that we can successfully create a database.
        """
        db = create_db("root", "password", "wcloudtest", flask_app.config["DB_USERNAME"], flask_app.config["DB_PASSWORD"])
        assert db.startswith("wcloudtest")

    def test_destroy_db(self):
        db = create_db("root", "password", "wcloudtest", flask_app.config["DB_USERNAME"], flask_app.config["DB_PASSWORD"])
        destroy_db("root", "password", db)
        engine = connect("root", "password")
        dbs = engine.execute("SHOW databases LIKE '%s'" % db).fetchall()
        assert len(dbs) == 0

    def _clearTestDatabases(self):
        engine = connect(flask_app.config["DB_USERNAME"], flask_app.config["DB_PASSWORD"])
        dbs = engine.execute(text("SHOW databases LIKE :bn"), bn="%s%%" % "wcloud_test")
        dbs = dbs.fetchall()
        dbs = [db[0] for db in dbs]
        for db in dbs:
            engine.execute("DROP DATABASE %s" % db)

    def setUp(self):
        self._clearTestDatabases()

    def tearDown(self):
        self._clearTestDatabases()