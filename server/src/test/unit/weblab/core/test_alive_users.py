#!/usr/bin/env python
#-*-*- encoding: utf-8 -*-*-
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
from __future__ import print_function, unicode_literals

import unittest
import time
import Queue

import test.unit.configuration as configuration_module

import test.unit.weblab.core.test_user_processor as UserProcessorTest

import voodoo.configuration as ConfigurationManager
import voodoo.sessions.manager as SessionManager
import voodoo.sessions.session_type as SessionType
import voodoo.sessions.session_id   as SessionId

import weblab.core.user_processor as UserProcessor
import weblab.core.coordinator.store as TemporalInformationStore
import weblab.core.alive_users as AliveUsersCollection

class TimeModule(object):
    def __init__(self):
        self._next_value = time.time()

    def set(self, next_value):
        self._next_value = next_value

    def time(self):
        return self._next_value

class DummyCoordinator(object):
    def is_post_reservation(self, reservation_id):
        return False

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
        coordinator = DummyCoordinator()

        self.finished_reservations_store = Queue.Queue()

        self.auc     = AliveUsersCollection.AliveUsersCollection(
                    locator,
                    cfg_manager,
                    SessionType.Memory,
                    self.session_mgr,
                    coordinator,
                    commands_store,
                    self.finished_reservations_store
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

    def create_session(self, timestamp):
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

    def test_finished_sessions(self):
        session_id1 = self.create_session(self.tm.time())
        session_id2 = self.create_session(self.tm.time())

        self.auc.add_user(session_id1)
        self.auc.add_user(session_id2)

        expired_users = self.auc.check_expired_users()
        self.assertEquals(0, len(expired_users))

        self.finished_reservations_store.put(session_id1)

        expired_users = self.auc.check_expired_users()
        self.assertEquals(1, len(expired_users))
        self.assertEquals(session_id1, expired_users[0])

    def test_finished_sessions2(self):
        session_id1 = self.create_session(self.tm.time() - 3600) # expired
        session_id2 = self.create_session(self.tm.time()) # expired

        self.auc.add_user(session_id1)
        self.auc.add_user(session_id2)

        self.finished_reservations_store.put(session_id2)

        expired_users = self.auc.check_expired_users()

        self.assertEquals(2, len(expired_users))
        self.assertEquals(session_id2, expired_users[0])
        self.assertEquals(session_id1, expired_users[1])

        expired_users = self.auc.check_expired_users()
        self.assertEquals(0, len(expired_users))

    def test_three_sessions_one_expired(self):
        session_id1 = self.create_session(self.tm.time())
        session_id2 = self.create_session(self.tm.time() - 3600) # expired
        session_id3 = self.create_session(self.tm.time())

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
        session_id1 = self.create_session(self.tm.time())
        session_id2 = self.create_session(self.tm.time() - 3600) # expired
        session_id3 = self.create_session(self.tm.time())

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

