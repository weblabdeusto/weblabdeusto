from flask import render_template, url_for, request
import requests
from flaskclient import flask_app
from flaskclient.helpers import _retrieve_configuration_js


@flask_app.route("/labs.html")
def labs():
    """
    Renders the Laboratories List.
    """

    # To properly render the labs list we need access to the configuration.js file (this will change in the
    # future). We actually request this to ourselves.
    config = _retrieve_configuration_js()
    print config

    return render_template("labs.html")