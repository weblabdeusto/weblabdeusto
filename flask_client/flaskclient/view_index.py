from flask import render_template, request
from flaskclient import flask_app



@flask_app.route("/")
def index():
    """
    This is actually the login method.
    """
    if request.method == "POST":
        # If this is a POST it is a login request.
        #
        pass

    return render_template("index.html")