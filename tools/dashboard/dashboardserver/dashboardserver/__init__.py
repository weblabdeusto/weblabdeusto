
import flask_app_builder


flask_app = flask_app_builder.build_flask_app()





@flask_app.route("/")
def index():
    return "Welcome to the DashBoard server"