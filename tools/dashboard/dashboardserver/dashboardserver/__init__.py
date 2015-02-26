from collections import defaultdict
from flask import jsonify
from flask.ext.cors import cross_origin
import flask_app_builder
from flask.ext import restful

flask_app = flask_app_builder.build_flask_app()
api = restful.Api(flask_app)

import checks

@flask_app.route("/")
def index():
    return "Welcome to the DashBoard server"


# @flask_app.route("/app/<path:file>")
# def app(file):
#     return ""



@flask_app.route("/status")
@cross_origin()
def status():
    data = defaultdict(dict)
    # data["archimedes"] = {
    #     "webcamtest1" : {
    #         "text": "First webcam is working",
    #         "status": "OK",
    #         "date": "2015-02-23",
    #         "task_state": "finished"
    #     }
    # }

    # Retrieve the full list of active checks in the REDIS instance.
    check_ids = set([check_id.split(':')[2] for check_id in checks.r.keys("dashboard:checks:*.*:*")])

    for check_id in check_ids:
        check_data = checks.read_check(check_id)
        component_id, element_id = check_id.split('.', 1)
        data[component_id][element_id] = {
                "text": check_data["msg"],
                "status": check_data["result"],
                "date": check_data["finished_date"],
                "task_state": check_data["task_state"]
        }

    return jsonify(data)
