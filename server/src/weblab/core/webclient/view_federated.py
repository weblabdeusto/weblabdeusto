from __future__ import print_function, unicode_literals

from flask import render_template, request, flash, redirect, url_for, jsonify, session

from weblab.core.wl import weblab_api

# ../../client/index.html%(localization)s#exp.name=%(exp_name)s&exp.category=%(exp_cat)s&reservation_id=%(reservation_id)s&header.visible=false&back_url=%(back_url)s&widget=%(widget)s

@weblab_api.route_webclient('/federated/<category_name>/<experiment_name>/')
def federated(category_name, experiment_name):
    url = request.args.get('back_url')
    widget = request.args.get('widget')
    session['reservation_id'] = request.args.get('reservation_id')
    return redirect(url_for('.lab', experiment_name=experiment_name, category_name=category_name))

