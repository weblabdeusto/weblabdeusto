'''
Created on 17/12/2009

@author: lrg
'''


def traced(resource_manager = None, logging = True):
    """

    """
    def wrapped(func):

        def wrapped_func(self, *args, **kargs):
            str = "[TRACE]: %s(" % func.__name__
            str += ")"
            print str
            return func(self, *args, **kargs)
            
        return wrapped_func

    return wrapped

