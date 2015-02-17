from collections import defaultdict
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
    # TODO: Take into account the somewhat unclear difference between the loginweblabsessionid and the other one.
    cookie = request.cookies.get("loginweblabsessionid", None)
    if cookie is None:
        flash("You are not logged in", category="error")
        return redirect(url_for(".index"))

    # experiments, experiments_by_category = get_experiments_data(sessionid, route)
    experiments, experiments_by_category = {}, {}

    # Prepare to call the weblab_api
    weblab_api.ctx.reservation_id = cookie
    experiments_raw = weblab_api.api.list_experiments()

    experiments, experiments_by_category = _get_experiment_info(experiments_raw)

    return render_template("webclient_web/labs.html", experiments=experiments, experiments_by_category=experiments_by_category,
                           urllib=urllib)


def _get_experiment_info(experiments_raw):
    """
    Retrieves a data-only dict with the allowed experiments by name and an index of these same experiments
    by their categories.
    :param experiments_raw: Raw experiments list as returned by list_experiments API.
    :return: (experiments, experiments_by_category)
    """
    experiments = {}
    experiments_by_category = defaultdict(list)

    for raw_exp in experiments_raw:
        exp = {}
        exp["name"] = raw_exp.experiment.name
        exp["category"] = raw_exp.experiment.category.name
        exp["time"] = raw_exp.time_allowed
        exp["type"] = raw_exp.experiment.client.client_id
        exp["config"] = raw_exp.experiment.client.configuration

        experiments[exp["name"]] = exp
        experiments_by_category[exp["category"]].append(exp)

    return experiments, experiments_by_category
