import StringIO
import yaml

from voodoo.configuration import ConfigurationManager

from .exc import GeneratorError
from .util import _load_type
from .address import CoordAddress
from .locator import Locator
from .servers import _create_server

LAB_CLASS  = 'weblab.lab.server.LaboratoryServer'
CORE_CLASS = 'weblab.core.server.UserProcessingServer'

PROTOCOL_PRIORITIES = ('http', 'xmlrpc')

############################################
# 
#   Configuration structures

class ComponentHandler(object): 
    def __init__(self, server, instance): 
        self.instance = instance
        self.server = server

    def start(self):
        self.server.start()
 
    def stop(self): 
        self.server.stop()

class ProcessHandler(object): 
    def __init__(self, components): 
        self.components = components

    def start(self):
        for component in self.components:
            component.start()
 
    def stop(self): 
        for component in self.components:
            component.stop()

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

    def create_component(self, coord_address):
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
        return ComponentHandler(server, instance)

    def create_process(self, host, process):
        component_handlers = []

        process_config = self[host][process]
        for component in process_config:
            addr = CoordAddress(host, process, component)
            component_handlers.append(self.create_component(addr))

        return ProcessHandler(component_handlers)

    def load_process(self, host, process):
        process_handler = self.create_process(host, process)
        process_handler.start()
        return process_handler

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

