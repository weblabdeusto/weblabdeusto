
import gevent
from gevent import socket
from gevent import Timeout
from lablistener import LabListener

lab = LabListener("localhost", 56789)

lab.start()













#
# exit(0)
#
# def printit():
#     timeout = Timeout(4, False)
#     timeout.start()
#     with timeout:
#         while True:
#             print("Hai")
#             gevent.sleep(3)
#         out = True
#
#
# glets = []
# glets.append(gevent.spawn(printit))
# glets.append(gevent.spawn(printit))
#
#
# gevent.joinall(glets, timeout=10)

