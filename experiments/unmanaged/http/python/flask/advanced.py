from flask import Flask, session, url_for
from flask_debugtoolbar import DebugToolbarExtension
from weblablib import WebLab

app = Flask(__name__)

# TODO: Change these settings
app.config['SECRET_KEY'] = 'something random'
app.config['WEBLAB_USERNAME'] = 'admin'
app.config['WEBLAB_PASSWORD'] = 'password'


weblab = WebLab(app, url='/foo', public_url='/lab/public')
toolbar = DebugToolbarExtension(app)

@weblab.initial_url
def initial_url():
    return url_for('.lab')

@app.route('/lab/')
def lab():
    return ":-)"

@app.route("/")
def index():
    return "<html><head></head><body></body></html>"


if __name__ == '__main__':
    app.run(debug=True, host = '0.0.0.0')
