from collections import defaultdict
from flask import render_template, url_for, request, flash, redirect, json, session
import urllib
import requests
from flaskclient import flask_app, get_experiments_data, _retrieve_configuration_js
from flaskclient.G import G
from flaskclient.helpers import build_experiments_list
from flaskclient.weblabweb import WeblabWeb



@flask_app.route("/labs.html")
def labs():
    """
    Renders the Laboratories List.
    """
    # We also want access to the experiment's list for the user.
    sessionid = request.cookies.get("sessionid", None)
    route = request.cookies.get("route", "")
    if sessionid is None:
        flash("You are not logged in", category="error")
        return redirect(url_for("index"))

    experiments, experiments_by_category = get_experiments_data(sessionid, route)

    return render_template("labs.html", experiments = experiments, experiments_by_category = experiments_by_category, urllib = urllib)
