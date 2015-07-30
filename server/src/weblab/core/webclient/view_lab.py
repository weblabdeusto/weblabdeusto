from __future__ import print_function, unicode_literals
import os
from flask import render_template, url_for, request, flash, redirect

from weblab.core.babel import gettext
from weblab.core.exc import SessionNotFoundError
from weblab.core.webclient.helpers import _get_gravatar_url, _get_experiment
from weblab.core.wl import weblab_api
from weblab.core.webclient import login_required


@weblab_api.route_webclient("/labs/<category_name>/<experiment_name>/")
@login_required
def lab(category_name, experiment_name):
    """
    Renders a specific laboratory.
    """
    try:
        # TODO: review, probably not necessary
        sessionid = request.cookies.get("weblabsessionid")
        weblab_api.ctx.reservation_id = sessionid

        # TODO: Remove me whenever we implement gravatar properly
        weblab_api.ctx.gravatar_url = _get_gravatar_url()

        experiment_list = weblab_api.api.list_experiments()

        experiment = None
        for exp_allowed in experiment_list:
            if exp_allowed.experiment.name == experiment_name and exp_allowed.experiment.category.name == category_name:
                experiment = _get_experiment(exp_allowed)

        if experiment is None:
            # TODO: check what to do in case there is no session_id (e.g., federated mode)
            flash(gettext("You don't have permission on this laboratory"), 'danger')
            return redirect(url_for('.labs'))

        type = experiment['type']

        # Get the target URL for the JS API.
        # Note: The following commented line should work best; but it doesn't make sure that the protocol matches.
        # core_server_url = weblab_api.server_instance.core_server_url
        core_server_url = os.path.join(*[url_for(".login"), "../../"])
        json_url = os.path.join(*[core_server_url, "json/"])
        # Old URL: lab_url = os.path.join(*[core_server_url, "client", "weblabclientlab/"])
        lab_url = os.path.join(url_for(".static", filename=""))

        return render_template("webclient/lab.html", display_name=experiment_name, experiment=experiment, json_url=json_url, lab_url=lab_url)
    except Exception as ex:
        raise

