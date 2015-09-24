from __future__ import print_function, unicode_literals
class ValidDatabaseSessionId(object):
    def __init__(self, username = None, role = ''):
        super(ValidDatabaseSessionId,self).__init__()
        self.valid = True
        self.role = role
        self.username = username

    def __repr__(self):
        return '<%(class_name)s> %(role_name)s@%(username)s' % {
                'class_name' : self.__class__,
                'role_name'  : self.role,
                'username'   : self.username
            }

