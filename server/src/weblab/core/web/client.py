#!/usr/bin/env python
#-*-*- encoding: utf-8 -*-*-
#
# Copyright (C) 2005 onwards University of Deusto
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#
# This software consists of contributions made by many individuals,
# listed below:
#
# Author: Pablo Orduña <pablo@ordunya.com>
#         Luis Rodriguez <luis.rodriguez@opendeusto.es>
#
from __future__ import print_function, unicode_literals

from flask import request, render_template, make_response, redirect, url_for
from weblab.core.wl import weblab_api

import urllib
from weblab.core.exc import SessionNotFoundError

RESERVATION_ID   = 'reservation_id'
BACK_URL         = 'back_url'
LOCALE           = 'locale'
FORMAT_PARAMETER = 'format'
WIDGET           = 'widget'

@weblab_api.route_web('/client/', methods = ['GET', 'POST'])
def client():
    """
    If there is a GET argument named %(reservation_id)s, it will take it and resend it as a
    POST argument. If it was passed through the history, then it will be again sent as a
    POST argument. Finally, if it is received as a POST argument, it will generate a redirect
    to the client, using the proper current structure.
    """ % { 'reservation_id' : RESERVATION_ID }

    # If it is passed as a GET argument, send it as POST
    reservation_id = request.args.get(RESERVATION_ID)
    back_url       = request.args.get(BACK_URL)
    locale         = request.args.get(LOCALE)
    widget         = request.args.get(WIDGET) or ''
    if reservation_id is not None:
        return render_template('core_web/client_redirect.html',
            reason = 'GET performed',
            reservation_id = urllib.unquote(reservation_id),
            back_url = back_url, locale = locale, widget = widget)

    # If it is passed as History (i.e. it was not passed by GET neither POST),
    # pass it as a POST argument
    reservation_id = request.form.get(RESERVATION_ID)
    if reservation_id is None:
        return render_template('core_web/client_label.html')

    back_url = request.form.get(BACK_URL)
    widget   = request.form.get(WIDGET) or ''
    locale   = request.form.get(LOCALE) or ''

    reservation_id = urllib.unquote(reservation_id)

    route = weblab_api.ctx.route
    if route is not None:
        # If the request should not go to the current server
        if reservation_id.find('.') >= 0 and not reservation_id.endswith(route):
            if reservation_id.find(';') >= 0:
                partial_reservation_id = reservation_id.split(';')[1]
            else:
                partial_reservation_id = reservation_id

            response = make_response(render_template('core_web/client_redirect.html',
                reason         = 'reservation_id %s does not end in server_route %s' % (reservation_id, weblab_api.ctx.route),
                reservation_id = reservation_id, back_url = back_url, 
                locale = locale, widget = widget,
            ))
            weblab_api.fill_session_cookie(response, partial_reservation_id)
            return response

    if reservation_id.find(';') >= 0:
        partial_reservation_id = reservation_id.split(';')[1]
    else:
        partial_reservation_id = reservation_id

    response = make_response()
    weblab_api.fill_session_cookie(response, partial_reservation_id)

    # Finally, if it was passed as a POST argument, generate the proper client address
    weblab_api.ctx.reservation_id = reservation_id.split(';')[0]
    try:
        experiment_id = weblab_api.api.get_reservation_info()
    except SessionNotFoundError:
        response.response = render_template('core_web/client_error.html', reservation_id = reservation_id)
        return response

    client_address = url_for('core_webclient.federated', locale=locale, reservation_id=reservation_id, back_url=back_url, widget=widget)
    format_parameter = request.form.get(FORMAT_PARAMETER)
    if format_parameter is not None and format_parameter == 'text':
        response.response = client_address
        return response

    return redirect(client_address)

