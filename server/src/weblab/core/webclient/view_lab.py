from __future__ import print_function, unicode_literals
import os
from flask import render_template, url_for, request, flash, redirect

from weblab.core.babel import gettext
from weblab.core.exc import SessionNotFoundError
from weblab.core.webclient.helpers import _get_experiment
from weblab.core.wl import weblab_api
from weblab.core.webclient import login_required


@weblab_api.route_webclient("/labs/<category_name>/<experiment_name>/")
@login_required
def lab(category_name, experiment_name):
    """
    Renders a specific laboratory.
    """
    try:
        experiment_list = weblab_api.api.list_experiments(experiment_name, category_name)

        experiment = None
        for exp_allowed in experiment_list:
            if exp_allowed.experiment.name == experiment_name and exp_allowed.experiment.category.name == category_name:
                experiment = _get_experiment(exp_allowed)

        if experiment is None:
            # TODO: check what to do in case there is no session_id (e.g., federated mode)
            if weblab_api.db.check_experiment_exists(experiment_name, category_name):
                flash(gettext("You don't have permission on this laboratory"), 'danger')
            else:
                flash(gettext("Experiment does not exist"), 'danger')
            return redirect(url_for('.labs'))

        # Get the target URL for the JS API.
        lab_url = url_for(".static", filename="")

        return render_template("webclient/lab.html", experiment=experiment, lab_url=lab_url)
    except Exception as ex:
        raise

