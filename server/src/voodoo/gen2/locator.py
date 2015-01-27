import voodoo.log as log

from .exc import LocatorKeyError
from .address import CoordAddress
from .clients import _create_client

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
