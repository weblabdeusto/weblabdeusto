#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 onwards University of Deusto
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#
# This software consists of contributions made by many individuals,
# listed below:
#
# Author: Pablo Orduña <pablo@ordunya.com>
#         Luis Rodriguez <luis.rodriguezgil@deusto.es>
#
from __future__ import print_function, unicode_literals

import threading
import traceback
import unittest
import time

from test.util.script import ServerCreator

from weblab.core.reservations import WaitingReservation, ConfirmedReservation, WaitingConfirmationReservation
from weblab.data.command import Command
from weblab.data.experiments import ExperimentId

class ScriptTestCase(unittest.TestCase):
    def test_simple(self):
        with ServerCreator(u"--cores=1") as sc:
            client = sc.create_client()
            session_id = client.login(u'admin', u'password')
            self.assertNotEquals(session_id, None)

    def test_multiple_cores_20_users_sql(self):
        with ServerCreator(u"--cores=1 --db-engine=mysql --db-name=WebLabIntTests1 --db-user=weblab --db-passwd=weblab --coordination-engine=sql --dummy-silent") as sc:

            tester = ExperimentUseTester(sc, 20, 'admin', 'password', 'dummy', 'Dummy experiments')
            failures, max_users = tester.run()
            self.assertEquals(failures, 0)
            self.assertEquals(max_users, 1)

    def test_multiple_cores_20_users_redis(self):
        with ServerCreator(u"--cores=1 --db-engine=mysql --db-name=WebLabIntTests1 --db-user=weblab --db-passwd=weblab --coordination-engine=redis --dummy-silent") as sc:
            tester = ExperimentUseTester(sc, 20, 'admin', 'password', 'dummy', 'Dummy experiments')
            failures, max_users = tester.run()
            self.assertEquals(failures, 0)
            self.assertEquals(max_users, 1)

    def test_multiple_cores_20_users_redis_4_cores(self):
        with ServerCreator(u"--cores=4 --db-engine=mysql --db-name=WebLabIntTests1 --db-user=weblab --db-passwd=weblab --coordination-engine=redis --dummy-silent") as sc:
            tester = ExperimentUseTester(sc, 20, 'admin', 'password', 'dummy', 'Dummy experiments')
            failures, max_users = tester.run()
            self.assertEquals(failures, 0)
            self.assertEquals(max_users, 1)


class ExperimentUseTester(object):

    def __init__(self, server_creator, concurrent_users, user, password, exp_name, cat_name, max_time = 180, fail_on_concurrency = True, quiet_errors = True):
        self.users_in = 0
        self.failures = 0
        self.clients = []
        for n in xrange(concurrent_users):
            client = server_creator.create_client()
            self.clients.append(client)

        self.concurrent_users = concurrent_users
        self.user = user
        self.password = password
        self.exp_name = exp_name
        self.cat_name = cat_name
        self.max_time = max_time
        self.fail_on_concurrency = fail_on_concurrency
        self.quiet_errors = quiet_errors

    def run(self):
        threads = []
        for n in xrange(self.concurrent_users):
            thread = threading.Thread(target = self.run_wrapped, args = (n,))
            thread.setDaemon(True)
            thread.start()
            threads.append(thread)

        initial_time = time.time()
        max_users = 0
        
        while True:
            time.sleep(0.1)

            max_users = max(self.users_in, max_users)
            if self.fail_on_concurrency and max_users > 1:
                raise Exception("More than one concurrent users using the same non-concurrent lab!")

            any_alive = False
            for thread in threads:
                if thread.isAlive():
                    any_alive = True
                    break
            
            if not any_alive:
                break
    
            if (time.time() - initial_time) > (self.max_time + 10):
                raise Exception("Threads still running after %s seconds!" % (self.max_time + 10))

        return self.failures, max_users

    def run_wrapped(self, user_number):
        try:
            self.do_full_experiment_use(user_number)
        except:
            if not self.quiet_errors:
                traceback.print_exc()
            else:
                print("Error not shown since quiet_errors = True")
            self.failures += 1

    def do_full_experiment_use(self, user_number):
        """
        Uses the configured experiment trying to resemble the way a human would do it.
        This method will block for a while.
        :return:
        """
        client = self.clients[user_number]
        sessionid = client.login(self.user, self.password)
        if not sessionid:
            raise Exception("Wrong login")

        # Reserve the flash dummy experiment.
        experiment_id = ExperimentId(self.exp_name, self.cat_name)
        waiting = client.reserve_experiment(sessionid, experiment_id, "{}", "{}", None)
        # print "Reserve response: %r" % waiting

        reservation_id = waiting.reservation_id

        initial_time = time.time()

        while (time.time() - initial_time) < self.max_time:
            status = client.get_reservation_status(reservation_id)

            if type(status) is WaitingReservation:
                time.sleep(0.1)
            elif type(status) is ConfirmedReservation:
                break
            elif type(status) is WaitingConfirmationReservation:
                time.sleep(0.1)

        if (time.time() - initial_time) >= self.max_time:
            raise Exception("Max time (%s seconds) achieved and still waiting..." % self.max_time)

        self.users_in += 1

        # Send some commands.

        for i in range(20):
            # What's commandstring actually for??
            cmd = Command("foo")
            result = client.send_command(reservation_id, cmd)
            if not result.commandstring.startswith("Received command"):
                raise Exception("Unrecognized command response")
            # print "Command result: %r" % result
            time.sleep(0.1)

        self.users_in -= 1

        result = client.logout(sessionid)


def suite():
    return unittest.makeSuite(ScriptTestCase)

if __name__ == '__main__':
    unittest.main()
