import urllib

from flask import render_template, url_for, request, flash, redirect

from weblab.core.webclient.web.helpers import _get_loggedin_info, _get_experiment_info
from weblab.core.wl import weblab_api
from weblab.core.exc import SessionNotFoundError


@weblab_api.route_webclient("/labs.html")
def labs():
    """
    Renders the Laboratories List.
    """
    try:
        # We also want access to the experiment's list for the user.
        # TODO: Take into account the somewhat unclear difference between the loginweblabsessionid and the other one.
        cookie = request.cookies.get("weblabsessionid", None)
        if cookie is None:
            flash("You are not logged in", category="error")
            # _ext + _scheme is a workaround around an http(s) issue.
            return redirect(url_for(".index", _external=True, _scheme=request.scheme))

        # Prepare to call the weblab_api
        weblab_api.ctx.reservation_id = cookie
        experiments_raw = weblab_api.api.list_experiments()

        experiments, experiments_by_category = _get_experiment_info(experiments_raw)
        loggedin_info = _get_loggedin_info()
    except SessionNotFoundError as ex:
        flash("You are not logged in", category="error")
        next = request.full_path
        return redirect(url_for(".index", _external=True, _scheme=request.scheme, next=next))

    return render_template("webclient_web/labs.html", experiments=experiments,
                           experiments_by_category=experiments_by_category,
                           urllib=urllib, loggedin=loggedin_info)






