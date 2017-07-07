from __future__ import print_function, unicode_literals

import datetime
from flask import render_template, request, flash, redirect, url_for, jsonify, session

from weblab.core.wl import weblab_api
from weblab.core.i18n import gettext
from weblab.core.exc import SessionNotFoundError

# ../../client/index.html%(localization)s#reservation_id=%(reservation_id)s&back_url=%(back_url)s&widget=%(widget)s

@weblab_api.route_webclient('/client/federated.html')
def federated_html():
    return render_template('webclient/federated_legacy.html')

@weblab_api.route_webclient('/client/')
def client_html():
    return render_template('webclient/index_legacy.html')

@weblab_api.route_webclient('/client/index.html')
def client_index_html():
    return render_template('webclient/index_legacy.html')

@weblab_api.route_webclient('/federated/')
def federated():
    redirecting = session.pop('federated_redirecting', None)
    widget = request.args.get('widget')
    reservation_id = request.args.get('reservation_id')
    reservation_tokens = reservation_id.split(';')
    back_url = request.args.get('back_url')
    if len(reservation_tokens) == 1:
        reservation_id = reservation_tokens[0]
    else:
        reservation_id = reservation_tokens[0]
        reservation_id_plus_route = reservation_tokens[1]
        # The second argument is the session identifier plus a route. 
        # Here we analyze whether this message was intended for this server or for any other with a different route.
        # To do this, we check the route, and if it's different, we return a redirection to the same URL but setting a cookie with the required URL
        # However, if we were already redirecting, then there is a problem (e.g., not using an existing route), and a message is displayed.
        if '.' in reservation_id_plus_route:
            route = reservation_id_plus_route.split('.', 1)[1]
            if route != weblab_api.ctx.route:
                if redirecting:
                    return render_template("webclient/error.html", error_message = gettext("Invalid federated URL: you're attempting to use a route not used in this WebLab-Deusto instance"), federated_mode = True, title = gettext("Error"), back_url = back_url)

                session['federated_redirecting'] = "true"
                response = redirect(request.url)
                now = datetime.datetime.now()
                response.set_cookie('weblabsessionid', reservation_id_plus_route, expires = now + datetime.timedelta(days = 100), path = weblab_api.ctx.location)
                return response

    weblab_api.ctx.reservation_id = reservation_id
    try:
        experiment = weblab_api.api.get_reservation_experiment_info()
    except SessionNotFoundError:
        return render_template("webclient/error.html", error_message = gettext("The provided reservation identifier is not valid or has expired."), federated_mode = True, back_url = back_url)
    except:
        traceback.print_exc()
        return render_template("webclient/error.html", error_message = gettext("Unexpected error on the server side while trying to get the reservation information."), federated_mode = True, back_url = back_url)

    session['reservation_id'] = reservation_id
    session['back_url'] = request.args.get('back_url')
    if request.args.get('locale'):
        session['locale'] = request.args.get('locale')
    response = redirect(url_for('.lab', experiment_name=experiment.name, category_name=experiment.category.name))
    reservation_id_plus_route = '%s.%s' % (reservation_id, weblab_api.ctx.route)
    weblab_api.fill_session_cookie(response, reservation_id_plus_route, reservation_id)
    return response

