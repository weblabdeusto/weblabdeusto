import StringIO
from abc import ABCMeta, abstractmethod

import yaml

import voodoo.log as log

from voodoo.configuration import ConfigurationManager
from voodoo.gen2.exc import GeneratorError, LocatorKeyError
from .util import _get_methods_by_component_type, _load_type
from .address import CoordAddress

LAB_CLASS  = 'weblab.lab.server.LaboratoryServer'
CORE_CLASS = 'weblab.core.server.UserProcessingServer'

PROTOCOL_PRIORITIES = ('http', 'xmlrpc')

class InstanceHandler(object): 
    def __init__(self, server, instance): 
        self.instance = instance
        self.server = server

    def start(self):
        self.server.start()
 
    def stop(self): 
        self.server.stop()

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

    def create(self, coord_address):
        """ create(coord_address) -> InstanceHandler
        
        Create an instance, attach the required communication servers, and return 
        both.
        """
        config = self._create_config(coord_address)
        component_config = self[coord_address]
        ComponentClass = _load_type(component_config.component_class)
        locator = Locator(self, coord_address)
        instance = ComponentClass(coord_address, locator, config)
        server = _create_server(instance, coord_address, component_config)
        return InstanceHandler(server, instance)

    def _create_config(self, coord_address):
        host_config = self[coord_address.host]
        process_config = host_config[coord_address.process]
        component_config = process_config[coord_address.component]

        config = ConfigurationManager()
        self._update_config(config, self)
        self._update_config(config, host_config)
        self._update_config(config, process_config)
        self._update_config(config, component_config)
        return config

    def _update_config(self, config, config_holder):
        for config_file in (config_holder.config_files or []):
            config.append_path(config_file)

        for config_key, config_value in (config_holder.config_values or {}).iteritems():
            config.append_value(config_key, config_value)

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

def _create_client(component_type, server_config):
    protocol = server_config.get('type')
    if protocol not in _SERVER_CLIENTS:
        raise Exception("Unregistered protocol in _SERVER_CLIENTS: %s" % protocol)

    return _SERVER_CLIENTS[protocol](component_type, server_config)

from .clients import DirectClient, HttpClient, XmlRpcClient

_SERVER_CLIENTS = {
    'direct' : DirectClient,
    'http' : HttpClient,
    'xmlrpc' : XmlRpcClient,
}

from .servers import _create_server
