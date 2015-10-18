from __future__ import print_function, unicode_literals
import six
import sys
import time
import pickle
import xmlrpclib
import requests
import httplib

from abc import ABCMeta, abstractmethod

import voodoo.log as log

from .util import _get_type_name, _load_type, _get_methods_by_component_type
from .exc import InternalCapturedServerCommunicationError, InternalServerCommunicationError, InternalClientCommunicationError
from .registry import GLOBAL_REGISTRY

ACCEPTABLE_EXC_TYPES = ('voodoo.', 'weblab.')

class AbstractClient(object):
    __metaclass__ = ABCMeta

    def __init__(self, component_type):

        methods = list(_get_methods_by_component_type(component_type)) + ['test_me']

        # Create methods in this instance for each of these methods
        for method in methods:
            call_method = self._create_method(method)
            setattr(self, method, call_method)

    def _create_method(self, method_name):
        def method(*args):
            return self._call(method_name, *args)
        if six.PY2:
            method.__name__ = method_name.encode('utf-8')
        else:
            method.__name__ = method_name
        return method

    @abstractmethod
    def _call(self, name, *args):
        """Call a method with the given name and arguments"""



class DirectClient(AbstractClient):
    
    def __init__(self, component_type, server_config):
        super(DirectClient, self).__init__(component_type)
        self.coord_address_str = server_config['address']

    def _call(self, name, *args):
        if name == 'test_me':
            return args[0]
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
            
            raise InternalCapturedServerCommunicationError(remote_exc_type, remote_exc_args)

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
        t0 = time.time()
        try:
            kwargs = {}
            if name == 'test_me':
                kwargs['timeout'] = (10, 60)
            else:
                kwargs['timeout'] = (60, 600)
            content = requests.post(self.url + '/' + name, data = request_data, **kwargs).content
            result = pickle.loads(content)
        except:
            tf = time.time()
            _, exc_instance, _ = sys.exc_info()
            raise InternalServerCommunicationError("Unknown server error contacting %s with HTTP after %s seconds: %r" % (self.url, tf - t0, exc_instance))

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
                try:
                    exc_instance = exc_type(*error_args)
                except TypeError:
                    # If we can't create it
                    log.error(__name__, 'Error on instantiating an exception %s(%r)' % (exc_type, error_args))
                    log.error_exc(__name__)
                    raise InternalCapturedServerCommunicationError(error_type, error_args)
                else:
                    raise exc_instance
            else:
                # Otherwise wrap it
                raise InternalCapturedServerCommunicationError(error_type, error_args)
        # No error? return the result
        return result['result']

class TimeoutTransport(xmlrpclib.Transport):

    timeout = 10.0

    def set_timeout(self, timeout):
        self.timeout = timeout
    def make_connection(self, host):
        h = httplib.HTTPConnection(host, timeout=self.timeout)
        return h

class XmlRpcClient(AbstractClient):

    def __init__(self, component_type, server_config):
        super(XmlRpcClient, self).__init__(component_type)
        path = server_config.get('path', '/')
        host = server_config.get('host')
        port = server_config.get('port')
        self.url = "http://%s:%s%s" % (host, port, path)

        long_transport = TimeoutTransport()
        long_transport.set_timeout(600.0)
        self.server = xmlrpclib.Server(self.url, transport = long_transport)

        short_transport = TimeoutTransport()
        short_transport.set_timeout(60.0)
        self.short_server = xmlrpclib.Server(self.url, transport = short_transport, allow_none = True)

    def _call(self, name, *args):
        if name == 'test_me':
            server = self.short_server
        else:
            server = self.server
        try:
            return getattr(server, 'Util.%s' % name)(*args)
        except xmlrpclib.Fault as ft:
            raise InternalCapturedServerCommunicationError(ft.faultCode, [ ft.faultString ])
        except:
            _, exc_instance, _ = sys.exc_info()
            raise InternalServerCommunicationError("Unknown server error contacting %s with XML-RPC: %r" % (self.url, exc_instance))

_SERVER_CLIENTS = {
    'direct' : DirectClient,
    'http' : HttpClient,
    'xmlrpc' : XmlRpcClient,
}

def _create_client(component_type, server_config):
    protocol = server_config.get('type')
    if protocol not in _SERVER_CLIENTS:
        raise Exception("Unregistered protocol in _SERVER_CLIENTS: %s" % protocol)

    return _SERVER_CLIENTS[protocol](component_type, server_config)

