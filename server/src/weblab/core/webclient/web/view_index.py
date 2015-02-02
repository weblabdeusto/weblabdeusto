import traceback
from flask import render_template, request, flash, redirect, url_for, make_response
from weblab.core.login.exc import InvalidCredentialsError
from weblab.core.webclient.web.weblabweb import WeblabWeb

from weblab.core.wl import weblab_api


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

    try:
        session_id = weblab_api.api.login(username, password)
    except InvalidCredentialsError:
        flash("Invalid username or password", category="error")
        return redirect(url_for(".index"))
    except:
        traceback.print_exc()
        flash("There was an unexpected error while logging in.", 500)
        return make_response("There was an unexpected error while logging in.", 500)
    else:
        response = make_response(redirect(url_for(".labs")))
        """ @type: flask.Response """

        session_id_cookie = '%s.%s' % (session_id.id, weblab_api.ctx.route)

        # Inserts the weblabsessionid and loginsessionid cookies into the response.
        # (What is the purpose of having both? Why the different expire dates?)
        weblab_api.fill_session_cookie(response, session_id_cookie)


        print "LOGGED IN WITH: (%s)" % (session_id_cookie)

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

