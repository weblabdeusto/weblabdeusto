from gevent import monkey
import gevent

monkey.patch_all()

from gevent import pywsgi
import socket

def application(env, start_response):
    start_response('200 OK', [('Content-Type', 'text/plain'), ('Content-Length', '11')])
    return [b'hello ', b'world']

server = pywsgi.WSGIServer(('127.0.0.1', 0), application)
server.start()

def talk_to_server():
    sock = socket.create_connection(('127.0.0.1', server.server_port))
    fd = sock.makefile('rwb')
    fd.write(b'GET / HTTP/1.0\r\n\r\n')
    fd.flush()
    print("\tFrom server:", fd.readline(), '\n')

# First one works fine, server is listening
talk_to_server()
print "First one worked"

# Stop the server
server.stop()

# This should now raise a socket error
try:
    talk_to_server()
except socket.error as se:
    print "Raised as expected"


gevent.sleep(2)