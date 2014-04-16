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

from wcloud.flaskapp import app, db
import wcloud.models
import wcloud.views
import wcloud.admin

if __name__ == '__main__':

    # Create the database if it doesn't exist already.
    # TODO: Check that this doesn't delete information if it exists already.
    db.create_all()

    app.run(debug=app.config['DEBUG'])