from flask import render_template, request, flash, redirect, url_for, session
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
            session["sessionid"] = sessionid
            return redirect(url_for("labs"))
        except:
            flash("Invalid username or password", category="error")
            return redirect(url_for("index"))

    return render_template("index.html")