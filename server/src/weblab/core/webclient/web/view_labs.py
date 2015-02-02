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
    cookie = request.cookies.get("loginweblabsessionid", None)
    if cookie is None:
        flash("You are not logged in", category="error")
        return redirect(url_for(".index"))

    # experiments, experiments_by_category = get_experiments_data(sessionid, route)
    experiments, experiments_by_category = {}, {}

    return render_template("webclient_web/labs.html", experiments=experiments, experiments_by_category=experiments_by_category,
                           urllib=urllib)
