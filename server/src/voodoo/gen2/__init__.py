import re
import sys
import time
import pickle
import logging
import StringIO
import traceback
import threading
import xmlrpclib
from functools import wraps
from abc import ABCMeta, abstractmethod

import yaml
import requests
from flask import Flask, Blueprint, request, current_app, render_template

import voodoo.log as log

from voodoo.counter import next_counter
from voodoo.resources_manager import is_testing
from voodoo.gen2.exc import GeneratorError, LocatorKeyError, InternalCapturedServerCommunicationError, InternalServerCommunicationError
from voodoo.gen2.registry import GLOBAL_REGISTRY

LAB_CLASS  = 'weblab.lab.server.LaboratoryServer'
CORE_CLASS = 'weblab.core.server.UserProcessingServer'
METHODS_PATH = 'weblab.methods'

PROTOCOL_PRIORITIES = ('http', 'xmlrpc')

############################################
# 
#   Configuration structures
# 

class GlobalConfig(dict):
    def __init__(self, config_files, config_values):
        super(GlobalConfig, self).__init__()
        self.config_files = config_files
        self.config_values = config_values
    
    def __getitem__(self, name):
        if isinstance(name, CoordAddress):
            coord_address = name
            return self[coord_address.host][coord_address.process][coord_address.component]

        return dict.__getitem__(self, name)

    def create_server(self, coord_address, server_instance):
        component_config = self[coord_address]
        return _create_server(server_instance, coord_address, component_config)

class HostConfig(dict):
    def __init__(self, config_files, config_values, host):
        super(HostConfig, self).__init__()
        self.config_files = config_files
        self.config_values = config_values
        self.host = host

class ProcessConfig(dict):
    def __init__(self, config_files, config_values):
        super(ProcessConfig, self).__init__()
        self.config_files = config_files
        self.config_values = config_values

class ComponentConfig(object):
    def __init__(self, config_files, config_values, component_type, component_class, protocols):
        super(ComponentConfig, self).__init__()
        self.config_files = config_files
        self.config_values = config_values
        self.component_type = component_type
        self.component_class = component_class
        self.protocols = protocols

    def __repr__(self):
        return 'ComponentConfig(%r, %r, %r, %r, %r)' % (self.config_files, self.config_values, self.component_type, self.component_class, self.protocols)

class ProtocolsConfig(dict):
    def __init__(self, port = None, path = None):
        super(ProtocolsConfig, self).__init__()
        self.port = port
        self.path = path


############################################
# 
#   Configuration loading
# 

def _process_config(tree):
    config_files = []
    config_values = {}

    if 'config_files' in tree:
        config_files.extend(tree['config_files'])

    if 'config_file' in tree:
        config_files.append(tree['config_file'])

    if 'config' in tree:
        config_values.update(tree['config'])

    return config_files, config_values

def load(yaml_file):
    return _load_contents(yaml.load(open(yaml_file)))

def loads(yaml_contents):
    return _load_contents(yaml.load(StringIO.StringIO(yaml_contents)))

def _load_contents(contents):
    global_value = contents

    config_files, config_values = _process_config(global_value)
    global_config = GlobalConfig(config_files, config_values)

    for host_name, host_value in global_value.get('hosts', {}).iteritems():
        config_files, config_values = _process_config(host_value)
        host = host_value.get('host')
        host_config = HostConfig(config_files, config_values, host)
        global_config[host_name] = host_config

        for process_name, process_value in host_value.get('processes', {}).iteritems():
            config_files, config_values = _process_config(process_value)
            process_config = ProcessConfig(config_files, config_values)
            host_config[process_name] = process_config
        
            for component_name, component_value in process_value.get('components', {}).iteritems():
                config_files, config_values = _process_config(component_value)

                # Type and class
                component_type = component_value.get('type')
                if not component_type:
                    raise GeneratorError("Missing component type on %s:%s@%s" % (component_name, process_name, host_name))

                if component_type == 'laboratory':
                    component_class = LAB_CLASS
                elif component_type == 'core':
                    component_class = CORE_CLASS
                else:
                    component_class = component_value.get('class')
                    if not component_class:
                        raise GeneratorError("Missing component class on %s:%s@%s" % (component_name, process_name, host_name))

                # Protocols
                protocols = component_value.get('protocols', None)
                if not protocols:
                    protocols_config = ProtocolsConfig()
                else:
                    port = protocols.pop('port', None)
                    if not port:
                        raise GeneratorError("Protocols defined but missing port on %s:%s@%s" % (component_name, process_name, host_name))

                    path = protocols.pop('path', None)
                    protocols_config = ProtocolsConfig(port, path)
                    supports = protocols.get('supports', PROTOCOL_PRIORITIES)
                    if isinstance(supports, basestring):
                        if ',' in supports:
                            supports = [ s.strip() for s in supports.split(',') ]
                        else:
                            supports = [ supports ]
                    for protocol in supports:
                        protocols_config[protocol] = {}

                component_config = ComponentConfig(config_files, config_values, component_type, component_class, protocols_config)
                process_config[component_name] = component_config

    return global_config


############################################
# 
#   Locator
# 

class Locator(object):
    def __init__(self, global_config, my_coord_address):
        self.global_config = global_config
        self.my_coord_address = my_coord_address

    def get_connection(self, coord_address):
        """Return the best connection, if any. If it's not possible to
        find a connection, simply returns None. Otherwise, it returns:
        {
            'type' : 'direct'
        }
        or:
        {
            'type' : 'http' # Or 'xmlrpc'
            'host' : '127.0.0.1',
            'port' : 12345,
            'path' : '/foo/bar'
        }
        """
        if coord_address.host == self.my_coord_address.host and coord_address.process == self.my_coord_address.process:
            # Same machine & process: connect through direct
            return {'type' : 'direct', 'address' :  coord_address.address}

        component_config = self.global_config[coord_address]
        protocols = component_config.protocols
        if coord_address.host == self.my_coord_address.host:
            host = '127.0.0.1'
        else:
            host = self.global_config[coord_address.host].host
            if not host:
                # If host is not configured or if the host is 
                # localhost (and we're in a different machine),
                # there is nothing to do
                return None

            if host in ('127.0.0.1', 'localhost', 'localhost.localdomain'):
                log.log(__name__, log.level.Warning, "WARNING: coord_address %s using %s to communicate with %s" % (self.my_coord_address.address, host, coord_address.address))

        if 'http' in protocols:
            return_data = {
                'type' : 'http',
                'host' : host,
                'port' : protocols.port,
                'path' : protocols.path or '',
            }
            return_data.update(protocols['http'])
            return return_data
       
        if 'xmlrpc' in protocols:
            return_data = {
                'type' : 'xmlrpc',
                'host' : host,
                'port' : protocols.port,
                'path' : protocols.path or '',
            }
            return_data.update(protocols['xmlrpc'])
            return return_data
        
        return None
        
    def find_by_type(self, component_type):
        """ returns a list of CoordAddress of those laboratories of a given component_type which can be reached from the current instance. """
        addresses = []

        for host, host_value in self.global_config.iteritems():
            for process, process_value in host_value.iteritems():
                for component, component_value in process_value.iteritems():
                    if component_value.component_type == component_type:
                        # It's a candidate. Try networks
                        external_component = CoordAddress(host, process, component)
                        connection = self.get_connection(external_component)
                        if connection:
                            addresses.append(external_component)

        return addresses

    def get(self, coord_address):
        """ Return the most efficient client to that component, or None """
        if not isinstance(coord_address, CoordAddress):
            raise ValueError("coord_address %r must be of type CoordAddress" % coord_address)
        
        connection_config = self.get_connection(coord_address)
        if connection_config:
            component_type = self.global_config[coord_address].component_type
            return _create_client(component_type, connection_config)

    def __getitem__(self, coord_address):
        """ Returns the most efficient client to that component, or raises a KeyError """
        client = self.get(coord_address)
        if client:
            return client
        
        raise LocatorKeyError(coord_address.address)


############################################
# 
#   CoordAddress
# 

class CoordAddress(object):

    FORMAT = u'%(component)s:%(process)s@%(host)s'
    REGEX_FORMAT = '^' + FORMAT % {
        'component' : '(.*)',
        'process' : '(.*)',
        'host' : '(.*)'
    } + '$'

    def __init__(self, host, process = '', component = ''):
        self._address = CoordAddress.FORMAT % {
                'component': component,
                'process': process,
                'host': host }

        self._host = host
        self._process = process
        self._component = component

    def __eq__(self, other):
        return self._address.__eq__(getattr(other, '_address', other))

    def __ne__(self, other):
        return self._address.__ne__(getattr(other, '_address', other))

    def __cmp__(self, other):
        return cmp(self._address, (getattr(other, '_address', other)))

    def __unicode__(self):
        return self._address

    def __hash__(self):
        return hash(self._address)

    def __repr__(self):
        return 'CoordAddress(host = %r, process = %r, component = %r)' % (self._host, self._process, self._component)

    @property
    def host(self):
        return self._host

    @property
    def process(self):
        return self._process

    @property
    def component(self):
        return self._component

    @property
    def address(self):
        return self._address

    @staticmethod
    def translate_address(address):
        """ translate_address(address) -> CoordAddress

        Given a Coordinator Address in CoordAddress.FORMAT format,
        translate_address will provide the corresponding CoordAddress
        """
        try:
            m = re.match(CoordAddress.REGEX_FORMAT,address)
        except TypeError:
            raise GeneratorError(
                "%(address)s is not a valid address. Format: %(format)s" % {
                "address" : address, "format"  : CoordAddress.FORMAT })

        if m is None:
            raise GeneratorError(
                    '%(address)s is not a valid address. Format: %(format)s' % {
                    'address' : address, 'format'  : CoordAddress.FORMAT })
        else:
            component, process, host = m.groups()
            return CoordAddress(host,process,component)

    translate = translate_address


############################################
# 
#   Clients
# 

class AbstractClient(object):
    __metaclass__ = ABCMeta

    def __init__(self, component_type):

        methods = _get_methods_by_component_type(component_type)

        # Create methods in this instance for each of these methods
        for method in methods:
            call_method = self._create_method(method)
            setattr(self, method, call_method)

    def _create_method(self, method_name):
        def method(*args):
            return self._call(method_name, *args)
        method.__name__ = method_name
        return method

    @abstractmethod
    def _call(self, name, *args):
        """Call a method with the given name and arguments"""

_SERVER_CLIENTS = {
    # 'direct' : DirectClient
}

def _create_client(component_type, server_config):
    protocol = server_config.get('type')
    if protocol not in _SERVER_CLIENTS:
        raise Exception("Unregistered protocol in _SERVER_CLIENTS: %s" % protocol)

    return _SERVER_CLIENTS[protocol](component_type, server_config)

ACCEPTABLE_EXC_TYPES = ('voodoo.', 'weblab.')

class DirectClient(AbstractClient):
    
    def __init__(self, component_type, server_config):
        super(DirectClient, self).__init__(component_type)
        self.coord_address_str = server_config['address']

    def _call(self, name, *args):
        instance = GLOBAL_REGISTRY[self.coord_address_str]
        method = getattr(instance, 'do_%s' % name)
        try:
            return method(*args)
        except:
            exc_type, exc_instance, _ = sys.exc_info()
            remote_exc_type = _get_type_name(exc_type)
            if remote_exc_type.startswith(ACCEPTABLE_EXC_TYPES):
                raise

            log.error(__name__, 'Error on %s' % name)
            log.error_exc(__name__)

            remote_exc_args = exc_instance.args
            if not isinstance(remote_exc_args, list) and not isinstance(remote_exc_args, tuple):
                remote_exc_args = [remote_exc_args]
            
            raise InternalCapturedServerCommunicationError(remote_exc_type, *remote_exc_args)

_SERVER_CLIENTS['direct'] = DirectClient

class HttpClient(AbstractClient):

    def __init__(self, component_type, server_config):
        super(HttpClient, self).__init__(component_type)
        path = server_config.get('path', '/')
        host = server_config.get('host')
        port = server_config.get('port')
        self.url = "http://%s:%s%s" % (host, port, path)

    def _call(self, name, *args):
        # In the future (once we don't pass any weird arg, such as SessionId and so on), use JSON

        # First, serialize the data provided in the client side
        try:
            request_data = pickle.dumps(args)
        except:
            _, exc_instance, _ = sys.exc_info()
            raise InternalClientCommunicationError("Unknown client error contacting %s: %r" % (self.url, exc_instance))
        
        # Then, perform the request and deserialize the results
        try:

            content = requests.post(self.url + '/' + name, data = request_data).content
            result = pickle.loads(content)
        except:
            _, exc_instance, _ = sys.exc_info()
            raise InternalServerCommunicationError("Unknown server error contacting %s with HTTP: %r" % (self.url, exc_instance))

        # result must be a dictionary which contains either 'result' 
        # with the resulting object or 'is_error' and some data about 
        # the exception

        if result.get('is_error'):
            error_type = result['error_type']
            error_args = result['error_args']
            if not isinstance(error_args, list) and not isinstance(error_args, tuple):
                error_args = [error_args]

            # If it's acceptable, raise the exception (e.g., don't raise a KeyboardInterrupt, a MemoryError, or a library error)
            if error_type.startswith(ACCEPTABLE_EXC_TYPES):
                exc_type = _load_type(error_type)
                raise exc_type(*error_args)
            else:
                # Otherwise wrap it
                raise InternalCapturedServerCommunicationError(error_type, *error_args)
        # No error? return the result
        return result['result']

_SERVER_CLIENTS['http'] = HttpClient

class XmlRpcClient(AbstractClient):

    def __init__(self, component_type, server_config):
        super(XmlRpcClient, self).__init__(component_type)
        path = server_config.get('path', '/')
        host = server_config.get('host')
        port = server_config.get('port')
        self.url = "http://%s:%s%s" % (host, port, path)
        self.server = xmlrpclib.Server(self.url)

    def _call(self, name, *args):
        try:
            return getattr(self.server, 'Util.%s' % name)(*args)
        except xmlrpclib.Fault as ft:
            raise InternalCapturedServerCommunicationError(ft.faultCode, [ ft.faultString ])
        except:
            _, exc_instance, _ = sys.exc_info()
            raise InternalServerCommunicationError("Unknown server error contacting %s with XML-RPC: %r" % (self.url, exc_instance))

_SERVER_CLIENTS['xmlrpc'] = XmlRpcClient


############################################
# 
#   Servers
#

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

    method = getattr(current_app.wl_server_instance, 'do_%s' % method_name)
    try:
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

    method = getattr(server_instance, 'do_%s' % method_name)
    try:
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
    def start(self):
        pass

    def stop(self):
        pass

class DirectServer(Server):
    pass

class InternalFlaskServer(Server):
    def __init__(self, application, port):
        self.application = application
        self.port = port

        if is_testing():
            @application.route('/_shutdown')
            def shutdown_func():
                func = request.environ.get('werkzeug.server.shutdown')
                if func:
                    func()
                    return "Shutting down"
                else:
                    return "Shutdown not available"

        self._thread = threading.Thread(target = self.application.run, kwargs = {'port' : self.port, 'debug' : False})
        self._thread.setDaemon(True)
        self._thread.setName(next_counter('InternalFlaskServer'))

    def start(self):
        self._thread.start()
        time.sleep(0.01)

    def stop(self):
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
                log.log(__name__, log.Warning, msg)

    GLOBAL_REGISTRY[coord_address.address] = instance

    protocols = component_config.protocols
    if protocols:
        app = Flask(__name__)
        app.wl_server_instance = instance
        app.wl_server_methods = methods
        logger = logging.getLogger('werkzeug')
        logger.setLevel(logging.CRITICAL)

        path = protocols.path or ''
        app.register_blueprint(_methods, url_prefix = path)
        return InternalFlaskServer(app, protocols.port)
    else:
        # This server does nothing
        return DirectServer()

#####################################################
# 
#  Auxiliar methods used above
# 

def _get_methods_by_component_type(component_type):
    methods_module = __import__(METHODS_PATH, fromlist = ['methods'])
    methods = getattr(methods_module.methods, component_type, None)
    if methods is None:
        raise Exception("Unregistered component type in weblab/methods.py: %s" % component_type)
    return methods

def _get_type_name(klass):
    """ _get_type_name(KeyError) -> 'exceptions.KeyError' """
    return klass.__module__ + '.' + klass.__name__

def _load_type(type_name):
    """ _load_type('exceptions.KeyError') -> KeyError """
    module_name, name = type_name.rsplit('.', 1)
    mod = __import__(module_name, fromlist = [name])
    return getattr(mod, name)

