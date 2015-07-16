import gevent
from lab_bridge.comms.lab.LabListener import LabListener

import gc
import gevent
from greenlet import greenlet

ll = LabListener("exp1", "127.0.0.1", 10501, "exp1")
ll.start()
gevent.sleep(10)
ll.stop()

print "STOPPED, SUPPOSEDLY"
gevent.sleep(60)
print "STARTING AGAIN"

ll = LabListener("exp1", "127.0.0.1", 10501, "exp1")
ll.start()

gevent.sleep(80)