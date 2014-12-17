import json
import traceback
import threading

from functools import wraps
from collections import OrderedDict

from flask import Flask, request

from voodoo.log import log, level, log_exc
from weblab.comm.codes import WEBLAB_GENERAL_EXCEPTION_CODE

def get_json():
    if request.json is not None:
        return request.json
    else:
        try:
            if request.data:
                data = request.data
            else:
                keys = request.form.keys() or ['']
                data = keys[0]
            return json.loads(data)
        except:
            log(__name__, level.Warning, "Error retrieving JSON contents")
            log_exc(__name__, level.Info)
            return None

class WebLab(object):
    def __init__(self):
        self.methods = OrderedDict() # {
        #   method_name : function
        #}
        self.routes = OrderedDict() # {
        #   path : (func, path, methods)
        # }
        self.context = threading.local()

    def __enter__(self, *args, **kwargs):
        # TODO: fill 
        self.context.reservation_id = 'reservation_id'

    def __exit__(self, *args, **kwargs):
        pass

    def _error(self, msg, code):
        return {"message": msg, "code": code, "is_exception": True}

    def _json(self):
        contents = get_json()
        method = contents['method']
        if method not in self.methods:
            return json.dumps(msg = "Method not recognized", code = WEBLAB_GENERAL_EXCEPTION_CODE)
        parameters = contents.get('params', {})
        with self:
            return self.methods[method](**parameters)
        
    def route(self, path, methods = ['GET']):
        def wrapper(func):
            if func.__name__ in self.methods:
                log(WebLab, level.Error, "Overriding %s" % func.__name__)

            self.methods[func.__name__] = func
            if path in self.routes:
                log(WebLab, level.Error, "Overriding %s" % path)
            self.routes[path] = (func, path, methods)
            return func
        return wrapper

    def apply_routes(self, flask_app):
        self.json = flask_app.route("/", methods = ['GET', 'POST'])(self._json)
        for path in self.routes:
            self._create_wrapper(path, flask_app)

    def _create_wrapper(self, path, flask_app):
        func, path, methods = self.routes[path]
        @wraps(func)
        def weblab_wrapper(*args, **kwargs):
            with self:
                return func(*args, **kwargs)
        flask_app.route(path, methods = methods)(weblab_wrapper)

# weblab = WebLab()
# 
# @weblab.route("/laboratories/", methods = ['GET', 'POST'])
# def list_laboratories():
#     print weblab.context.reservation_id
#     return "Listing laboratories..."
# 
# @weblab.route("/uses/", methods = ['GET', 'POST'])
# def list_uses():
#     print weblab.context.reservation_id
#     return json.dumps([ 'use_id1', 'use_id2' ])
# 
# @weblab.route("/uses/<id>/", methods = ['GET', 'POST'])
# def list_use(id):
#     print weblab.context.reservation_id
#     return "Uses of id: %s" % id
# 
# 
# # Later on
# app = Flask(__name__)
# weblab.apply_routes(app)
# 
# # TO TEST:
# # >>> import json
# # >>> requests.post("http://localhost:5000/", data = json.dumps({'method' : 'list_uses' })).json()
# # [u'use_id1', u'use_id2']
# # >>> requests.post("http://localhost:5000/", data = json.dumps({'method' : 'list_use', 'arguments' : {'id' : 'use_id1'} })).text
# # u'Uses of id: use_id1'
# 
# 
# app.run(debug = True)
