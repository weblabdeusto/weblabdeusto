from __future__ import print_function, unicode_literals
ALL = 'All servers'

def caller_check(servers = ALL):
    def func_wrapper(func):
        # TODO: To be implemented. Could get current_app and check it. Useful for anything?
        return func
    return func_wrapper

