from __future__ import print_function, unicode_literals

from werkzeug.utils import secure_filename
from flask import request, render_template, current_app

from weblab.core.wl import weblab_api

@weblab_api.route_webclient('/visir.html')
def visir():
    return render_template("webclient/visir.html")

@weblab_api.route_webclient('/fonts/<path:path>')
def fonts(path):
    blueprint = current_app.blueprints['core_webclient']
    return blueprint.send_static_file("gen/fonts/{}".format(secure_filename(path)))
