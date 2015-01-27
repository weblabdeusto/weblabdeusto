import sys
import pickle
import xmlrpclib
import requests

import voodoo.log as log

from . import AbstractClient
from .util import _get_type_name, _load_type
from .exc import InternalCapturedServerCommunicationError, InternalServerCommunicationError, InternalClientCommunicationError
from .registry import GLOBAL_REGISTRY

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

