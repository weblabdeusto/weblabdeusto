import urllib

from flask import render_template, url_for, request, flash, redirect

# from weblab.webclient.web.helpers import get_experiments_data
from weblab.core.wl import weblab_api


@weblab_api.route_webclient("/labs.html")
def labs():
    """
    Renders the Laboratories List.
    """
    # We also want access to the experiment's list for the user.
    sessionid = request.cookies.get("sessionid", None)
    route = request.cookies.get("route", "")
    if sessionid is None:
        flash("You are not logged in", category="error")
        return redirect(url_for(".index"))

    # experiments, experiments_by_category = get_experiments_data(sessionid, route)
    experiments, experiments_by_category = {}, {}

    return render_template("labs.html", experiments=experiments, experiments_by_category=experiments_by_category,
                           urllib=urllib)
