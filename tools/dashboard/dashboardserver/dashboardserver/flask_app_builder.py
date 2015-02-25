from flask import Flask


def build_flask_app():
    flask_app = Flask(__name__)
    flask_app.config["DEBUG"] = True
    flask_app.config["SECRET_KEY"] = "SECRET"
    return flask_app