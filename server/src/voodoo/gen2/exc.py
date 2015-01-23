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

class LocatorError(GeneratorError):
    pass

class LocatorKeyError(LocatorError, KeyError):
    pass

class AddressAlreadyRegisteredError(VoodooGenError):
    pass
