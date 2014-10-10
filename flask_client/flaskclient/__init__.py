from flask import render_template, jsonify, Response
from flaskclient.flask_app_builder import build_flask_app
import requests
import re
from flaskclient.helpers import _retrieve_configuration_js

flask_app = build_flask_app()
flask_app.config.from_pyfile("../config.py")

# Import the different flask_views. This needs to be exactly here because
# otherwise the @flask_app notation wouldn't work.
import view_index
import view_upload
import view_labs


@flask_app.route("/lab.html")
def lab():
    return render_template("lab.html")


@flask_app.route("/contact.html")
def contact():
    return render_template("contact.html")


@flask_app.route("/test.html")
def test():
    return render_template("test.html")


@flask_app.route("/configuration")
def configuration():
    """
    Returns the Weblab configuration JSON file. This is mostly for testing. It will eventually
    be removed. It will also filter comments so that the contents can be parsed as valid JSON.
    @return: Configuration file as a JSON response.
    @rtype: Response
    """
    js = _retrieve_configuration_js()
    return Response(js, mimetype="application/json")
