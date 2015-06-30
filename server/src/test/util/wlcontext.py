from __future__ import print_function, unicode_literals
import threading
from weblab.core.wl import weblab_api

"""
The target is to forget all the internal things of weblab / Flask and be able
to run things like:

with wlcontext(server, reservation_id = reservation_id):
    list_experiments()
"""

class wlcontext(object):
    def __init__(self, server, session_id = None, reservation_id = None):
        self.server = server
        self.session_id = session_id
        self.reservation_id = reservation_id
        self.local = threading.local()

    def __enter__(self):
        self.local.request_context = self.server.app.test_request_context()
        self.local.request_context.__enter__()
        kwargs = { 'server_instance' : self.server }
        if self.session_id:
            if isinstance(self.session_id, basestring): 
                kwargs['session_id'] = self.session_id
            else:
                kwargs['session_id'] = self.session_id.id
        if self.reservation_id:
            if isinstance(self.reservation_id, basestring): 
                kwargs['reservation_id'] = self.reservation_id
            else:
                kwargs['reservation_id'] = self.reservation_id.id
        self.local.weblab_api = weblab_api(**kwargs)
        self.local.weblab_api.__enter__()

    initialize = __enter__

    def __exit__(self, exc_type, exc_value, traceback):
        self.local.weblab_api.__exit__(exc_type, exc_value, traceback)
        self.local.request_context.__exit__(exc_type, exc_value, traceback)

    def dispose(self):
        self.__exit__(None, None, None)

