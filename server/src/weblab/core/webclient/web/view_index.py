from __future__ import print_function, unicode_literals
import traceback
from flask import render_template, request, flash, redirect, url_for, make_response
from weblab.core.login.exc import InvalidCredentialsError
from weblab.core.webclient.web.helpers import safe_redirect

from weblab.core.wl import weblab_api
from weblab.core.exc import SessionNotFoundError


@weblab_api.route_webclient("/", methods=["GET", "POST"])
def index():
    """
    Handles the index screen displaying (GET) and login (POST).
    """

    # THIS POST WILL ONLY BE INVOKED IF JAVASCRIPT IS DISABLED.
    # Otherwise logging is handled from JS.
    if request.method == "POST":
        return handle_login_POST()

    return handle_login_GET()

def handle_login_POST():
    """
    Carries out an actual log in.
    :return:
    """

    # If this is a POST it is a login request.
    #
    username = request.values.get("username")
    password = request.values.get("password")
    guestlogin = request.values.get("guestlogin")

    # If we have a guestlogin then it is a DEMO login request.
    if guestlogin is not None:
        username = "demo"
        password = "demo"

    # We may or may not have a 'next' field. If we do, we make sure that the URL is safe.
    next = request.values.get("next")
    next = safe_redirect(next)

    try:
        session_id = weblab_api.api.login(username, password)
    except InvalidCredentialsError:
        flash("Invalid username or password", category="error")
        # _scheme is a workaround. See comment in other redirect.
        return redirect(url_for(".index", _external=True, _scheme=request.scheme))
    except:
        traceback.print_exc()
        flash("There was an unexpected error while logging in.", 500)
        return make_response("There was an unexpected error while logging in.", 500)
    else:
        # TODO: Find proper way to do this.
        # This currently redirects to HTTP even if being called from HTTPS. Tried _external as a workaround but didn't work.
        # More info: https://github.com/mitsuhiko/flask/issues/773
        # For now we force the scheme from the request.
        response = make_response(redirect(next or url_for(".labs", _external=True, _scheme=request.scheme)))
        """ @type: flask.Response """

        session_id_cookie = '%s.%s' % (session_id.id, weblab_api.ctx.route)

        # Inserts the weblabsessionid and loginsessionid cookies into the response.
        # (What is the purpose of having both? Why the different expire dates?)
        weblab_api.fill_session_cookie(response, session_id_cookie)
        return response

def handle_login_GET():
    """
    Displays the index (the login page).
    """
    return render_template("webclient_web/index.html")



@weblab_api.route_webclient("/logout",  methods=["GET", "POST"])
def logout():
    """
    Logout will logout the current session and redirect to the main page.
    """
    try:
        # TODO: Take into account the somewhat unclear difference between the loginweblabsessionid and the other one.
        cookie = request.cookies.get("weblabsessionid", None)
        if cookie is not None:
            # Prepare to call the weblab_api
            weblab_api.ctx.reservation_id = cookie
            weblab_api.api.logout()
    except SessionNotFoundError:
        # We weren't logged in but it doesn't matter because we want to logout anyway.
        pass

    return redirect(url_for(".index", _external=True, _scheme=request.scheme))

@weblab_api.route_webclient("/demo")
def demo():
    # TODO: log in
    return ":-)"

