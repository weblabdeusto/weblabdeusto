from __future__ import print_function, unicode_literals

from flask import request, render_template

from weblab.core.wl import weblab_api

@weblab_api.route_webclient('/visir.html')
def visir():
    return render_template("webclient/visir.html")
