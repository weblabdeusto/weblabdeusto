from collections import defaultdict
from flask import render_template, url_for, request, flash, redirect, json, session
import urllib
import requests
from flaskclient import flask_app
from flaskclient.G import G
from flaskclient.helpers import _retrieve_configuration_js
from flaskclient.weblabweb import WeblabWeb



@flask_app.route("/lab.html")
def lab():
    """
    Renders a specific laboratory.
    """
    name = request.values.get("name")
    category = request.values.get("category")
    type = request.values.get("type")

    if name is None or category is None or type is None:
        return "500 Please specify a name and category", 500

    sessionid = request.cookies.get("sessionid", None)
    if sessionid is None:
        flash("You are not logged in", category="error")
        return redirect(url_for("index"))


    # Access experiment data.
    # TODO: Globals won't really work with most setups, it should be changed eventually.
    experiments = G["sessiondata"][sessionid]

    experiment = {
        "name": name,
        "category": category
    }

    experiment = experiments["%s@%s" % (name, category)]



    return render_template("lab.html", experiment=experiment, experiment_type = type)