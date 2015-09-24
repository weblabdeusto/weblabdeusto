from __future__ import print_function, unicode_literals
import unittest

import test.util.stress as stress_util
from voodoo.log import logged

def avg(l):
    total = 0
    for element in l:
        total +=  element
    return 1.0 * total / len(l)

def next_max(l, n):
    new_list = l[:]
    new_list.sort()
    new_list.reverse()
    return new_list[:n]

class TestingLog(object):
    @logged()
    def normal_method(self, a, b):
        return a + b

    def normal_method_wrap(self):
        self.normal_method(1,2)

    @logged()
    def wrong_method(self):
        return 10 / 0

    def wrong_method_wrap(self):
        try:
            self.wrong_method()
        except ZeroDivisionError:
            pass

class LogTestCase(unittest.TestCase):
    def setUp(self):
        testing_log = TestingLog()
        self.runner_normal = stress_util.MainRunner(testing_log.normal_method_wrap, "testing_log_normal")
        self.runner_wrong = stress_util.MainRunner(testing_log.wrong_method_wrap, "testing_log_exc")

    def _show_results(self, l):
        return "max: %s; avg: %s; next max: %s" % (max(l), avg(l), next_max(l,4))

    def test_sequential_normal(self):
        iterations = 10000
        max_time   = 0.3
        print "seq_normal",self._show_results(self.runner_normal.run_sequential(iterations, max_time))

    def test_concurrent_normal(self):
        threads    = 200
        iterations =  50
        max_time   =   2 # And this is far too much
        print "con_normal",self._show_results(self.runner_normal.run_threaded(threads, iterations, max_time))

    def test_sequential_wrong(self):
        iterations = 10000
        max_time   = 0.3
        print "seq_wrong",self._show_results(self.runner_wrong.run_sequential(iterations, max_time))

    def test_concurrent_wrong(self):
        threads    = 200
        iterations =  50
        max_time   =   2 # And this is far too much
        print "con_wrong",self._show_results(self.runner_wrong.run_threaded(threads, iterations, max_time))


def suite():
    return unittest.makeSuite(LogTestCase)

if __name__ == '__main__':
    unittest.main()

