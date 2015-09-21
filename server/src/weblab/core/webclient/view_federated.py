from __future__ import print_function, unicode_literals

import datetime
from flask import render_template, request, flash, redirect, url_for, jsonify, session

from weblab.core.wl import weblab_api

# ../../client/index.html%(localization)s#reservation_id=%(reservation_id)s&back_url=%(back_url)s&widget=%(widget)s

@weblab_api.route_webclient('/federated/')
def federated():
    redirecting = session.pop('federated_redirecting', None)
    widget = request.args.get('widget')
    reservation_id = request.args.get('reservation_id')
    reservation_tokens = reservation_id.split(';')
    if len(reservation_tokens) == 1:
        reservation_id = reservation_tokens[0]
    else:
        reservation_id = reservation_tokens[0]
        reservation_id_plus_route = reservation_tokens[1]
        if '.' in reservation_id_plus_route:
            route = reservation_id_plus_route.split('.', 1)[1]
            if route != weblab_api.ctx.route:
                if redirecting:
                    return "Invalid federated URL: you're attempting to use a route not used in this WebLab-Deusto instance"

                session['federated_redirecting'] = "true"
                response = redirect(request.url)
                now = datetime.datetime.now()
                response.set_cookie('weblabsessionid', reservation_id_plus_route, expires = now + datetime.timedelta(days = 100), path = weblab_api.ctx.location)
                return response
    
    weblab_api.ctx.reservation_id = reservation_id
    try:
        experiment = weblab_api.api.get_reservation_experiment_info()
    except:
        # TODO
        raise

    session['reservation_id'] = reservation_id
    session['back_url'] = request.args.get('back_url')
    return redirect(url_for('.lab', experiment_name=experiment.name, category_name=experiment.category.name))

