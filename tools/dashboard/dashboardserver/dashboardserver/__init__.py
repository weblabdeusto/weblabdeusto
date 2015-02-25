from flask import jsonify
import flask_app_builder
from flask.ext import restful

flask_app = flask_app_builder.build_flask_app()
api = restful.Api(flask_app)

import checks


@flask_app.route("/")
def index():
    return "Welcome to the DashBoard server"



@flask_app.route("/status")
def status():
    data = {}
    data["archimedes"] = {
        "webcamtest1" : {
            "text": "First webcam is working",
            "status": "OK",
            "date": "2015-02-23",
            "task_state": "finished"
        }
    }

    # Retrieve the full list of active checks in the REDIS instance.
    check_ids = set([check_id.split(':')[2] for check_id in checks.r.keys("dashboard:checks:*.*:")])

    for check_id in check_ids:
        check_data = checks.read_check(check_id)
        component, id = check_id.split('.', 1)
        data["component"] = {
            id: {
                "text": check_data["msg"],
                "status": check_data["result"],
                "date": check_data["finished_date"],
                "task_state": check_data["task_state"]
            }
        }

    return jsonify(data)
