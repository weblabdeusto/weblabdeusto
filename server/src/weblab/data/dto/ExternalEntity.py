#!/usr/bin/env python
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
# Author: Jaime Irurzun <jaime.irurzun@gmail.com>
#

class ExternalEntity(object):
    
    def __init__(self, name, country, description, email, id=None):
        super(ExternalEntity,self).__init__()
        self.id = id
        self.name = name
        self.country = country
        self.description = description
        self.email = email

    def __repr__(self):
        return "ExternalEntity(id = %i, name = '%s', country = '%s', description = '%s', email = '%s')" % (
                self.name,
                self.country,
                self.description,
                self.email
            )