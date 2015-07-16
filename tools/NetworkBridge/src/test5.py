


from gevent import server
import gevent


def handle(socket, addr):
    print "Connected"
    gevent.sleep(60)

s = server.StreamServer(("localhost", 2345), handle)
s.start()


gevent.sleep(10)

s.stop()


gevent.sleep(200)