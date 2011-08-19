import sys, os
sys.path.append(os.sep.join(("..","..","..","src")))
import libraries

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import traceback
import MySQLdb as dbi

import weblab.database.Model as Model

########################################################
# 
# Abstract class. All classes implementing this class
# will provide a "check" method, which will focus on 
# checking if the patch must be applied or it has already
# been applied, and a method "apply" which will work 
# in case the patch had not been applied.
# 
class Patch(object):
    SQL_FORMAT   = 'SQL'
    SQLALCHEMY_FORMAT = 'sqlalchemy'

    CHECK_FORMAT = SQL_FORMAT
    APPLY_FORMAT = SQL_FORMAT

    def __init__(self, user, password, db):
        self.user     = user
        self.db       = db
        self.password = password
    def execute(self):
        connection_url = "mysql://%(USER)s:%(PASS)s@%(HOST)s/%(NAME)s" % {
                                "USER": self.user,
                                "PASS": self.password,
                                "HOST": "localhost",
                                "NAME": self.db }
        self.engine = create_engine(connection_url, convert_unicode=True, echo=False)
        Session = sessionmaker(bind=self.engine)
        session = Session()
        try:
            connection = dbi.connect(host="localhost", user=self.user, passwd=self.password, db=self.db)
            try:
                cursor = connection.cursor()
                try:
                    print "Checking %s..." % type(self).__name__,
                    if self.CHECK_FORMAT == self.SQL_FORMAT:
                        check_arg = cursor
                    else:
                        check_arg = session
                    if self.check(check_arg):
                        print "[NOT APPLIED]"
                        print "Applying %s..." % type(self).__name__,
                        try:
                            if self.APPLY_FORMAT == self.SQL_FORMAT:
                                self.apply(cursor)
                                connection.commit()
                            else:
                                self.apply(session)
                                session.commit()
                        except:
                            print "[FAIL]"
                            print
                            traceback.print_exc()
                            print
                        else:
                            print "[OK]"
                    else:
                        print "[already applied]"
                finally: 
                    cursor.close()
            finally:
                connection.close()
        finally:
            session.close()

    def check(self, cursor):
        raise UnimplementedError("Not implemented!")
  
    def apply(self, cursor):
        raise UnimplementedError("Not implemented!")


class PatchApplier(object):
    def __init__(self, user, password, db, order):
        self.user     = user
        self.password = password
        self.db       = db
        self.order    = order

    def execute(self, force = False):
        for klass in Patch.__subclasses__():
            if not klass in self.order:
                print "WARNING: Class %s not found in provided order: " % klass.__name__,
                if force:
                    print "[skipped]"
                else:
                    print "[aborted]"
                    raise Exception("Class %s not found in provided order. Call execute(force=True) if this is correct" % klass.__name__)

        # Always recreate all the tables
        connection_url = "mysql://%(USER)s:%(PASS)s@%(HOST)s/%(NAME)s" % {
                                "USER": self.user,
                                "PASS": self.password,
                                "HOST": "localhost",
                                "NAME": self.db }

        engine = create_engine(connection_url, convert_unicode=True, echo=False)
        Model.Base.metadata.create_all(engine)

        for klass in self.order:
            fix = klass(self.user, self.password, self.db)
            fix.execute()

