# -*- coding: utf-8 -*-
#
# Copyright (C) 2012 onwards University of Deusto
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#
# This software consists of contributions made by many individuals,
# listed below:
#
# Author: Xabier Larrakoetxea <xabier.larrakoetxea@deusto.es>
# Author: Pablo Orduña <pablo.orduna@deusto.es>
#
# These authors would like to acknowledge the Spanish Ministry of science
# and innovation, for the support in the project IPT-2011-1558-430000
# "mCloud: http://innovacion.grupogesfor.com/web/mcloud"
#

from wcloud.flaskapp import db
from sqlalchemy import func, Unicode, String, Column, Integer, Boolean, DateTime

class User(db.Model):

    __tablename__ = 'users'

    id             = Column(Integer, primary_key=True)
    email          = Column(Unicode(200), nullable=False, unique=True, index = True)
    password       = Column(Unicode(200), nullable=False)
    full_name      = Column(Unicode(200), nullable=False)
    ip_address     = Column(Unicode(200))
    creation_date  = Column(DateTime)
    active         = Column(Boolean, nullable = False)
    is_admin       = Column(Boolean, nullable = True, server_default = "0")

    token_id = Column(Integer, db.ForeignKey('tokens.id'))
    token    = db.relationship('Token', cascade="all, delete-orphan",
                                single_parent=True,
                                uselist=False, #This
                                backref=db.backref('user', uselist=False)) #and this are for one-to-one

    entity_id = Column(Integer, db.ForeignKey('entities.id'))
    entity = db.relationship('Entity', single_parent=True,
                                uselist=False, #This
                                backref=db.backref('user', uselist=False))

    def __init__(self, email, password, full_name):
        self.email = email
        self.password = password
        self.full_name = full_name

    # TODO: Consider whether we should use this from wcloud_tasks or not. And fix it accordingly.
    @staticmethod
    def total_users():
        return db.session.query(func.count(User.id)).first()[0]

    @staticmethod
    def user_exists(email):
        return User.query.filter_by(email=email).first() is not None

class Token(db.Model):

    __tablename__ = 'tokens'

    id    = Column(Integer, primary_key=True)
    token = Column(String(200), nullable=False, unique=True, index=True)
    date  = Column(DateTime, nullable=False)

    def __init__(self, token, date):
        self.token = token
        self.date  = date


class Entity(db.Model):

    __tablename__ = 'entities'

    id                      = Column(Integer, primary_key=True)
    name                    = Column(Unicode(200), unique=True, nullable=False, index=True) # e.g. University of Deusto
    logo                    = Column(db.LargeBinary(16 * 1024 * 1024), nullable=False)           # e.g. (the logo of the entity)
    logo_ext                = Column(Unicode(4), nullable=False)           # e.g. '.jpeg'
    base_url                = Column(Unicode(200), unique=True, nullable=False, index=True) # e.g. myschool (as in http://www.deusto.es/myschool)
    link_url                = Column(Unicode(300), nullable=False)             # e.g. http://www.deusto.es
    google_analytics_number = Column(Unicode(30))                              # e.g. UA-1234-1234
    start_port_number       = Column(Integer) # Null until the task manager assigns them
    end_port_number         = Column(Integer, index=True) # Null until the task manager assigns them
    deployed                = Column(Boolean, nullable = False)
    db_name                 = Column(Unicode(200), unique=True)  # TODO: Make this the right size. I assume the db name should be unique.

    def __init__(self, name, base_url):
        self.name = name
        self.base_url = base_url
        self.deployed = False

    @staticmethod
    def last_port():
        return db.session.query(func.max(Entity.end_port_number)).one()[0]

    @staticmethod
    def url_exists(user_email, base_url):
        entity = Entity.query.filter_by(base_url=base_url).first()
        return entity is not None and entity.user.email != user_email
        
