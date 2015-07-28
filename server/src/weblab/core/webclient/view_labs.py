from __future__ import print_function, unicode_literals
import urllib

from flask import render_template, url_for, request, flash, redirect

from weblab.core.webclient.helpers import _get_loggedin_info, _get_experiment_info
from weblab.core.wl import weblab_api
from weblab.core.exc import SessionNotFoundError
from weblab.core.webclient import login_required


@weblab_api.route_webclient("/")
@login_required
def labs():
    """
    Renders the Laboratories List.
    """
    experiments_raw = weblab_api.api.list_experiments()
    experiments, experiments_by_category = _get_experiment_info(experiments_raw)
    loggedin_info = _get_loggedin_info()

    return render_template("webclient/labs.html", experiments=experiments,
                           experiments_by_category=experiments_by_category,
                           urllib=urllib, loggedin=loggedin_info)






