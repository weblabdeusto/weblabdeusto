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
import threading

import voodoo.lock as lock

VERY_SHORT_TIMEOUT = 0.2
SHORT_TIMEOUT = 1

class RWLockTestCase(unittest.TestCase):
    def test_rw_lock_basic(self):
        rwlock = lock.RWLock()

        rlock  = rwlock.read_lock()
        wlock  = rwlock.write_lock()

        rlock.acquire()
        rlock.release()

        wlock.acquire()
        wlock.release()

    def test_rw_lock_multiple_reads(self):
        rwlock = lock.RWLock()

        rlock  = rwlock.read_lock()

        evt    = threading.Event()

        rlock.acquire()
        class RLockThread(threading.Thread):
            def run(self):
                rlock.acquire()
                evt.set()

        thread = RLockThread()
        thread.setDaemon(True)
        thread.start()
        evt.wait(SHORT_TIMEOUT)
        self.assertTrue(evt.isSet())
        thread.join()

    def test_rw_lock_only_one_write(self):
        rwlock = lock.RWLock()

        wlock  = rwlock.write_lock()

        evt1   = threading.Event()
        evt2   = threading.Event()

        wlock.acquire()
        class RLockThread(threading.Thread):
            def run(self):
                evt1.set()
                wlock.acquire()
                evt2.set()

        thread = RLockThread()
        thread.setDaemon(True)
        thread.start()
        evt1.wait(SHORT_TIMEOUT)
        self.assertTrue(evt1.isSet())
        evt2.wait(VERY_SHORT_TIMEOUT)
        self.assertFalse(evt2.isSet())

        # Cleaning up
        wlock.release()
        thread.join()

    def test_rw_lock_reentrant_one_write(self):
        rwlock = lock.RWLock()

        wlock  = rwlock.write_lock()

        evt1   = threading.Event()
        evt2   = threading.Event()

        wlock.acquire()
        class RLockThread(threading.Thread):
            def run(self):
                evt1.set()
                wlock.acquire()
                evt2.set()

        thread = RLockThread()
        thread.setDaemon(True)
        thread.start()
        evt1.wait(SHORT_TIMEOUT)
        self.assertTrue(evt1.isSet())
        evt2.wait(VERY_SHORT_TIMEOUT)
        self.assertFalse(evt2.isSet())
        # I don't have any problem
        wlock.acquire()
        # And I can release and the other thread is still there
        wlock.release()
        evt2.wait(VERY_SHORT_TIMEOUT)
        self.assertFalse(evt2.isSet())
        # The second time it works
        wlock.release()
        evt2.wait(SHORT_TIMEOUT)
        self.assertTrue(evt2.isSet())
        thread.join()
        # Everyone is now happy

    def test_rw_lock_reentrant_reading_while_write_locked(self):
        rwlock = lock.RWLock()
        rlock = rwlock.read_lock()
        wlock = rwlock.write_lock()

        wlock.acquire()
        rlock.acquire()
        rlock.release()
        wlock.release()
        # Everyone is happy

    def test_rw_lock_no_write_when_reading(self):
        rwlock = lock.RWLock()

        rlock  = rwlock.read_lock()
        wlock  = rwlock.write_lock()

        evt1   = threading.Event()
        evt2   = threading.Event()

        rlock.acquire()
        class RLockThread(threading.Thread):
            def run(self):
                evt1.set()
                wlock.acquire()
                evt2.set()

        thread = RLockThread()
        thread.setDaemon(True)
        thread.start()
        evt1.wait(SHORT_TIMEOUT)
        self.assertTrue(evt1.isSet())
        evt2.wait(VERY_SHORT_TIMEOUT)
        self.assertFalse(evt2.isSet())

        # Cleaning
        rlock.release()
        thread.join()

    def test_rw_lock_no_read_when_writing(self):
        rwlock = lock.RWLock()

        rlock  = rwlock.read_lock()
        wlock  = rwlock.write_lock()

        evt1   = threading.Event()
        evt2   = threading.Event()

        wlock.acquire()
        class RLockThread(threading.Thread):
            def run(self):
                evt1.set()
                rlock.acquire()
                evt2.set()

        thread = RLockThread()
        thread.setDaemon(True)
        thread.start()
        evt1.wait(SHORT_TIMEOUT)
        self.assertTrue(evt1.isSet())
        evt2.wait(VERY_SHORT_TIMEOUT)
        self.assertFalse(evt2.isSet())

        # Cleaning
        wlock.release()
        thread.join()

    def test_rw_write_write(self):
        rwlock = lock.RWLock()
        wlock  = rwlock.write_lock()
        wlock.acquire()
        wlock.release()
        wlock.acquire()
        wlock.release()

    def test_rw_write_read(self):
        rwlock = lock.RWLock()
        rlock  = rwlock.read_lock()
        wlock  = rwlock.write_lock()
        wlock.acquire()
        wlock.release()
        rlock.acquire()
        rlock.release()

    def test_rw_lock_read_read_write(self):
        rwlock = lock.RWLock()

        rlock  = rwlock.read_lock()
        wlock  = rwlock.write_lock()

        evt1r   = threading.Event()
        evt2r   = threading.Event()
        evt3r   = threading.Event()
        evt4r   = threading.Event()

        class RLockThread(threading.Thread):
            def run(self):
                evt1r.set()
                rlock.acquire()
                evt2r.set()
                evt3r.wait(SHORT_TIMEOUT * 2)
                rlock.release()
                evt4r.set()

        evt1w   = threading.Event()
        evt2w   = threading.Event()
        evt3w   = threading.Event()

        class WLockThread(threading.Thread):
            def run(self):
                evt1w.set()
                evt2w.wait(SHORT_TIMEOUT * 2)
                wlock.acquire()
                evt3w.set()

        threadR = RLockThread()
        threadR.setDaemon(True)
        threadW = WLockThread()
        threadW.setDaemon(True)

        rlock.acquire()

        threadR.start()
        threadW.start()

        evt1r.wait(SHORT_TIMEOUT)
        self.assertTrue(evt1r.isSet())
        evt2r.wait(SHORT_TIMEOUT)
        self.assertTrue(evt2r.isSet())

        evt1w.wait(SHORT_TIMEOUT)
        self.assertTrue(evt1w.isSet())
        evt2w.set()

        evt3w.wait(VERY_SHORT_TIMEOUT)
        self.assertFalse(evt3w.isSet())

        # Everybody did an acquire
        # WLockThread is locked until
        # we do a couple of releases

        rlock.release()

        # Not yet...
        evt3w.wait(VERY_SHORT_TIMEOUT)
        self.assertFalse(evt3w.isSet())

        evt3r.set()
        evt4r.wait(VERY_SHORT_TIMEOUT)
        self.assertTrue(evt4r.isSet())

        # Now yes

        evt3w.wait(VERY_SHORT_TIMEOUT)
        self.assertTrue(evt3w.isSet())


def suite():
    return unittest.makeSuite(RWLockTestCase)

if __name__ == '__main__':
    unittest.main()

