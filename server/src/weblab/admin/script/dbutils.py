from __future__ import print_function, unicode_literals
import os
import sys

from voodoo.dbutil import get_sqlite_dbname
import weblab.configuration_doc as configuration_doc

def get_variable(dictionary, name):
    default = configuration_doc.variables[name].default
    if default == configuration_doc.NO_DEFAULT:
        return dictionary[name]
    else:
        return dictionary.get(name, default)

class DbConfiguration(object):
    def __init__(self, configuration_files, configuration_values):

        for configuration_file in configuration_files:
            if not os.path.exists(configuration_file):
                print("Could not find configuration file", configuration_file, file=sys.stderr)
                sys.exit(1)

            globals()['CURRENT_PATH'] = configuration_file
            execfile(configuration_file, globals(), globals())    

        global_vars = globals()

        for key, value in (configuration_values or []):
            global_vars[key] = value

        self.db_host           = get_variable(global_vars, configuration_doc.DB_HOST)
        self.db_port           = get_variable(global_vars, configuration_doc.DB_PORT)
        self.db_engine         = get_variable(global_vars, configuration_doc.DB_ENGINE)
        self.db_name           = get_variable(global_vars, configuration_doc.DB_DATABASE)
        self.db_user           = get_variable(global_vars, configuration_doc.DB_USERNAME)
        self.db_pass           = get_variable(global_vars, configuration_doc.DB_PASSWORD)

        if get_variable(global_vars, configuration_doc.COORDINATOR_IMPL) == 'sqlalchemy':
            self.coord_db_host     = get_variable(global_vars, configuration_doc.COORDINATOR_DB_HOST)
            self.coord_db_port     = get_variable(global_vars, configuration_doc.COORDINATOR_DB_PORT)
            self.coord_db_engine   = get_variable(global_vars, configuration_doc.COORDINATOR_DB_ENGINE)
            self.coord_db_name     = get_variable(global_vars, configuration_doc.COORDINATOR_DB_NAME)
            self.coord_db_user     = get_variable(global_vars, configuration_doc.COORDINATOR_DB_USERNAME)
            self.coord_db_pass     = get_variable(global_vars, configuration_doc.COORDINATOR_DB_PASSWORD)
        else:
            self.coord_db_host = self.coord_db_port = self.coord_db_engine = self.coord_db_name = self.coord_db_user = self.coord_db_pass = None


    def build_url(self):
        if self.db_engine == 'sqlite':
            return 'sqlite:///%s' % get_sqlite_dbname(self.db_name)
        else:
            return "%(ENGINE)s://%(USER)s:%(PASSWORD)s@%(HOST)s/%(DATABASE)s" % \
                            { "ENGINE":   self.db_engine,
                              "USER":     self.db_user, "PASSWORD": self.db_pass,
                              "HOST":     self.db_host, "DATABASE": self.db_name }
    
    def build_coord_url(self):
        if self.coord_db_engine is None:
            return None
        elif self.coord_db_engine == 'sqlite':
            return 'sqlite:///%s' % get_sqlite_dbname(self.coord_db_name)
        else:
            return "%(ENGINE)s://%(USER)s:%(PASSWORD)s@%(HOST)s/%(DATABASE)s" % \
                            { "ENGINE":   self.coord_db_engine,
                              "USER":     self.coord_db_user, "PASSWORD": self.coord_db_pass,
                              "HOST":     self.coord_db_host, "DATABASE": self.coord_db_name }

