# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import os
import sys
import time
import random
import hashlib
import threading

import six
import requests

from flask import Flask, Response, stream_with_context, abort, send_file, redirect, request, escape

PROXY_SESSION   = 'proxy-sessions:'
REDIRECT        = 'redirect:'
FILE            = 'file:'

PROTOCOLS = FILE, PROXY_SESSION, REDIRECT
QUIET = False

def _validate_protocols(paths):
    """Check that the paths are valid, and that the order is not hiding some results"""
    for _, processor in paths:
        if not processor.startswith(PROTOCOLS):
            raise ValueError("Invalid protocol in paths: %s " % processor)

    previous_paths = []
    for pos, (_path, _) in enumerate(paths):

        if '$' in _path and (_path.count('$') > 1 or not _path.endswith('$')):
            print("The $ char is a special character meaning the end of the path. It can appear only once and at the end. Expect errors with %s!" % _path, file=sys.stderr)

        for _previous_path in previous_paths:
            if _path.startswith(_previous_path.replace('$','')):
                if '$' in _previous_path and _path != _previous_path:
                    # This previous_path has a $ and it is not the same as _path, so forget it
                    continue
                print("ProxyHandler: Path %s (number %s) will not be managed since a previous one manages %s!" % (_path, pos, _previous_path), file=sys.stderr)
                break
        previous_paths.append(_path)
    return previous_paths

def _generate_file(current_path, value):
    where = value.split(':', 1)[1]

    if '..' in current_path:
        return abort(404)

    if current_path.startswith('/'):
        current_path = current_path[1:]
    fname = os.path.join(where, current_path)
    if os.path.exists(fname):
        if os.path.isdir(fname):
            return abort(403)
        else:
            return send_file(fname, as_attachment = False, conditional = True)
    else:
        return abort(404)

def _generate_redirect(current_path, value):
    where = value.split(':', 1)[1]
    return redirect(where)

def _generate_proxy(current_path, value):
    where = value.split(':', 1)[1]
    cookie_name, routes = where.split(':', 1)
    routes = dict([ route.strip().split('=', 1) for route in routes.split(',') if route.strip() ])

    # cookie_name = 'weblabsessionid'
    # routes = {
    #    'route1' : 'http://localhost:10000/weblab/json/',
    #    'route2' : 'http://localhost:10001/weblab/json/',
    #    'route3' : 'http://localhost:10002/weblab/json/',
    # }

    current_cookie_value = request.cookies.get(cookie_name, '')

    chosen_url = None
    for route in routes:
        if current_cookie_value.endswith(route):
            chosen_url = routes[route]
            break

    if chosen_url is None:
        chosen_url = random.choice(list(routes.values()))

    headers = dict(request.headers)
    headers['X-Forwarded-For'] = request.remote_addr
    headers['X-Forwarded-Host'] = request.host
    headers.pop('Host', None)
    headers.pop('host', None)

    kwargs = dict(headers = headers, cookies = dict(request.cookies), allow_redirects=False)

    if request.method == 'GET':
        method = requests.get
    elif request.method == 'POST':
        kwargs['data'] = request.data

        if request.files:
            kwargs['files'] = {}
            for f, f_contents in six.iteritems(request.files):
                kwargs['files'][f] = [f_contents.filename, f_contents.stream, f_contents.content_type, f_contents.headers]

        if request.form:
            headers.pop('Content-Type', None)
            kwargs['data'] = request.form

        method = requests.post
    else:
        raise Exception("Method not supported")

    MAX_RETRIES = 5
    retry = 0
    full_url = chosen_url + current_path
    if request.args:
        full_url += '?' + '&'.join([ '%s=%s' % (key, requests.utils.quote(value, '')) for key, value in request.args.items() ])

    while True:
        try:
            req = method(full_url, **kwargs)
            break
        except requests.ConnectionError:
            if request.method != 'GET':
                raise
            retry += 1
            if retry >= MAX_RETRIES:
                raise
            time.sleep(0.5)
    
    response_kwargs = {
        'headers' : dict(req.headers),
        'status' : req.status_code,
    }
    if 'content-type' in req.headers:
        response_kwargs['content_type'] = req.headers['content-type']

    return Response(req.content, **response_kwargs)


def generate_proxy_handler(paths):
    _validate_protocols(paths)

    app = Flask(__name__)

    @app.route('/')
    @app.route('/<path:url>', methods = ['GET', 'POST'])
    def index(url = ''):
        url = '/' + url
        current_path = None
        current_value = None
        selected_path = None

        for path, value in paths:
            if path.endswith('$'):
                if url == path[:-1] or url == path[:-1] + '/':
                    selected_path = path
                    current_path = path[:-1]
                    current_value = value
                    break
            else:
                if url.startswith(path):
                    selected_path = path
                    current_path = url[len(path):]
                    current_value = value
                    break

        if current_path is None:
            return abort(404)
        
        if value.startswith(FILE):
            return _generate_file(current_path, value)
        elif value.startswith(REDIRECT):
            return _generate_redirect(current_path, value)
        elif value.startswith(PROXY_SESSION):
            return _generate_proxy(current_path, value)

    return app

DEBUG = False

def start(port, paths, host = '0.0.0.0'):
    app = generate_proxy_handler(paths)
    t = threading.Thread(target=app.run, kwargs = dict(port = port, threaded = True, debug = DEBUG, use_reloader = False, host = host))
    t.setName('proxy-server:%s' % port)
    t.setDaemon(True)
    t.start()

if __name__ == '__main__':
    paths = [
        ('/foo', 'proxy-sessions:weblabsessionid:route1=http://weblab.deusto.es'),
        ('/client', 'file:/var/www/'),
        ('/client/foo', 'redirect:/foo'),
    ]
    start(8000, paths)
    raw_input('Listening in port 8000, press Enter to finish...')

