from __future__ import print_function, unicode_literals
METHODS_PATH = 'weblab.methods'

#####################################################
# 
#  Auxiliar methods used above
# 

def _get_methods_by_component_type(component_type):
    methods_module = __import__(METHODS_PATH, fromlist = ['methods'])
    methods = getattr(methods_module, 'methods', None)
    if methods:
        methods = getattr(methods, component_type, None)
    else:
        methods = getattr(methods_module, component_type, None)
    if methods is None:
        raise Exception("Unregistered component type in weblab/methods.py: %s" % component_type)
    return methods

def _get_type_name(klass):
    """ _get_type_name(KeyError) -> 'exceptions.KeyError' """
    return klass.__module__ + '.' + klass.__name__

def _load_type(type_name):
    """ _load_type('exceptions.KeyError') -> KeyError """
    module_name, name = type_name.rsplit('.', 1)
    mod = __import__(module_name, fromlist = [name])
    return getattr(mod, name)

