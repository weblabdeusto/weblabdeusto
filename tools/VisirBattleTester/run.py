#!/usr/local/env python

import time
import numpy as np
import sys, os
import cPickle as pickle
from multiprocessing import Pool

sys.path.append(os.sep.join(('..','..','server','src')))

from visir_tester import Tester

# EXECUTIONS = 15
# PROCESSES  = 80
URL = "http://www.weblab.deusto.es/weblab/"
USERNAME = "tester"
PASSWORD = "t3st3r6"

EXECUTIONS =  2
PROCESSES  =  10
# URL = "http://localhost/weblab/"
# USERNAME = "any"
# PASSWORD = "password"

def f(n):
    time.sleep(0.01 * n)
    tester = Tester(URL, USERNAME, PASSWORD, EXECUTIONS)
    result = tester.run()
    return result


if __name__ == '__main__':    
    n = PROCESSES
    pool = Pool(n)
    results = pool.map(f, range(n))
    failed = 0
    time_results = [0]
    for result in results:
        if result.failed:
            failed += 1
        time_results.extend(result.times)
    
    msg = ""
    msg += "Failed %s of %s\n"   % (failed, len(results))
    msg += "Max time: %.3f s\n"  % np.max(time_results)
    msg += "Min time: %.3f s\n"  % np.min(time_results)
    msg += "Mean time: %.3f s\n" % np.mean(time_results)
    msg += "Std time: %.3f\n"    % np.std(time_results)
    print msg
    print >> sys.stderr, msg

    pickle.dump(results, open("results.dump","w"))
    pickle.dump(time_results, open("time_results.dump","w"))
