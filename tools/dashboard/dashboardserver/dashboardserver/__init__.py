from flask import jsonify
import flask_app_builder
from flask.ext import restful

flask_app = flask_app_builder.build_flask_app()
api = restful.Api(flask_app)


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
            "date": "2015-02-23"
        }
    }

    return jsonify(data)
