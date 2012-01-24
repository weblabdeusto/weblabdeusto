#!/usr/local/env python

import time
import numpy as np
import sys, os
import cPickle as pickle
from multiprocessing import Pool

sys.path.append(os.sep.join(('..','..','server','src')))

import libraries
from visir_tester import Tester

EXECUTIONS =  15
PROCESSES  =  50

def f(n):
    time.sleep(0.01 * n)
    tester = Tester("http://www.weblab.deusto.es/weblab/", "tester", "t3st3r6", EXECUTIONS)
    result = tester.run()
    return result

if __name__ == '__main__':
    n = PROCESSES
    pool = Pool(n)
    results = pool.map(f, range(n))
    failed = 0
    time_results = []
    for result in results:
        if result.failed:
            failed += 1
        time_results.extend(result.times)
    
    print "Failed %s of %s"   % (failed, len(results))
    print "Max time: %.3f s"  % np.max(time_results)
    print "Min time: %.3f s"  % np.min(time_results)
    print "Mean time: %.3f s" % np.mean(time_results)
    print "Std time: %.3f"    % np.std(time_results)

    pickle.dump(results, open("results.dump","w"))
    pickle.dump(time_results, open("time_results.dump","w"))
