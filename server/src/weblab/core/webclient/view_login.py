from __future__ import print_function, unicode_literals
import traceback
from flask import render_template, request, flash, redirect, url_for, jsonify, g
from weblab.core.login.exc import InvalidCredentialsError
from weblab.core.webclient.helpers import safe_redirect, WebError, json_exc, web_exc
from weblab.core.webclient.view_labs import labs as labs_view
from weblab.core.i18n import gettext
from weblab.core.wl import weblab_api
from weblab.core.exc import SessionNotFoundError


@weblab_api.route_webclient("/login", methods=["GET", "POST"])
def login():
    """
    Handles the index screen displaying (GET) and login (POST).
    """

    # THIS POST WILL ONLY BE INVOKED IF JAVASCRIPT IS DISABLED.
    # Otherwise logging is handled from JS.
    if request.method == "POST":
        return handle_login_POST()

    return handle_login_GET()

@weblab_api.route_webclient("/login/service", methods=["POST"])
@json_exc
def login_service():
    contents = request.get_json(force=True, silent=True)
    if contents == False or not isinstance(contents, dict):
        return weblab_api.jsonify(error = True, message = "Error reading username and password")

    username = contents.get('username', '')
    password = contents.get('password', '')

    try:
        session_id = weblab_api.api.login(username, password)
    except InvalidCredentialsError:
        return weblab_api.jsonify(error = True, message = gettext("Invalid username or password"))

    return weblab_api.jsonify(error = False, redirect = get_next_url())

def handle_login_POST():
    """
    Carries out an actual log in.
    :return:
    """

    # If this is a POST it is a login request.
    #
    username = request.values.get("username")
    password = request.values.get("password")

    # We may or may not have a 'next' field. If we do, we make sure that the URL is safe.
    try:
        session_id = weblab_api.api.login(username, password)
    except InvalidCredentialsError:
        flash(gettext("Invalid username or password"), category="error")
        # _scheme is a workaround. See comment in other redirect.
        return redirect(url_for(".login", _external=True, _scheme=request.scheme))
    except:
        traceback.print_exc()
        flash(gettext("There was an unexpected error while logging in."), 500)
        return weblab_api.make_response(gettext("There was an unexpected error while logging in."), 500)
    else:
        # TODO: Find proper way to do this.
        # This currently redirects to HTTP even if being called from HTTPS. Tried _external as a workaround but didn't work.
        # More info: https://github.com/mitsuhiko/flask/issues/773
        # For now we force the scheme from the request.
        return weblab_api.make_response(redirect(get_next_url()))

def handle_login_GET():
    """
    Displays the index (the login page).
    """
    if request.args.get('next'):
        url_kwargs = dict(next=request.args.get('next'))
    else:
        url_kwargs = {}

    try:
        weblab_api.api.check_user_session()
    except SessionNotFoundError:
        pass # Expected behavior
    else:
        # User is already logged in, send him to the next url
        return redirect(get_next_url())

    return render_template("webclient/login.html", url_kwargs = url_kwargs)


@weblab_api.route_webclient("/logout",  methods=["GET", "POST"])
def logout():
    """
    Logout will logout the current session and redirect to the main page.
    """
    try:
        weblab_api.api.logout()
    except SessionNotFoundError:
        # We weren't logged in but it doesn't matter because we want to logout anyway.
        pass

    return redirect(url_for(".login", _external=True, _scheme=request.scheme))

@weblab_api.route_webclient("/demo")
def demo():
    if not weblab_api.config.client.get('demo.available'):
        return "Not found", 404

    username = weblab_api.config.client.get('demo.username')
    password = weblab_api.config.client.get('demo.password')

    if username is None or password is None:
        # TODO: mail the admin, use an errors template
        return "Invalid configuration! Contact the administrator so he puts the username and password for the demo account"

    try:
        session_id = weblab_api.api.login(username, password)
    except InvalidCredentialsError:
        # TODO: mail the admin, use an errors template
        return "Invalid configuration! Contact the administrator so he correctly puts the username and password for the demo account"
    
    if hasattr(g, 'next_url') or request.args.get('next'):
        return weblab_api.make_response(redirect(get_next_url()))

    return labs_view()

def get_next_url():
    if hasattr(g, 'next_url'):
        next_url = g.next_url
    else:
        next_url = request.args.get("next")
    next_url = safe_redirect(next_url)
    return next_url or url_for(".labs", _external=True, _scheme=request.scheme)

