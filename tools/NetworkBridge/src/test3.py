# Try the wait(), signal() mechanics.
import gevent
import gevent.event as event
from gevent.event import Event

ar = event.AsyncResult()


def g_wait_for_response():
    gevent.sleep(1)
    print "REQUEST SENT"
    ar.wait()
    print "RESPONSE HANDLED"
    print "IT IS: " + ar.get()

def g_emit_response():
    gevent.sleep(6)
    print "RESPONSE RECEIVED"
    ar.set("THIS IS GOOD")


gwaiter = gevent.spawn(g_wait_for_response)
gemitter = gevent.spawn(g_emit_response)


gevent.joinall([gwaiter, gemitter], timeout=10)