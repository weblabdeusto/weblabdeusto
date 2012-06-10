#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2005 onwards University of Deusto
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#
# This software consists of contributions made by many individuals,
# listed below:
#
# Author: Pablo Orduña <pablo@ordunya.com>
# 

import sys, os
sys.path.append( os.sep.join( ('..', 'src') ) )

from optparse import OptionParser

import time
t_initial = time.time()

import traceback
import subprocess

import libraries
import weblab.db.model as Model
import weblab.core.coordinator.model as CoordinatorModel

import voodoo.sessions.db_lock_data as DbLockData
import voodoo.sessions.sqlalchemy_data as SessionSqlalchemyData

from weblab.admin.deploy import insert_required_initial_data, populate_weblab_tests

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

try:
    import weblab_administrator_credentials as wac
except ImportError:
    print >> sys.stderr, "Error: weblab_administrator_credentials.py not found. Did you execute create_weblab_administrator.py first?" 
    sys.exit(1)

try:
	from configuration import weblab_db_username, weblab_db_password, core_coordinator_db_username, core_coordinator_db_password, weblab_sessions_db_username, weblab_sessions_db_password, db_engine
except ImportError, e:
	print >> sys.stderr, "Error: configuration.py doesn't exist or doesn't have all the required parameters: %s " % e
	sys.exit(2)

parser = OptionParser()
parser.add_option("-p", "--prefix", dest="prefix", default="",
                  help="Ask for a prefix", metavar="PREFIX")
parser.add_option("-a", "--avoid-real",
                  action="store_true", dest="avoid_real", default=False,
                  help="Avoid real database")
parser.add_option("-f", "--force",
                  action="store_true", dest="force", default=False,
                  help="Force removing information")

(options, args) = parser.parse_args()
prefix = options.prefix

if prefix != "" and not options.avoid_real and not options.force:
    print "WARNING: You have specified a prefix and this script is going to delete all the databases (including user information, experiments, etc.). Are you sure you want to delete all the information from all the WebLab databases? You can remove only the temporary coordination and session information by providing the -a option, and you can avoid this warning in the future passing the -f option."
    response = raw_input("Press 'y' if you are sure of this: ")
    if response != 'y':
        print "Cancelled by the user"
        sys.exit(0)

if db_engine == 'mysql':
    try:
        import MySQLdb
        dbi = MySQLdb
    except ImportError:
        import pymysql_sa
        pymysql_sa.make_default_mysql_dialect()
        import pymysql
        dbi = pymysql

    if not options.avoid_real:
        weblab_db_str = 'mysql://%s:%s@localhost/%sWebLab' % (weblab_db_username, weblab_db_password, prefix)
        weblab_test_db_str = 'mysql://%s:%s@localhost/%sWebLabTests%s' % (weblab_db_username, weblab_db_password, prefix, '%s')
    weblab_coord_db_str = 'mysql://%s:%s@localhost/%sWebLabCoordination%s' % (core_coordinator_db_username, core_coordinator_db_password, prefix, '%s')
    weblab_sessions_db_str = 'mysql://%s:%s@localhost/%sWebLabSessions' % (weblab_sessions_db_username, weblab_sessions_db_password, prefix)

    def _connect(admin_username, admin_password):
        try:
            return dbi.connect(user = admin_username, passwd = admin_password)
        except dbi.OperationalError, oe:
            traceback.print_exc()
            print >> sys.stderr, ""
            print >> sys.stderr, "    Tip: did you run create_weblab_administrator.py first?"
            print >> sys.stderr, ""
            sys.exit(-1)


    def create_database(admin_username, admin_password, database_name, new_user, new_password, host = "localhost"):
        args = {
                'DATABASE_NAME' : database_name,
                'USER'          : new_user,
                'PASSWORD'      : new_password,
                'HOST'          : host
            }


        sentence1 = "DROP DATABASE IF EXISTS %(DATABASE_NAME)s;" % args
        sentence2 = "CREATE DATABASE %(DATABASE_NAME)s;" % args
        sentence3 = "GRANT ALL ON %(DATABASE_NAME)s.* TO %(USER)s@%(HOST)s IDENTIFIED BY '%(PASSWORD)s';" % args
        
        try:
            dbi.connect(db=database_name, user = admin_username, passwd = admin_password).close()
        except dbi.OperationalError, e:
            if e[1].startswith("Unknown database"):
                sentence1 = "SELECT 1"

        for sentence in (sentence1, sentence2, sentence3):
            connection = _connect(admin_username, admin_password)
            cursor = connection.cursor()
            cursor.execute(sentence)
            connection.commit()
            connection.close()

elif db_engine == 'sqlite':
    import sqlite3
    dbi = sqlite3

    db_dir = os.sep.join(('..','db'))

    if not os.path.exists(db_dir):
        os.mkdir(db_dir)

    if not options.avoid_real:
        weblab_db_str = 'sqlite:///../db/%sWebLab.db' % prefix
        weblab_test_db_str = 'sqlite:///../db/%sWebLabTests%s.db' % (prefix, '%s')
    weblab_coord_db_str = 'sqlite:///../db/%sWebLabCoordination%s.db' % (prefix, '%s')
    weblab_sessions_db_str = 'sqlite:///../db/%sWebLabSessions.db' % prefix

    def create_database(admin_username, admin_password, database_name, new_user, new_password, host = "localhost"):
        fname = os.sep.join((db_dir, '%s.db' % database_name))
        if os.path.exists(fname):
            os.remove(fname)
        sqlite3.connect(database = fname).close()

else:
    raise Exception("db engine %s not supported" % db_engine)

t = time.time()

if not options.avoid_real:
    create_database(wac.wl_admin_username, wac.wl_admin_password, "%sWebLab" % prefix,              weblab_db_username, weblab_db_password)
    create_database(wac.wl_admin_username, wac.wl_admin_password, "%sWebLabTests" % prefix,         weblab_db_username, weblab_db_password)
    create_database(wac.wl_admin_username, wac.wl_admin_password, "%sWebLabTests2" % prefix,        weblab_db_username, weblab_db_password)
    create_database(wac.wl_admin_username, wac.wl_admin_password, "%sWebLabTests3" % prefix,        weblab_db_username, weblab_db_password)
create_database(wac.wl_admin_username, wac.wl_admin_password, "%sWebLabCoordination" % prefix,  core_coordinator_db_username, core_coordinator_db_password)
create_database(wac.wl_admin_username, wac.wl_admin_password, "%sWebLabCoordination2" % prefix, core_coordinator_db_username, core_coordinator_db_password)
create_database(wac.wl_admin_username, wac.wl_admin_password, "%sWebLabCoordination3" % prefix, core_coordinator_db_username, core_coordinator_db_password)
create_database(wac.wl_admin_username, wac.wl_admin_password, "%sWebLabSessions" % prefix,      weblab_sessions_db_username, weblab_sessions_db_password)

print "Databases created.\t\t\t\t[done] [%1.2fs]" % (time.time() - t)

#####################################################################
# 
# Populating main database
# 

if not options.avoid_real:
    print "Populating 'WebLab' database...   \t\t", 

    t = time.time()

    engine = create_engine(weblab_db_str, echo = False)
    metadata = Model.Base.metadata
    metadata.drop_all(engine)
    metadata.create_all(engine)

    insert_required_initial_data(engine)

    print "[done] [%1.2fs]" % (time.time() - t)

if not options.avoid_real:
    for tests in ('','2','3'):
        print "Populating 'WebLabTests%s' database...   \t\t" % tests, 
        t = time.time()

        engine = create_engine(weblab_test_db_str % tests, echo = False)
        metadata = Model.Base.metadata
        metadata.drop_all(engine)
        metadata.create_all(engine)

        insert_required_initial_data(engine)
        populate_weblab_tests(engine, tests)

        print "[done] [%1.2fs]" % (time.time() - t)



#####################################################################
# 
# Populating Coordination database
# 

for coord in ('','2','3'):
    print "Populating 'WebLabCoordination%s' database...\t" % coord,
    t = time.time()

    engine = create_engine(weblab_coord_db_str % coord, echo = False)

    CoordinatorModel.load()

    metadata = CoordinatorModel.Base.metadata
    metadata.drop_all(engine)
    metadata.create_all(engine)    

    print "[done] [%1.2fs]" % (time.time() - t)


#####################################################################
# 
# Populating Sessions database
# 


print "Populating 'WebLabSessions' database...\t\t",
t = time.time()

engine = create_engine(weblab_sessions_db_str, echo = False)

metadata = DbLockData.SessionLockBase.metadata
metadata.drop_all(engine)
metadata.create_all(engine)    

metadata = SessionSqlalchemyData.SessionBase.metadata
metadata.drop_all(engine)
metadata.create_all(engine)   

print "[done] [%1.2fs]" % (time.time() - t)

print "Total database deployment: \t\t\t[done] [%1.2fs]" % (time.time() - t_initial)

