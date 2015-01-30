import logging

from flask import render_template, url_for, request, flash, redirect

from weblab.webclient.web.flask_app import flask_app
from weblab.webclient.web.helpers import get_experiments_data
from weblab.webclient.web.weblabweb import WeblabWeb, WeblabWebException


@flask_app.route("/lab.html")
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

        sessionid = request.cookies.get("sessionid", None)
        if sessionid is None:
            flash("You are not logged in", category="error")
            next = request.full_path
            return redirect(url_for("index", next=next))

        # Check if the session is valid (check if we are still logged in).
        logging.debug("Checking if we are still logged in")
        weblabweb = WeblabWeb()
        route = request.cookies.get("route", "")
        weblabweb.set_target_urls(flask_app.config["LOGIN_URL"], flask_app.config["CORE_URL"])
        weblabweb._feed_cookies(request.cookies)
        weblabweb._feed_cookies({"weblabsessionid": "%s.%s" % (sessionid, route)})
        user_info = weblabweb._get_user_information(sessionid)

        # Retrieves experiment data.
        # TODO: This is extremely inefficient but it will be possible to remove it eventually.
        experiments, experiments_by_category = get_experiments_data(sessionid, route)

        experiment = {
            "name": name,
            "category": category
        }

        experiment = experiments["%s@%s" % (name, category)]

        return render_template("lab.html", experiment=experiment, experiment_type = type)

    except WeblabWebException as ex:
        # Our session is no longer valid. Go login again.
        if ex.args[0]["code"] == "JSON:Client.SessionNotFound":
            next = request.full_path
            return redirect(url_for("index", next=next))
        else:
            return "500 WeblabWeb Exception was raised", 500

