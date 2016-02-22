from __future__ import print_function, unicode_literals
import os
from flask import render_template, url_for, request, flash, redirect, session, g

from weblab.core.i18n import gettext, get_locale
from weblab.core.exc import SessionNotFoundError
from weblab.core.webclient.view_login import demo
from weblab.core.webclient.helpers import _get_experiment, _get_experiment_data, _hook_native_experiments
from weblab.core.wl import weblab_api
from weblab.core.webclient import login_required
from weblab.core.reservations import Reservation

# TODO: make sure we have a special 500 error handler, which simply calls error but also calls the send_mail function

@weblab_api.route_webclient("/labs/<category_name>/<experiment_name>/")
def lab(category_name, experiment_name):
    """
    Renders a specific laboratory.
    """
    federated_reservation_id = session.get('reservation_id')
    federated_mode = federated_reservation_id is not None
    if federated_mode:
        back_url = session.get('back_url')
    else:
        back_url = None

    experiment = None
    if federated_mode:
        weblab_api.ctx.reservation_id = federated_reservation_id
        # Now obtain the current experiment
        try:
            experiment = _get_experiment_data(weblab_api.api.get_reservation_experiment_info())
            reservation_status = weblab_api.api.get_reservation_status()
        except SessionNotFoundError:
            session.pop('reservation_id', None)
            session.pop('back_url', None)
            federated_mode = False

            # Check if the user has a valid session (it may happen that this comes from an old reservation_id)
            try:
                experiment_list = weblab_api.api.list_experiments(experiment_name, category_name)
            except SessionNotFoundError:
                return render_template("webclient/error.html", error_message = gettext("The reservation you used has expired."), federated_mode = True, back_url = back_url)
        else:
            if experiment is not None and reservation_status is not None and experiment['type'] == 'redirect':
                if reservation_status.status == Reservation.CONFIRMED:
                    local_url = reservation_status.url
                    if local_url is not None:
                        return redirect(local_url.replace("TIME_REMAINING", unicode(local_url.time)))

    if experiment is None:
        try:
            experiment_list = weblab_api.api.list_experiments(experiment_name, category_name)
        except SessionNotFoundError:
            flash(gettext("You are not logged in"), 'danger')
            return redirect(url_for('.login', next=request.url))

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

    return render_template("webclient/lab.html", experiment=experiment, federated_mode = federated_mode, back_url = back_url, federated_reservation_id = federated_reservation_id)

@weblab_api.route_webclient("/demos/labs/<category_name>/<experiment_name>/")
def demo_lab(category_name, experiment_name):
    try:
        experiment_list = weblab_api.api.list_experiments(experiment_name, category_name)
    except SessionNotFoundError:
        g.next_url = url_for('.lab', category_name = category_name, experiment_name = experiment_name)
        return demo()
    except:
        flash(gettext("Error processing request"), 'danger')
        return redirect(url_for('.labs'))
    else: # User is logged in and has permissions
        return redirect(url_for('.lab', category_name = category_name, experiment_name = experiment_name))


@weblab_api.route_webclient('/demos/')
def demos_index():
    return redirect(url_for('.demo'))

@weblab_api.route_webclient('/demos/labs/')
def demos_index_labs():
    return redirect(url_for('.demo'))

@weblab_api.route_webclient('/demos/labs/<category_name>/')
def demos_index_labs_category(category_name):
    return redirect(url_for('.demo'))


@weblab_api.route_webclient("/labs/<category_name>/<experiment_name>/config.json")
def lab_config(category_name, experiment_name):
    experiment_config = {}
    try:
        experiment = weblab_api.db.get_experiment(experiment_name, category_name)
    except Exception as ex:
        pass
    else:
        if experiment is not None:
            _hook_native_experiments(experiment)
            experiment_config = experiment.client.configuration

    scripts = [
        url_for('.static', filename='js/iframeResizer.contentWindow.min.js', _external=True)
    ]
    locale = get_locale().language
    return weblab_api.jsonify(locale=locale, targetURL=url_for('json.service_url'), fileUploadURL=url_for('core_web.upload'), scripts=scripts, config=experiment_config, currentURL = weblab_api.core_server_url)


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
