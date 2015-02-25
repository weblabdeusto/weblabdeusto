from flask import Flask


def build_flask_app():
    flask_app = Flask(__name__)

    # The following settings will likely be overriden.
    flask_app.config["DEBUG"] = False
    flask_app.config["SECRET_KEY"] = "SECRET"

    flask_app.config.from_pyfile("config")

    return flask_app