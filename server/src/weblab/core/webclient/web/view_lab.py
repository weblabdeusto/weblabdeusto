import os
from flask import render_template, url_for, request, flash, redirect

from weblab.core.exc import SessionNotFoundError
from weblab.core.webclient.web.helpers import _get_loggedin_info, _get_experiment_info
from weblab.core.wl import weblab_api


@weblab_api.route_webclient("/lab.html")
def lab():
    """
    Renders a specific laboratory.
    """

    try:
        name = request.values.get("name")
        category = request.values.get("category")
        type = request.values.get("type")

        if name is None or category is None or type is None:
            return "500 Please specify a name and category", 500

        sessionid = request.cookies.get("weblabsessionid")

        weblab_api.ctx.reservation_id = sessionid

        # Retrieve the loggedin information.
        loggedin_info = _get_loggedin_info()

        experiments_raw = weblab_api.api.list_experiments()
        experiments, experiments_by_category = _get_experiment_info(experiments_raw)

        experiment = experiments[name]

        # Get the target URL for the JS API.
        # Note: The following commented line should work best; but it doesn't make sure that the protocol matches.
        # core_server_url = weblab_api.server_instance.core_server_url
        core_server_url = os.path.join(*[url_for(".index"), "../../"])
        json_url = os.path.join(*[core_server_url, "json/"])
        # Old URL: lab_url = os.path.join(*[core_server_url, "client", "weblabclientlab/"])
        lab_url = os.path.join(url_for(".static", filename=""))

        return render_template("webclient_web/lab.html", experiment=experiment, loggedin=loggedin_info, json_url=json_url, lab_url=lab_url)

    except SessionNotFoundError as ex:
        flash("You are not logged in", category="error")
        next = request.full_path
        return redirect(url_for(".index", next=next))
    except Exception as ex:
        raise ex

