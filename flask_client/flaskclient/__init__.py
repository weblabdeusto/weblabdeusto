from flask import render_template
from flaskclient.flask_app_builder import build_flask_app

flask_app = build_flask_app()
flask_app.config.from_pyfile("../config.py")

# Import the different flask_views. This needs to be exactly here because
# otherwise the @flask_app notation wouldn't work.
import view_index


@flask_app.route("/labs.html")
def labs():
    return render_template("labs.html")


@flask_app.route("/lab.html")
def lab():
    return render_template("lab.html")


@flask_app.route("/contact.html")
def contact():
    return render_template("contact.html")
