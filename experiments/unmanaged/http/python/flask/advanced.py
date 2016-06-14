from flask import Flask, session, url_for
from flask_debugtoolbar import DebugToolbarExtension
from weblablib import WebLab, requires_login, current_user, poll

app = Flask(__name__)

# TODO: Change these settings
app.config['SECRET_KEY'] = 'something random'
app.config['WEBLAB_USERNAME'] = 'admin'
app.config['WEBLAB_PASSWORD'] = 'password'
app.config['WEBLAB_SESSION_ID_NAME'] = 'lab_session_id'
app.config['SESSION_COOKIE_NAME'] = 'advanced_lab'
app.config['SESSION_COOKIE_PATH'] = '/lab'

# Other variables you might want to change
# app.config['WEBLAB_REDIS_URL'] = 'redis://localhost:6379/0' # default value
# app.config['WEBLAB_TIMEOUT'] = 15 # in seconds, default value
# app.config['WEBLAB_SCHEME'] = 'https'

weblab = WebLab(app, url='/foo', public_url='/lab/public')
toolbar = DebugToolbarExtension(app)

@weblab.initial_url
def initial_url():
    return url_for('.lab')

@weblab.on_start
def on_start(client_data, server_data):
    print("New user!")
    print(client_data)
    print(server_data)

@weblab.on_dispose
def on_stop():
    print("User expired. Here you should clean resources")

@app.route('/lab/')
@requires_login()
def lab():
    user = current_user()
    return "Hello %s. You didn't poll in %.2f seconds (timeout configured to %s). Total time left: %s" % (user.username, user.time_without_polling, weblab.timeout, user.time_left)

@app.route("/")
def index():
    return "<html><head></head><body></body></html>"


if __name__ == '__main__':
    app.run(debug=True, host = '0.0.0.0', threaded=True)

