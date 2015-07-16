
from gevent import monkey
import gevent

monkey.patch_all()

from gevent import pywsgi
import socket

def handle_request(env, start_response):
    start_response('200', [('Content-Type', 'text/plain')])
    return ['HELLO']

server = pywsgi.WSGIServer(('127.0.0.1', 0), handle_request)
server.start()

sock = socket.create_connection(('127.0.0.1', server.server_port))
fd = sock.makefile('rwb')

def do_http_request(fd):
    fd.write(b'GET / HTTP/1.1\r\n\r\n')
    fd.flush()

    r = fd.readline()
    while len(r.strip()) > 0:
        r = fd.readline()
        print("\tFrom server:", r, '\n')

# First one works fine, server is listening
do_http_request(fd)

# Stop the server
server.stop()

do_http_request(fd)

do_http_request(fd)
