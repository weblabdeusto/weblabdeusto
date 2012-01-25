#!/usr/bin/python
# -*- coding: utf-8 -*-
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

import threading

import voodoo.sessions.manager       as SessionManager
import voodoo.sessions.memory as SessionMemoryGateway
import voodoo.sessions.session_type          as SessionType
import voodoo.sessions.session_id            as SessionId

import voodoo.sessions.exc as SessionExceptions

import test.unit.configuration as configuration_module
import voodoo.configuration as ConfigurationManager


class SessionManagerTestCase(unittest.TestCase):
    def setUp(self):
        cfg_manager= ConfigurationManager.ConfigurationManager()
        cfg_manager.append_module(configuration_module)

        cfg_manager._set_value(SessionMemoryGateway.SERIALIZE_MEMORY_GATEWAY_SESSIONS, True)

        self.memory_server1 = SessionManager.SessionManager(
                    cfg_manager,
                    SessionType.Memory,
                    "foo"
                )
        self.memory_server2 = SessionManager.SessionManager(
                    cfg_manager,
                    SessionType.Memory,
                    "bar"
                )
        self.sqlalchemy_server1 = SessionManager.SessionManager(
                    cfg_manager,
                    SessionType.sqlalchemy,
                    "foo"
                )
        self.sqlalchemy_server2 = SessionManager.SessionManager(
                    cfg_manager,
                    SessionType.sqlalchemy,
                    "bar"
                )

        self.memory_server1.clear()
        self.memory_server2.clear()
        self.sqlalchemy_server1.clear()
        self.sqlalchemy_server2.clear()

    def test_checking_parameter(self):
        self.assertRaises(
            SessionExceptions.SessionInvalidSessionTypeException,
            SessionManager.SessionManager,
            None,
            5,
            "foo"
        )
        self.assertRaises(
            SessionExceptions.SessionInvalidSessionIdException,
            self.memory_server1.get_session,
            'test'
        )
        self.assertRaises(
            SessionExceptions.SessionInvalidSessionIdException,
            self.memory_server1.get_session_locking,
            'test'
        )
        self.assertRaises(
            SessionExceptions.SessionInvalidSessionIdException,
            self.memory_server1.modify_session,
            'test',
            'something'
        )
        self.assertRaises(
            SessionExceptions.SessionInvalidSessionIdException,
            self.memory_server1.modify_session_unlocking,
            'test',
            'something'
        )
        self.assertRaises(
            SessionExceptions.SessionInvalidSessionIdException,
            self.memory_server1.delete_session,
            'test'
        )

    def test_session_id(self):
        self.assertRaises(
            SessionExceptions.SessionInvalidSessionIdException,
            SessionId.SessionId,
            5
        )

    def session_create_session_given_a_sess_id(self, server):
        # The first time works ok
        DESIRED_SESS_ID1 = '-pw0EvJ1+kEQ+WC2'
        sess_id1 = server.create_session(DESIRED_SESS_ID1)
        self.assertEquals(DESIRED_SESS_ID1, sess_id1)

        # The second time must fail
        self.assertRaises(
            SessionExceptions.DesiredSessionIdAlreadyExistsException,
            server.create_session, DESIRED_SESS_ID1
        )

    def session_tester(self,server):
        sess_id = server.create_session()
        information = { 'test':'mytest' }
        invalid_information = {'test':threading.Lock()}

        server.modify_session(sess_id,information)
        self.assertEquals(server.get_session(sess_id),information)

        self.assertRaises(
                SessionExceptions.SessionNotSerializableException,
                server.modify_session,
                sess_id,
                invalid_information
            )

        server.delete_session(sess_id)
        self.assertRaises(
                SessionExceptions.SessionNotFoundException,
                server.get_session,
                sess_id
            )
        self.assertRaises(
                SessionExceptions.SessionNotFoundException,
                server.modify_session,
                sess_id,
                ''
            )
        self.assertRaises(
                SessionExceptions.SessionNotFoundException,
                server.delete_session,
                sess_id
            )

    def session_tester_locking(self,server):
        sess_id = server.create_session()
        information = { 'test':'mytest' }

        server.modify_session(sess_id,information)

        session = server.get_session_locking(sess_id)
        session['test2'] = 'mytest2'
        server.modify_session_unlocking(sess_id, session)

        self.assertEquals(
                'mytest2',
                server.get_session(sess_id)['test2']
            )

    def session_tester_locking_2steps(self,server):
        sess_id = server.create_session()
        information = { 'test':'mytest' }

        server.modify_session(sess_id,information)

        session = server.get_session_locking(sess_id)
        session['test2'] = 'mytest2'
        server.modify_session(sess_id, session)
        server.unlock_without_modifying(sess_id)

        self.assertEquals(
                'mytest2',
                server.get_session(sess_id)['test2']
            )

    def session_tester_list_sessions(self, server):
        sess_id1 = server.create_session()
        sess_id2 = server.create_session()
        sess_id3 = server.create_session()

        sessions = server.list_sessions()
        self.assertEquals(3, len(sessions))

        self.assertTrue(sess_id1 in sessions)
        self.assertTrue(sess_id2 in sessions)
        self.assertTrue(sess_id3 in sessions)

    def session_tester_pool_ids(self, server1, server2):
        sess_id1 = server1.create_session()
        sess_id2 = server2.create_session()

        sessions1 = server1.list_sessions()
        self.assertEquals(1, len(sessions1))

        self.assertTrue(sess_id1 in sessions1)

        sessions2 = server2.list_sessions()
        self.assertEquals(1, len(sessions2))

        self.assertTrue(sess_id2 in sessions2)

        server1.clear()
        sessions2 = server2.list_sessions()
        self.assertEquals(1, len(sessions2))

        self.assertTrue(sess_id2 in sessions2)

        server2.clear()
        sessions2 = server2.list_sessions()
        self.assertEquals(0, len(sessions2))

    def test_memory_session(self):
        self.session_tester(self.memory_server1)

    def test_memory_session_locking(self):
        self.session_tester_locking(self.memory_server1)

    def test_memory_session_locking_2steps(self):
        self.session_tester_locking_2steps(self.memory_server1)

    def test_memory_session_list_sessions(self):
        self.session_tester_list_sessions(self.memory_server1)

    def test_memory_pool_ids(self):
        self.session_tester_pool_ids(self.memory_server1, self.memory_server2)

    def test_memory_create_session_given_a_sess_id(self):
        self.session_create_session_given_a_sess_id(self.memory_server1)

    def test_sqlalchemy_session(self):
        self.session_tester(self.sqlalchemy_server1)

    def test_sqlalchemy_session_locking(self):
        self.session_tester_locking(self.sqlalchemy_server1)

    def test_sqlalchemy_session_locking_2steps(self):
        self.session_tester_locking_2steps(self.sqlalchemy_server1)

    def test_sqlalchemy_session_list_sessions(self):
        self.session_tester_list_sessions(self.sqlalchemy_server1)

    def test_sqlalchemy_pool_ids(self):
        self.session_tester_pool_ids(self.sqlalchemy_server1, self.sqlalchemy_server2)

    def test_sqlalchemy_create_session_given_a_sess_id(self):
        self.session_create_session_given_a_sess_id(self.sqlalchemy_server1)


def suite():
    return unittest.makeSuite(SessionManagerTestCase)

if __name__ == '__main__':
    unittest.main()

