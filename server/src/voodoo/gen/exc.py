from __future__ import print_function, unicode_literals
from voodoo.exc import VoodooError

class VoodooGenError(VoodooError):
    pass

class GeneratorError(VoodooGenError):
    pass

class LoadingError(GeneratorError):
    pass

class InternalCommunicationError(VoodooGenError):
    pass

class FailingConnectionError(InternalCommunicationError):
    pass

class InternalClientCommunicationError(InternalCommunicationError):
    pass

class InternalServerCommunicationError(InternalCommunicationError):
    pass

class InternalCapturedServerCommunicationError(InternalServerCommunicationError):
    def __init__(self, remote_exc_type, remote_exc_args, *args):
        super(InternalCapturedServerCommunicationError, self).__init__(remote_exc_type, remote_exc_args, *args)
        self.remote_exc_type = remote_exc_type
        self.remote_exc_args = remote_exc_args

    def __repr__(self):
        return 'InternalCapturedServerCommunicationError(%r, %r, %r)' % (self.remote_exc_type, self.remote_exc_args, self.args)

    def __str__(self):
        return repr(self)

class LocatorError(GeneratorError):
    pass

class LocatorKeyError(LocatorError, KeyError):
    pass

class AddressAlreadyRegisteredError(VoodooGenError):
    pass

class ServerNotFoundInRegistryError(VoodooGenError, KeyError):
    pass
