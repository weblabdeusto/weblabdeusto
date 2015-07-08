#########################################
# Auxiliar method used by lablistener.
# They resemble those in voodoo/gen/util
#########################################

def _get_type_name(klass):
    """ _get_type_name(KeyError) -> 'exceptions.KeyError' """
    return klass.__module__ + '.' + klass.__name__

def _load_type(type_name):
    """ _load_type('exceptions.KeyError') -> KeyError """
    module_name, name = type_name.rsplit('.', 1)
    mod = __import__(module_name, fromlist = [name])
    return getattr(mod, name)