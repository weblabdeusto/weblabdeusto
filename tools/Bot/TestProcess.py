import sys
import os
sys.path.append(os.sep.join(('..','..','server','src')))

import time

import libraries

from weblab.admin.bot.WebLabProcess import WebLabProcess

for i in xrange(10):
    try:
        wl = WebLabProcess(('..','..','server','src'), 'launch_sample.py')
        wl.start()
        print i, "start"
    except Exception, e:
        print "Error:", e
    finally:
        wl.shutdown()
        print i, "shutdown"
        print
