from collections import defaultdict
from flask import render_template, url_for, request, flash, redirect, json
import urllib
import requests
from flaskclient import flask_app
from flaskclient.G import G
from flaskclient.helpers import _retrieve_configuration_js
from flaskclient.weblabweb import WeblabWeb


def build_experiments_list(experiments_list, experiments_config):
    """
    Builds a merged experiments list which contains, for only those experiments which the user
    is allowed to use, the extra information contained within experiments_config.

    @param experiments_list {list[object]}: List of experiments, provided by the experiments_list Weblab method.
    @param experiments_config {dict}: Configuration JS file (which will eventually be removed).
    @returns {dict[object], dict[object]}: Experiments dictionary, experiments_by_category
    """
    experiments = {}
    experiments_by_category = defaultdict(list)

    # First, store the info available from the experiments_list into the experiments registry.
    for exp_data in experiments_list:
        category = exp_data["experiment"]["category"]["name"]
        exp_name = exp_data["experiment"]["name"]
        time_allowed = exp_data["time_allowed"]
        experiments["%s@%s" % (exp_name, category)] = {"time_allowed": time_allowed}

    # Now, merge the data from experiments_config into the experiments which are available for the user
    exps = experiments_config["experiments"]
    for exp_type, exp_list in exps.items():
        for exp_config in exp_list:
            key = exp_config["experiment.name"] + "@" + exp_config["experiment.category"]
            if key in experiments:
                exp_config["experiment_type"] = exp_type
                experiments[key].update(exp_config)
                experiments_by_category[exp_config["experiment.category"]] = experiments[key]

    return experiments, experiments_by_category


@flask_app.route("/labs.html")
def labs():
    """
    Renders the Laboratories List.
    """

    # To properly render the labs list we need access to the configuration.js file (this will change in the
    # future). We actually request this to ourselves.
    config = _retrieve_configuration_js()
    config = json.loads(config)

    # We also want access to the experiment's list for the user.
    sessionid = request.cookies.get("sessionid", None)
    if sessionid is None:
        flash("You are not logged in", category="error")
        return redirect(url_for("index"))
    weblabweb = WeblabWeb()
    weblabweb.set_target_urls(flask_app.config["LOGIN_URL"], flask_app.config["CORE_URL"])

    weblabweb._feed_cookies(request.cookies)

    experiments_list = weblabweb._list_experiments(sessionid)
    # TODO: There could be issues with the routing.


    # Merge the data for the available experiments.
    experiments, experiments_by_category = build_experiments_list(experiments_list, config)

    # Store the list in a global.
    # TODO: This should eventually be changed, it won't work in all setups and will have thread issues.
    if G.get("sessiondata") is None:
        G["sessiondata"] = {}
    G["sessiondata"][sessionid] = experiments

    return render_template("labs.html", experiments = experiments, experiments_by_category = experiments_by_category, urllib = urllib)