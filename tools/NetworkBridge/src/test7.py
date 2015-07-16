

import gevent
from gevent import pywsgi

listen_host = "127.0.0.1"
listen_port = 3456

def on_http_request(environ, start_response):
    start_response('200', [('Content-Type', 'text/html')])
    return ["This server accepts ExperimentServer-like methods"]

server = pywsgi.WSGIServer((listen_host, listen_port), on_http_request)


server.start()


gevent.sleep(10)


server.stop()
print "Out"

gevent.sleep(10)
print "Real out"