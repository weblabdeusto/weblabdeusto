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

from weblab.admin.deploy import insert_required_initial_data, populate_weblab_tests, generate_create_database

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

db_dir = os.path.join('..','db')

if not os.path.exists(db_dir):
    os.mkdir(db_dir)

if db_engine == 'mysql':
    if not options.avoid_real:
        weblab_db_str = 'mysql://%s:%s@localhost/%sWebLab' % (weblab_db_username, weblab_db_password, prefix)
        weblab_test_db_str = 'mysql://%s:%s@localhost/%sWebLabTests%s' % (weblab_db_username, weblab_db_password, prefix, '%s')
    weblab_coord_db_str = 'mysql://%s:%s@localhost/%sWebLabCoordination%s' % (core_coordinator_db_username, core_coordinator_db_password, prefix, '%s')
    weblab_sessions_db_str = 'mysql://%s:%s@localhost/%sWebLabSessions' % (weblab_sessions_db_username, weblab_sessions_db_password, prefix)

elif db_engine == 'sqlite':
    if not options.avoid_real:
        weblab_db_str = 'sqlite:///../db/%sWebLab.db' % prefix
        weblab_test_db_str = 'sqlite:///../db/%sWebLabTests%s.db' % (prefix, '%s')
    weblab_coord_db_str = 'sqlite:///../db/%sWebLabCoordination%s.db' % (prefix, '%s')
    weblab_sessions_db_str = 'sqlite:///../db/%sWebLabSessions.db' % prefix

else:
    raise Exception("db engine %s not supported" % db_engine)

create_database = generate_create_database(db_engine)
if create_database is None:
    raise Exception("db engine %s not supported for creating database" % db_engine)

t = time.time()

if not options.avoid_real:
    create_database(wac.wl_admin_username, wac.wl_admin_password, "%sWebLab" % prefix,              weblab_db_username, weblab_db_password, db_dir = db_dir)
    create_database(wac.wl_admin_username, wac.wl_admin_password, "%sWebLabTests" % prefix,         weblab_db_username, weblab_db_password, db_dir = db_dir)
    create_database(wac.wl_admin_username, wac.wl_admin_password, "%sWebLabTests2" % prefix,        weblab_db_username, weblab_db_password, db_dir = db_dir)
    create_database(wac.wl_admin_username, wac.wl_admin_password, "%sWebLabTests3" % prefix,        weblab_db_username, weblab_db_password, db_dir = db_dir)

create_database(wac.wl_admin_username, wac.wl_admin_password, "%sWebLabCoordination" % prefix,  core_coordinator_db_username, core_coordinator_db_password, db_dir = db_dir)
create_database(wac.wl_admin_username, wac.wl_admin_password, "%sWebLabCoordination2" % prefix, core_coordinator_db_username, core_coordinator_db_password, db_dir = db_dir)
create_database(wac.wl_admin_username, wac.wl_admin_password, "%sWebLabCoordination3" % prefix, core_coordinator_db_username, core_coordinator_db_password, db_dir = db_dir)
create_database(wac.wl_admin_username, wac.wl_admin_password, "%sWebLabSessions" % prefix,      weblab_sessions_db_username, weblab_sessions_db_password, db_dir = db_dir)

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

