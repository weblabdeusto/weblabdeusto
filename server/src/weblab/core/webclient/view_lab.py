from __future__ import print_function, unicode_literals
import os
from flask import render_template, url_for, request, flash, redirect, session

from weblab.core.babel import gettext
from weblab.core.exc import SessionNotFoundError
from weblab.core.webclient.helpers import _get_experiment, _get_experiment_data
from weblab.core.wl import weblab_api
from weblab.core.webclient import login_required


@weblab_api.route_webclient("/labs/<category_name>/<experiment_name>/")
def lab(category_name, experiment_name):
    """
    Renders a specific laboratory.
    """
    federated_reservation_id = session.pop('reservation_id', None)
    federated_mode = federated_reservation_id is not None
    if federated_mode:
        back_url = session.pop('back_url', None)
    else:
        back_url = None

    try:
        experiment = None
        if federated_mode:
            weblab_api.ctx.reservation_id = federated_reservation_id
            # Now obtain the current experiment
            experiment = _get_experiment_data(weblab_api.api.get_reservation_experiment_info())
        else:
            experiment_list = weblab_api.api.list_experiments(experiment_name, category_name)
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

        return render_template("webclient/lab.html", experiment=experiment, federated_mode = federated_mode, back_url = back_url)
    except Exception as ex:
        raise

@weblab_api.route_webclient("/labs/<category_name>/<experiment_name>/config.json")
@login_required
def lab_config(category_name, experiment_name):
    experiment_config = {}
    try:
        experiment_list = weblab_api.api.list_experiments(experiment_name, category_name)


        for exp_allowed in experiment_list:
            if exp_allowed.experiment.name == experiment_name and exp_allowed.experiment.category.name == category_name:
                experiment_config = exp_allowed.experiment.client.configuration

    except Exception as ex:
        experiment_config = {}

    scripts = [
        url_for('.static', filename='js/iframeResizer.contentWindow.min.js', _external=True)
    ]
    return weblab_api.jsonify(targetURL=url_for('json.service_url'), scripts=scripts, config=experiment_config, currentURL = weblab_api.core_server_url)


@weblab_api.route_webclient("/labs/<category_name>/<experiment_name>/latest_uses.json")
@login_required
def latest_uses(category_name, experiment_name):
    uses = []
    for use in weblab_api.api.get_latest_uses_per_lab(category_name, experiment_name):
        current_use = {
            'start_date' : use['start_date'].strftime('%Y-%m-%d %H:%M:%SZ'),
            'link' : url_for('accesses.detail', id=use['id'])
        }
        if use['country']:
            current_use['location'] = '{0} ({1})'.format(use['country'], use['origin'])
        else:
            current_use['location'] = use['origin']

        uses.append(current_use)

    return weblab_api.jsonify(uses=uses[::-1])

@weblab_api.route_webclient("/labs/<category_name>/<experiment_name>/stats.json")
@login_required
def lab_stats(category_name, experiment_name):
    experiment_found = False
    try:
        experiment_list = weblab_api.api.list_experiments(experiment_name, category_name)


        for exp_allowed in experiment_list:
            if exp_allowed.experiment.name == experiment_name and exp_allowed.experiment.category.name == category_name:
                experiment_found = True

    except Exception as ex:
        return {}

    if not experiment_found:
        return {}

    stats = weblab_api.db.get_experiment_stats(experiment_name, category_name)
    stats['status'] = 'online';
    return weblab_api.jsonify(stats=stats)
