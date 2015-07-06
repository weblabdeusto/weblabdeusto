# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import os
import sys
import random
import hashlib
import threading

import six
import requests

from flask import Flask, Response, stream_with_context, abort, send_file, redirect, request, escape
from werkzeug.routing import Rule

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

def _add_rules(app, current_path, value):
    hash_value = hashlib.new("md5", value).hexdigest()
    # If it ends in <path:url>, use also without it
    app.url_map.add(Rule(current_path, endpoint=hash_value))
    if '<path' in current_path:
        app.url_map.add(Rule(current_path.split('<')[0], endpoint=hash_value))
        if '/<' not in current_path:
            app.url_map.add(Rule(current_path.replace('<','/<'), endpoint=hash_value))
    return hash_value

def _generate_file(app, current_path, value):
    """
    FILE
    
    Example: { '/foo' : 'file:/var/www/' }
    
    If  /foo/index.html => returns /var/www/index.html
    """
    where = value.split(':', 1)[1]
    endpoint = _add_rules(app, current_path, value)

    @app.endpoint(endpoint)
    def handle_file(url = None):
        if '..' in url:
            abort(404)
        fname = os.path.join(where, url)
        if os.path.exists(fname):
            return send_file(fname, as_attachment = False, conditional = True)
        else:
            return abort(404)

def _generate_redirect(app, current_path, value):
    """
    REDIRECT
    
    Example: { '/foo' : 'redirect:http://www.google.com' }
    
    If /foo => redirect to http://www.google.com
    """
    where = value.split(':', 1)[1]
    endpoint = _add_rules(app, current_path, value)

    @app.endpoint(endpoint)
    def handle_file(url = None):
        return redirect(where)

def _generate_proxy(app, current_path, value):
    """ 
    PROXY_SESSION
    
    Example: { u'/weblab/json/', u'proxy-sessions:weblabsessionid:route1=http://localhost:10000/weblab/json/,route2=http://localhost:10001/weblab/json/,route3=http://localhost:10002/weblab/json/,' }
    
    If /weblab/json/
       if route1 present in weblabsessionid, proxy to http://localhost:10000/weblab/json/
       if route2 present in weblabsessionid, proxy to http://localhost:10001/weblab/json/
       if route3 present in weblabsessionid, proxy to http://localhost:10002/weblab/json/
       else, randomly to any of them.
    """
    
    endpoint = _add_rules(app, current_path, value)

    where = value.split(':', 1)[1]
    cookie_name, routes = where.split(':', 1)
    routes = dict([ route.strip().split('=', 1) for route in routes.split(',') if route.strip() ])

    # cookie_name = 'weblabsessionid'
    # routes = {
    #    'route1' : 'http://localhost:10000/weblab/json/',
    #    'route2' : 'http://localhost:10001/weblab/json/',
    #    'route3' : 'http://localhost:10002/weblab/json/',
    # }

    routes_list = list(routes.values())

    @app.endpoint(endpoint)
    def handle_proxy(url = None):
        current_cookie_value = request.cookies.get(cookie_name, '')

        where = None
        for route in routes:
            if current_cookie_value.endswith(route):
                where = routes[route]
                break

        if where is None:
            where = random.choice(routes_list)

        headers = dict(request.headers)
        headers['X-Forwarded-For'] = request.remote_addr
        headers.pop('Host', None)
        headers.pop('host', None)
        if request.method == 'GET':
            req = requests.get(where + (url or ''), headers = headers, cookies = dict(request.cookies))
        elif request.method == 'POST':
            req = requests.post(where + (url or ''),  data = request.data, headers = headers, cookies = dict(request.cookies))

        return Response(req.content, headers = dict(req.headers), content_type = req.headers['content-type'])


def generate_proxy_handler(paths):
    _validate_protocols(paths)

    app = Flask(__name__)

    for path, value in paths:
        # $ is supported, otherwise anything after will be considered url
        if path.endswith('$'):
            current_path = path[:-1]
            if current_path == '':
                current_path = '/'
        else:
            if path == '':
                current_path = '/<path:url>'
                continue #TODO
            else:
                current_path = path + '<path:url>'
            if current_path == '/weblab/<path:url>':
                continue
                

        if value.startswith(FILE):
            _generate_file(app, current_path, value)
        elif value.startswith(REDIRECT):
            _generate_redirect(app, current_path, value)
        elif value.startswith(PROXY_SESSION):
            _generate_proxy(app, current_path, value)
        else:
            print("Unknown starting path: %s" % value)

    if DEBUG:
        @app.route("/site-map")
        def site_map():
            lines = []
            for rule in app.url_map.iter_rules():
                line = str(escape(repr(rule)))
                lines.append(line)

            ret = "<br>".join(lines)
            return ret
    return app

DEBUG = True # TODO

def start(port, paths):
    app = generate_proxy_handler(paths)
    t = threading.Thread(target=app.run, kwargs = dict(port = port, threaded = True, debug = DEBUG, use_reloader = False))
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

