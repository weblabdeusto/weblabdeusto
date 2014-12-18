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
        self.ctx = self.context # Alias

    def __enter__(self, *args, **kwargs):
        if not hasattr(self.context, 'reservation_id'):
            self.context.reservation_id = request.args.get('reservation_id')
        
        if not hasattr(self.context, 'session_id'):
            session_id = request.cookies.get('weblabsessionid')
            if session_id:
                if '.' in session_id:
                    session_id = session_id.split('.')[0]
                self.context.session_id = session_id
            else:
                self.context.session_id = request.args.get('session_id')

    def __exit__(self, *args, **kwargs):
        pass

    def _error(self, msg, code):
        return {"message": msg, "code": code, "is_exception": True}

    def _json(self, flask_app, server_instance):
        if request.method == 'POST':
            contents = get_json()
            if contents:
                method = contents['method']
                if method not in self.methods:
                    return json.dumps(msg = "Method not recognized", code = WEBLAB_GENERAL_EXCEPTION_CODE)
                parameters = contents.get('params', {})

                if 'reservation_id' in parameters:
                    self.context.reservation_id = parameters['reservation_id']

                if 'session_id' in parameters:
                    self.context.session_id = parameters['session_id']

                with self:
                    self.context.app = flask_app
                    self.context.server_instance = server_instance
                    return self.methods[method](**parameters)
            else:
                # TODO
                return "Not a valid JSON..."
        else:
            # TODO
            return "Hi there. This should be a list of services or something..."
        
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

    def apply_routes(self, flask_app, base_path = '', server_instance = None):
        if base_path == '/':
            base_path = ''
        self.json = flask_app.route(base_path + "/", methods = ['GET', 'POST'])(lambda : self._json(flask_app, server_instance) )
        for path in self.routes:
            self._create_wrapper(base_path, path, flask_app, server_instance)

    def _create_wrapper(self, base_path, path, flask_app, server_instance):
        func, path, methods = self.routes[path]
        @wraps(func)
        def weblab_wrapper(*args, **kwargs):
            self.context.app = flask_app
            self.context.server_instance = server_instance
            with self:
                result = func(*args, **kwargs)
                if isinstance(result, dict):
                    return json.dumps(result)
                else:
                    return result

        flask_app.route(base_path + path, methods = methods)(weblab_wrapper)

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
