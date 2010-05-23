#-*-*- encoding: utf-8 -*-*-
#
# Copyright (C) 2005-2009 University of Deusto
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#
# This software consists of contributions made by many individuals, 
# listed below:
#
# Author: Pablo Orduña <pablo@ordunya.com>
#

import datetime
import time
from sqlalchemy import Column, String, DateTime, Binary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import IntegrityError


SessionBase = declarative_base()

class Session(SessionBase):
    __tablename__  = 'Sessions'

    sess_id         = Column(String(100), primary_key = True)
    session_pool_id = Column(String(100), nullable = False)
    start_date      = Column(DateTime(),  nullable = False)
    latest_access   = Column(DateTime())
    latest_change   = Column(DateTime())
    session_obj     = Column(Binary(), nullable = False)

    def __init__(self, sess_id, session_pool_id, start_date, session_obj):
        self.sess_id         = sess_id
        self.session_pool_id = session_pool_id
        self.start_date      = start_date
        self.session_obj     = session_obj

if __name__ == '__main__':
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    weblab_db_username = 'wl_session_user'
    weblab_db_password = 'wl_session_user_password'
    engine = create_engine('mysql://%s:%s@localhost/WebLabSessions' % (weblab_db_username, weblab_db_password), echo = False)
    metadata = SessionBase.metadata
    metadata.drop_all(engine)
    metadata.create_all(engine)

    session_maker = sessionmaker(bind=engine, autoflush = True, autocommit = False)
    session = session_maker()

    sess1 = Session("asdf", "id1", datetime.datetime.now(), "Foo")
    session.add(sess1)

    session.commit()
    session.close()



    while True:
        try:
            session = session_maker()
            sess2 = Session("asdf", "id1", datetime.datetime.now(), "Foo")
            session.add(sess2)

            session.commit()
        except IntegrityError, ie:
            print "Te pille"
            time.sleep(0.5)
        else:
            break
        finally:
            session.close()

    print "Hecho"


