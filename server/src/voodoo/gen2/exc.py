from voodoo.exc import VoodooError

class VoodooGenError(VoodooError):
    pass

class GeneratorError(VoodooGenError):
    pass

class InternalCommunicationError(VoodooGenError):
    pass

class InternalClientCommunicationError(InternalCommunicationError):
    pass

class InternalServerCommunicationError(InternalCommunicationError):
    pass

class InternalCapturedServerCommunicationError(InternalServerCommunicationError):
    def __init__(self, remote_exc_type, remote_exc_args, *args):
        super(InternalKnownServerCommunicationError, self).__init__(*args)
        self.remote_exc_type = remote_exc_type
        self.remote_exc_args = remote_exc_args

class LocatorError(GeneratorError):
    pass

class LocatorKeyError(LocatorError, KeyError):
    pass

class AddressAlreadyRegisteredError(VoodooGenError):
    pass
