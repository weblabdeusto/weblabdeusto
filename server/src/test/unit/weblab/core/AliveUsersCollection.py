#!/usr/bin/env python
#-*-*- encoding: utf-8 -*-*-
#
# Copyright (C) 2005-2009 University of Deusto
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

import unittest
import time

import test.unit.configuration as configuration_module

# TODO: this referes to the test code; replace this
import UserProcessor as UserProcessorTest

import voodoo.configuration.ConfigurationManager as ConfigurationManager
import voodoo.sessions.manager as SessionManager
import voodoo.sessions.SessionType as SessionType
import voodoo.sessions.SessionId   as SessionId

import weblab.core.processor as UserProcessor
import weblab.core.coordinator.store as TemporalInformationStore
import weblab.core.alive_users as AliveUsersCollection

class TimeModule(object):
    def __init__(self):
        self._next_value = time.time()

    def set(self, next_value):
        self._next_value = next_value

    def time(self):
        return self._next_value

class AliveUsersCollectionTestCase(unittest.TestCase):
    def setUp(self):
        cfg_manager = ConfigurationManager.ConfigurationManager()
        cfg_manager.append_module(configuration_module)

        commands_store = TemporalInformationStore.CommandsTemporalInformationStore()

        locator          = UserProcessorTest.FakeLocator(None)
        self.session_mgr = SessionManager.SessionManager(
                    cfg_manager,
                    SessionType.Memory,
                    "foo"
                )
        db_manager       = None

        self.auc     = AliveUsersCollection.AliveUsersCollection(
                    locator,
                    cfg_manager,
                    SessionType.Memory,
                    self.session_mgr,
                    db_manager,
                    commands_store
                )

        self.tm      = TimeModule()

        self.auc._time_module = self.tm

    def test_add(self):
        session_id = SessionId.SessionId("my session")

        self.auc.add_user(session_id)
        self.auc.add_user(session_id) # no exception

    def test_remove(self):
        session_id = SessionId.SessionId("my session")

        self.auc.add_user(session_id)
        self.auc.remove_user(session_id)
        self.auc.remove_user(session_id) # No exception

    def test_three_sessions_one_expired(self):
        def create_session(timestamp):
            session_id = self.session_mgr.create_session()
            self.session_mgr.modify_session(
                    session_id,
                    {
                        'db_session_id'   : 'whatever',
                        'session_polling' : (
                            timestamp,
                            UserProcessor.UserProcessor.EXPIRATION_TIME_NOT_SET
                        )
                    }
                )
            return session_id

        session_id1 = create_session(self.tm.time())
        session_id2 = create_session(self.tm.time() - 3600) # expired
        session_id3 = create_session(self.tm.time())

        self.auc.add_user(session_id1)
        self.auc.add_user(session_id2)
        self.auc.add_user(session_id3)

        expired_users = self.auc.check_expired_users()
        self.assertEquals(1, len(expired_users))
        self.assertEquals(session_id2, expired_users[0])

        expired_users = self.auc.check_expired_users()
        self.assertEquals(0, len(expired_users))

        # Some time passes with same results
        self.tm.set(self.tm.time() + self.auc._min_time_between_checks + 1)

        expired_users = self.auc.check_expired_users()
        self.assertEquals(0, len(expired_users))

    def test_three_sessions_one_expired_and_then_another_before_time_passes(self):
        def create_session(timestamp):
            session_id = self.session_mgr.create_session()
            self.session_mgr.modify_session(
                    session_id,
                    {
                        'db_session_id'   : 'whatever',
                        'session_polling' : (
                            timestamp,
                            UserProcessor.UserProcessor.EXPIRATION_TIME_NOT_SET
                        )
                    }
                )
            return session_id

        session_id1 = create_session(self.tm.time())
        session_id2 = create_session(self.tm.time() - 3600) # expired
        session_id3 = create_session(self.tm.time())

        self.auc.add_user(session_id1)
        self.auc.add_user(session_id2)
        self.auc.add_user(session_id3)

        expired_users = self.auc.check_expired_users()
        self.assertEquals(1, len(expired_users))
        self.assertEquals(session_id2, expired_users[0])

        expired_users = self.auc.check_expired_users()
        self.assertEquals(0, len(expired_users))

        session = self.session_mgr.get_session(session_id3)
        session['session_polling'] = (
                self.tm.time() - 3600, # Expired
                UserProcessor.UserProcessor.EXPIRATION_TIME_NOT_SET
            )
        self.session_mgr.modify_session(
                session_id3,
                session
            )

        # Still it doesn't find it!
        expired_users = self.auc.check_expired_users()
        self.assertEquals(0, len(expired_users))

        # Some time passes
        self.tm.set(self.tm.time() + self.auc._min_time_between_checks + 1)

        # And now it finds the new expired session
        expired_users = self.auc.check_expired_users()
        self.assertEquals(1, len(expired_users))

        self.assertEquals(session_id3, expired_users[0])


def suite():
    return unittest.makeSuite(AliveUsersCollectionTestCase)

if __name__ == '__main__':
    unittest.main()

