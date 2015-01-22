import re
from abc import ABCMeta, abstractmethod
import pickle
import xmlrpclib

import yaml

import requests
from voodoo.gen2.exc import GeneratorError
from voodoo.gen2.registry import GLOBAL_REGISTRY

LAB_CLASS  = 'weblab.lab.server.LaboratoryServer'
CORE_CLASS = 'weblab.core.server.UserProcessingServer'
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
    def __init__(self, port):
        super(ProtocolsConfig, self).__init__()
        self.port = port


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

def loads(yaml_file):
    return _load_contents(yaml.loads(yaml_contents))

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
                protocols = component_value.get('protocols', {})
                port = protocols.pop('port', None)
                protocols_config = ProtocolsConfig(port)
                protocols_config.update(protocols)

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
            if not host or host in ('127.0.0.1', 'localhost', 'localhost.localdomain'):
                # If host is not configured or if the host is 
                # localhost (and we're in a different machine),
                # there is nothing to do
                return None

        if 'http' in protocols:
            return_data = {
                'type' : 'http',
                'host' : host,
                'port' : protocols.port
            }
            return_data.update(protocols['http'])
            return return_data

        if 'xmlrpc' in protocols:
            return_data = {
                'type' : 'xmlrpc',
                'host' : host,
                'port' : protocols.port
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
            component_type = slef.global_config[coord_address].component_type
            return _create_client(component_type, connection_config)

    def __getitem__(self, coord_address):
        """ Returns the most efficient client to that component, or raises a KeyError """
        client = self.get(coord_address)
        if client:
            return client
        
        # TODO: make a class that subclasses both KeyError and VoodooError
        raise KeyError(unicode(coord_address))


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


############################################
# 
#   Clients
# 

METHODS_PATH = 'weblab.methods'

def _get_methods_by_component_type(component_type):
    methods_module = __import__(METHODS_PATH)
    methods = getattr(methods_module.methods, component_type, None)
    if methods is None:
        raise Exception("Unregistered component type in weblab/methods.py: %s" % component_type)
    return methods

class AbstractClient(object):
    __metaclass__ = ABCMeta

    def __init__(self, component_type):

        methods = _get_methods_by_component_type(component_type)

        print "Loading", methods
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

class DirectClient(AbstractClient):
    
    def __init__(self, component_type, server_config):
        super(DirectClient, self).__init__(component_type)
        self.coord_address_str = server_config['address']

    def _call(self, name, *args):
        instance = GLOBAL_REGISTRY[self.coord_address_str]
        method = getattr(instance, 'do_%s' % name)
        # TODO: exceptions
        return method(*args)

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
        # TODO: exceptions
        result = requests.post(self.url + '/' + name, data = pickle.dumps(args)).content
        return pickle.loads(content)

_SERVER_CLIENTS['http'] = HttpClient

class XmlRpcClient(AbstractClient):

    def __init__(self, component_type, server_config):
        super(XmlRpcClient, self).__init__(component_type)
        path = server_config.get('path', '/')
        host = server_config.get('host')
        port = server_config.get('port')
        self.server = xmlrpclib.Server("http://%s:%s%s" % (host, port, path))

    def _call(self, name, *args):
        # TODO: exceptions
        return getattr(self.server, 'Util.%s' % name)(*args)

_SERVER_CLIENTS['xmlrpc'] = XmlRpcClient


############################################
# 
#   Servers
#

def _create_server(server_instance, coord_address, component_config):
    """ server_instance: an instance of a class which contains the defined methods """
    component_type = component_config['type']
    
    methods = _get_methods_by_component_type(component_type)
    missing_methods = []
    for method in methods:
        method_name = 'do_%s' % method
        if not hasattr(instance, method_name):
            missing_methods.append(method_name)

    if missing_methods:
        raise Exception("instance %s missing methods: %r" % (server_instance, missing_methods))

    GLOBAL_REGISTRY[coord_address.address] = server_instance

    protocols = component_config.get('protocols', {})
    if protocols:
        # Create a single Flask app first, then start registering per protocol (http, xmlrpc)
        # TODO
        pass



