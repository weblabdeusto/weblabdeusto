from flask import Flask
from flask import escape


def build_flask_app():
    flask_app = Flask(__name__, static_folder="../../dashboardapp/dist", static_url_path="/app")

    # The following settings will likely be overriden.
    flask_app.config["DEBUG"] = False
    flask_app.config["SECRET_KEY"] = "SECRET"

    flask_app.config.from_pyfile("../config.py")

    # Mostly for debugging purposes, this snippet will print the site-map so that we can check
    # which methods we are routing.
    @flask_app.route("/site-map")
    def site_map():
        lines = []
        for rule in flask_app.url_map.iter_rules():
            line = str(escape(repr(rule)))
            lines.append(line)

        ret = "<br>".join(lines)
        return ret

    return flask_app