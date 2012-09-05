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

from weblabDeployer import db

class User(db.Model):
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String)
    full_name = db.Column(db.String)
    active = db.Column(db.Boolean)
    
    token_id = db.Column(db.Integer, db.ForeignKey('tokens.id'))
    token = db.relationship('Token', cascade="all, delete-orphan",
                                single_parent=True,
                                uselist=False, #This 
                                backref=db.backref('user', uselist=False)) #and this are for one-to-one

    entity_id = db.Column(db.Integer, db.ForeignKey('entities.id'))
    entity = db.relationship('Entity', single_parent=True,
                                uselist=False, #This 
                                backref=db.backref('user', uselist=False))
     
    def __init__(self, email, password):
        self.email = email
        self.password = password


class Token(db.Model):
    
    __tablename__ = 'tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String, unique=True)
    
    def __init__(self, token):
        self.token = token


class Entity(db.Model):
    
    __tablename__ = 'entities'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)#. e.g. University of Deusto
    logo = db.Column(db.LargeBinary)#e.g. (the logo of the entity)
    base_url = db.Column(db.String)#e.g. /myschool.
    link_url = db.Column(db.String)#e.g. http://www.deusto.es
    google_analytics_number = db.Column(db.String)#e.g. UA-1234-1234
    
    def __init__(self, name, base_url):
        self.name = name
        self.base_url = base_url