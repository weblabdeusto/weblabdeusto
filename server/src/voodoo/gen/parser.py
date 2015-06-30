from __future__ import print_function, unicode_literals
import os

import six
import yaml
import traceback
from collections import defaultdict

from voodoo.configuration import ConfigurationManager

from voodoo.gen.exc import GeneratorError, LoadingError
from voodoo.gen.util import _load_type
from voodoo.gen.address import CoordAddress
from voodoo.gen.locator import Locator
from voodoo.gen.servers import _create_server

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
    def __init__(self, config_files, config_values, deployment_dir):
        super(GlobalConfig, self).__init__()
        self.config_files = config_files
        self.config_values = config_values
        self.deployment_dir = deployment_dir
    
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
        config = self.create_config(coord_address)
        component_config = self[coord_address]
        try:
            ComponentClass = _load_type(component_config.component_class)
        except Exception as e:
            traceback.print_exc()
            raise LoadingError(u"Error loading component: %r for server %s: %s" % (component_config.component_class, coord_address, e))
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
        """
        Starts a WebLab process with the configuration that is currently loaded in the calling object.
        Unless the dont-start flag has been enabled in the configuration, this will start the Flask
        server and start listening for requests.

        :param host: Name of the host (specified in the configuration)
        :type host: str
        :param process: Name of the process (specified in the configuration)
        :type process: str
        """
        process_handler = self.create_process(host, process)
        process_handler.start()
        return process_handler

    def _retrieve_config(self, element, all_config_files, all_config_values):
        for config_file in element.config_files:
            all_config_files.append(config_file)

        for key, value in six.iteritems(element.config_values):
            all_config_values.append((key, value))


    def get_all_config(self):
        all_config_files = []
        all_config_values = []

        self._retrieve_config(self, all_config_files, all_config_values)

        for host_name, host in six.iteritems(self):
            self._retrieve_config(host, all_config_files, all_config_values)

            for process_name, process in six.iteritems(host):
                self._retrieve_config(process, all_config_files, all_config_values)

                for component_name, component in six.iteritems(process):
                    self._retrieve_config(component, all_config_files, all_config_values)
        
        return all_config_files, all_config_values

    def create_config(self, coord_address):
        host_config = self[coord_address.host]
        process_config = host_config[coord_address.process]
        component_config = process_config[coord_address.component]

        config = ConfigurationManager()
        self._update_config(config, self)
        self._update_config(config, host_config)
        self._update_config(config, process_config)
        self._update_config(config, component_config)
        config.append_value('deployment_dir', self.deployment_dir)
        return config

    def _update_config(self, config, config_holder):
        for config_file in (config_holder.config_files or []):
            config.append_path(config_file)

        for config_key, config_value in (config_holder.config_values or {}).iteritems():
            config.append_value(config_key, config_value)

class HostConfig(dict):
    def __init__(self, config_files, config_values, host, runner):
        super(HostConfig, self).__init__()
        self.config_files = config_files
        self.config_values = config_values
        self.host = host
        self.runner = runner

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

def _process_config(tree, directory):
    config_files = []
    config_values = {}

    if 'config_files' in tree:
        for config_file in tree['config_files']:
            config_files.append(os.path.join(directory, config_file))

    if 'config_file' in tree:
        config_files.append(os.path.join(directory, tree['config_file']))

    if 'config' in tree:
        config_values.update(tree['config'])

    return config_files, config_values

def load_dir(directory):
    """
    Loads the WebLab instance global configuration within the specified directory, which can be
    used to start WebLab instances.

    :param directory: Directory to load configuration files from.
    :type directory: str
    :return: The global configuration object with the loaded configuration
    :rtype: GlobalConfig
    """
    if not os.path.exists(directory):
        raise GeneratorError("Directory %s does not exist" % directory)

    config_filename = os.path.join(directory, 'configuration.yml')
    if not os.path.exists(config_filename):
        raise GeneratorError("Expected file %s not found" % config_filename)

    return load(config_filename)

def load(yaml_file):
    return _load_contents(yaml.load(open(yaml_file)), os.path.dirname(yaml_file))

def loads(yaml_contents):
    return _load_contents(yaml.load(six.StringIO(yaml_contents)), '.')

def _load_contents(contents, directory):
    global_value = contents

    config_files, config_values = _process_config(global_value, directory)
    global_config = GlobalConfig(config_files, config_values, directory)

    type_counter = defaultdict(int)

    for host_name, host_value in global_value.get('hosts', {}).iteritems():
        config_files, config_values = _process_config(host_value, directory)
        host = host_value.get('host')
        runner = host_value.get('runner')
        host_config = HostConfig(config_files, config_values, host, runner)
        global_config[host_name] = host_config

        for process_name, process_value in host_value.get('processes', {}).iteritems():
            config_files, config_values = _process_config(process_value, directory)
            process_config = ProcessConfig(config_files, config_values)
            host_config[process_name] = process_config
        
            for component_name, component_value in process_value.get('components', {}).iteritems():
                config_files, config_values = _process_config(component_value, directory)

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

                config_values['%s_number' % component_type] = type_counter[component_class]
                type_counter[component_class] += 1

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

