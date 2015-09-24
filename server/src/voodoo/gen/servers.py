from __future__ import print_function, unicode_literals
import sys
import time
import pickle
import logging
import threading
import xmlrpclib
import traceback
from functools import wraps

import requests
from flask import Flask, Blueprint, request, render_template, current_app

import voodoo.log as log
from voodoo.resources_manager import is_testing
from voodoo.counter import next_counter

from .util import _get_type_name, _get_methods_by_component_type
from .registry import GLOBAL_REGISTRY

def show_exceptions(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:
            traceback.print_exc()
            raise
    return wrapper

_methods = Blueprint('methods', __name__)

@_methods.route('/', methods = ['GET', 'POST'])
@_methods.route('/RPC2', methods = ['GET', 'POST'])
@show_exceptions
def xmlrpc():
    if request.method == 'GET':
        return render_template('xmlrpc-methods.html', methods = current_app.wl_server_methods)

    raw_data = request.get_data()
    params, method_name = xmlrpclib.loads(raw_data)
    if method_name.startswith('Util.'):
        method_name = method_name[len('Util.'):]

    if method_name not in current_app.wl_server_methods:
        return xmlrpclib.dumps(xmlrpclib.Fault("Method not found", "Method not found"))

    try:
        if method_name == 'test_me':
            result = params[0]
        else:
            method = getattr(current_app.wl_server_instance, 'do_%s' % method_name)
            result = method(*params)
    except:
        exc_type, exc_instance, _ = sys.exc_info()
        remote_exc_type = _get_type_name(exc_type)
        fault = xmlrpclib.Fault(remote_exc_type, repr(exc_instance.args))
        log.error(__name__, 'Error on %s' % method_name)
        log.error_exc(__name__)
        return xmlrpclib.dumps(fault)

    return xmlrpclib.dumps( (result,))

@_methods.route('/<method_name>', methods = ['GET', 'POST'])
@show_exceptions
def http_method(method_name):
    if request.method == 'GET':
        return render_template('xmlrpc-methods.html', methods = current_app.wl_server_methods)

    if method_name not in current_app.wl_server_methods:
        return "Method name not supported", 404

    server_instance = current_app.wl_server_instance

    raw_data = request.get_data()
    args = pickle.loads(raw_data)
    

    try:
        if method_name == 'test_me':
            result = args[0]
        else:
            method = getattr(server_instance, 'do_%s' % method_name)
            result = method(*args)
    except:
        exc_type, exc_instance, _ = sys.exc_info()
        remote_exc_type = _get_type_name(exc_type)
        log.error(__name__, 'Error on %s' % method_name)
        log.error_exc(__name__)
        return pickle.dumps({
            'is_error' : True,
            'error_type' : remote_exc_type,
            'error_args' : exc_instance.args,
        })
    else:
        return pickle.dumps({ 'result' : result })

class Server(object):
    def __init__(self, instance):
        self.instance = instance

    def start(self):
        pass

    def stop(self):
        if hasattr(self.instance, 'stop'):
            self.instance.stop()

class DirectServer(Server):
    pass

class InternalFlaskServer(Server):
    def __init__(self, application, port, instance):
        super(InternalFlaskServer, self).__init__(instance)
        self.application = application
        self.port = port
        self.instance = instance

        if is_testing():
            @application.route('/_shutdown')
            def shutdown_func():
                func = request.environ.get('werkzeug.server.shutdown')
                if func:
                    func()
                    return "Shutting down"
                else:
                    return "Shutdown not available"

        self._thread = threading.Thread(target = self.application.run, kwargs = {'port' : self.port, 'debug' : False, 'host' : '', 'threaded' : True})
        self._thread.setDaemon(True)
        self._thread.setName(next_counter('InternalFlaskServer'))

    def start(self):
        self._thread.start()
        time.sleep(0.01)

    def stop(self):
        super(InternalFlaskServer, self).stop()

        if is_testing():
            requests.get('http://127.0.0.1:%s/_shutdown' % self.port)
            self._thread.join(5)

def _critical_debug(message):
    """Useful to make sure it's printed in the screen but not in tests"""
    print(message)

def _create_server(instance, coord_address, component_config):
    """ Creates a server that manages the communications server_instance: an instance of a class which contains the defined methods """
    component_type = component_config.component_type
    
    methods = _get_methods_by_component_type(component_type)
    missing_methods = []
    for method in methods:
        method_name = 'do_%s' % method
        if not hasattr(instance, method_name):
            missing_methods.append(method_name)

    if missing_methods:
        raise Exception("instance %s missing methods: %r" % (instance, missing_methods))
    
    # Warn if there are do_method and method is not registered
    for method in dir(instance):
        if method.startswith('do_'):
            remainder = method[len('do_'):]
            if remainder not in methods:
                msg = "Warning: method %s not in the method list for component_type %s" % (remainder, component_type)
                _critical_debug(msg)
                log.warning(__name__, msg)

    GLOBAL_REGISTRY[coord_address.address] = instance

    protocols = component_config.protocols
    if protocols:
        app = Flask(__name__)
        app.wl_server_instance = instance
        app.wl_server_methods = tuple(methods) + ('test_me',)
        logger = logging.getLogger('werkzeug')
        logger.setLevel(logging.CRITICAL)

        path = protocols.path or ''
        app.register_blueprint(_methods, url_prefix = path)
        return InternalFlaskServer(app, protocols.port, instance)
    else:
        # This server does nothing
        return DirectServer(instance)

