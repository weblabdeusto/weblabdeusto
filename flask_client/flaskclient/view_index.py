from flask import render_template, request, flash, redirect, url_for, session, make_response, Response
from flaskclient import flask_app
from flaskclient.weblabweb import WeblabWeb


@flask_app.route("/", methods=["GET", "POST"])
def index():
    """
    This is actually the login method.
    """
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
            sessionid = weblabweb._login(username, password)

            response = make_response(redirect(url_for("labs")))
            """ @type: flask.Response """

            # We set it in a cookie rather than session so that is is immediately interoperable with JS
            response.set_cookie("sessionid", sessionid)

            return redirect(url_for("labs"))
        except:
            flash("Invalid username or password", category="error")
            return redirect(url_for("index"))

    return render_template("index.html")


@flask_app.route("/logout",  methods=["GET", "POST"])
def logout():
    """
    Logout will logout the current session and redirect to the main page.
    """
    sessionid = request.cookies.get("sessionid")
    if sessionid is not None:
        try:
            weblabweb = WeblabWeb()
            weblabweb._logout(sessionid)
        except:
            flash("Could not logout", category="warning")

    return redirect(url_for("index"))

