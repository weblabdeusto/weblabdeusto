from flask import render_template, request, flash, redirect, url_for, make_response
from weblab.core.webclient.web.weblabweb import WeblabWeb

from weblab.core.wl import weblab_api


@weblab_api.route_webclient("/", methods=["GET", "POST"])
def index():
    """
    This is actually the login method.
    """

    # THIS POST WILL ONLY BE INVOKED IF JAVASCRIPT IS DISABLED.
    # Otherwise logging is handled from JS.
    if request.method == "POST":
        # If this is a POST it is a login request.
        #
        username = request.values.get("username")
        password = request.values.get("password")

        if not username or not password:
            flash("Username and password must be filled", category="error")
            return redirect(url_for("index"))

        try:
            weblabweb = WeblabWeb()
            # weblabweb.set_target_urls(flask_app.config["LOGIN_URL"], flask_app.config["CORE_URL"])
            sessionid, route = weblabweb._login(username, password)


            response = make_response(redirect(url_for("labs")))
            """ @type: flask.Response """

            # We set it in a cookie rather than session so that is is immediately interoperable with JS
            response.set_cookie("sessionid", sessionid)
            response.set_cookie("route", route) # Save the route too, we need to use it from the Python-API

            print "LOGGED IN WITH: (%s, %s)" % (sessionid, route)

            return response
        except:
            flash("Invalid username or password", category="error")
            return redirect(url_for("index"))

    return render_template("webclient_web/index.html")


@weblab_api.route_webclient("/logout",  methods=["GET", "POST"])
def logout():
    """
    Logout will logout the current session and redirect to the main page.
    """
    sessionid = request.cookies.get("sessionid")
    route = request.cookies.get("route")
    if sessionid is not None:
        try:
            weblabweb = WeblabWeb()
            # weblabweb.set_target_urls(flask_app.config["LOGIN_URL"], flask_app.config["CORE_URL"])
            weblabweb._feed_cookies({"weblabsessionid": "%s.%s" % (sessionid, route)})
            weblabweb._logout(sessionid)
        except:
            flash("Could not logout", category="warning")

    return redirect(url_for("index"))

