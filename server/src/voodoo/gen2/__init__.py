import re
import yaml

from voodoo.gen2.exc import GeneratorException

class GlobalConfig(dict):
    def __init__(self, cfg_files, cfg_values):
        super(GlobalConfig, self).__init__()
        self.cfg_files = cfg_files
        self.cfg_values = cfg_values
    
    def __getitem__(self, name):
        if isinstance(name, CoordAddress):
            coord_address = name
            return self[coord_address.host][coord_address.process][coord_address.component]

        return dict.__getitem__(self, name)

class HostConfig(dict):
    def __init__(self, cfg_files, cfg_values, host):
        super(HostConfig, self).__init__()
        self.cfg_files = cfg_files
        self.cfg_values = cfg_values
        self.host = host

class ProcessConfig(dict):
    def __init__(self, cfg_files, cfg_values):
        super(ProcessConfig, self).__init__()
        self.cfg_files = cfg_files
        self.cfg_values = cfg_values

class ComponentConfig(object):
    def __init__(self, cfg_files, cfg_values, component_type, component_class, protocols):
        super(ComponentConfig, self).__init__()
        self.cfg_files = cfg_files
        self.cfg_values = cfg_values
        self.component_type = component_type
        self.component_class = component_class
        self.protocols = protocols

    def __repr__(self):
        return 'ComponentConfig(%r, %r, %r, %r, %r)' % (self.cfg_files, self.cfg_values, self.component_type, self.component_class, self.protocols)

class ProtocolsConfig(dict):
    def __init__(self, port):
        super(ProtocolsConfig, self).__init__()
        self.port = port

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
        return self._address.__cmp__(getattr(other, '_address', other))

    def __unicode__(self):
        return self._address

    def __hash__(self):
        return self._address.__hash__

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
        return self.address

    @staticmethod
    def translate_address(address):
        """ translate_address(address) -> CoordAddress

        Given a Coordinator Address in CoordAddress.FORMAT format,
        translate_address will provide the corresponding CoordAddress
        """
        try:
            m = re.match(CoordAddress.REGEX_FORMAT,address)
        except TypeError:
            raise GeneratorException(
                "%(address)s is not a valid address. Format: %(format)s" % {
                "address" : address, "format"  : CoordAddress.FORMAT })

        if m is None:
            raise GeneratorException(
                    '%(address)s is not a valid address. Format: %(format)s' % {
                    'address' : address, 'format'  : CoordAddress.FORMAT })
        else:
            component, process, host = m.groups()
            return CoordAddress(host,process,component)

def _process_cfg(tree):
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

    cfg_files, cfg_values = _process_cfg(global_value)
    global_config = GlobalConfig(cfg_files, cfg_values)

    for host_name, host_value in global_value.get('hosts', {}).iteritems():
        cfg_files, cfg_values = _process_cfg(host_value)
        host = host_value.get('host')
        host_config = HostConfig(cfg_files, cfg_values, host)
        global_config[host_name] = host_config

        for process_name, process_value in host_value.get('processes', {}).iteritems():
            cfg_files, cfg_values = _process_cfg(process_value)
            process_config = ProcessConfig(cfg_files, cfg_values)
            host_config[process_name] = process_config
        
            for component_name, component_value in process_value.get('components', {}).iteritems():

                cfg_files, cfg_values = _process_cfg(process_config)

                # Type and class
                component_type = component_value.get('type')
                if not component_type:
                    raise GeneratorException("Missing component type on %s:%s@%s" % (component_name, process_name, host_name))

                if component_type == 'laboratory':
                    component_class = 'weblab.lab.server.LaboratoryServer'
                elif component_type == 'core':
                    component_class = 'weblab.lab.server.UserProcessingServer'
                else:
                    component_class = component_value.get('class')
                    if not component_class:
                        raise GeneratorException("Missing component class on %s:%s@%s" % (component_name, process_name, host_name))

                # Protocols
                protocols = component_value.get('protocols', {})
                port = protocols.pop('port', None)
                protocols_config = ProtocolsConfig(port)
                protocols_config.update(protocols)

                component_config = ComponentConfig(cfg_files, cfg_values, component_type, component_class, protocols_config)
                process_config[component_name] = component_config

    return global_config

if __name__ == '__main__':
    result = load('/home/nctrun/weblab/server/src/salida.yml')
    result = load('/home/nctrun/weblab/server/src/salida2.yml')
    import pprint
    pprint.pprint(result)

    lab = CoordAddress('core_machine', 'laboratory1', 'laboratory1')
    pprint.pprint(result[lab])

