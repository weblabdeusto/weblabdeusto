from collections import defaultdict
import json
import os
import urllib

from flask import render_template, url_for, request, flash, redirect

from helpers import remove_comments_from_json

import requests
from weblab.core.wl import weblab_api
import hashlib


@weblab_api.route_webclient("/labs.html")
def labs():
    """
    Renders the Laboratories List.
    """
    # We also want access to the experiment's list for the user.
    # TODO: Take into account the somewhat unclear difference between the loginweblabsessionid and the other one.
    cookie = request.cookies.get("weblabsessionid", None)
    if cookie is None:
        flash("You are not logged in", category="error")
        return redirect(url_for(".index"))

    # experiments, experiments_by_category = get_experiments_data(sessionid, route)
    experiments, experiments_by_category = {}, {}

    # Prepare to call the weblab_api
    weblab_api.ctx.reservation_id = cookie
    experiments_raw = weblab_api.api.list_experiments()

    experiments, experiments_by_category = _get_experiment_info(experiments_raw)
    loggedin_info = _get_loggedin_info()

    return render_template("webclient_web/labs.html", experiments=experiments,
                           experiments_by_category=experiments_by_category,
                           urllib=urllib, loggedin=loggedin_info)


def _get_loggedin_info():
    """
    Returns a dictionary with several parameters to render the logged_in part of the website.
    PRERREQUISITE: weblab_api.ctx.reservation_id must be set.
    :return: info dictionary
    :rtype: dict
    """

    # Retrieve the configuration.js info.
    core_server_url = weblab_api.server_instance.core_server_url
    configuration_js_url = os.path.join(*[core_server_url, "client", "weblabclientlab", "configuration.js"])
    configuration_js = requests.get(configuration_js_url).content
    configuration_js = remove_comments_from_json(configuration_js)
    configuration_js = json.loads(configuration_js)

    # Retrieve user information
    user_info = weblab_api.api.get_user_information()

    # Calculate the admin and profile urls.
    admin_url = os.path.join(*[core_server_url, ""])
    profile_url = os.path.join(*[core_server_url, ""])

    # Calculate the Gravatar from the mail
    gravatar_url = "http://www.gravatar.com/avatar/" + hashlib.md5(user_info.email.lower()).hexdigest() + "?"
    gravatar_url += urllib.urlencode({'d': "http://placehold.it/150x150", 's': str(50)})

    info = {}
    info["logo_url"] = os.path.join(*[core_server_url, "client", "weblabclientlab", configuration_js["host.entity.image"].lstrip('/')])
    info["host_link"] = configuration_js["host.entity.link"]
    info["full_name"] = user_info.full_name
    info["gravatar"] = gravatar_url

    return info


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
