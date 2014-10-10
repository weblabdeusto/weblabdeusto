from flask import render_template
from flaskclient import flask_app


@flask_app.route("/labs.html")
def labs():
    return render_template("labs.html")