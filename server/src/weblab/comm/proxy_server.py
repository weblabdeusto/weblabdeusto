#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2012 onwards University of Deusto
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#
# This software consists of contributions made by many individuals,
# listed below:
#
# Author: Pablo Orduña <pablo@ordunya.com>
#

import sys
import os
from six.moves import socketserver
from six.moves import BaseHTTPServer
import shutil
import urllib2
import mimetypes
import threading

PROXY           = 'proxy:'
PROXIES         = 'proxies:'
PROXY_SESSION   = 'proxy-sessions:'
REDIRECT        = 'redirect:'
FILE            = 'file:'

PROTOCOLS = PROXY, FILE, PROXY_SESSION, PROXIES, REDIRECT
QUIET = False

def generate_proxy_handler(paths):

    for _, processor in paths:
        if not processor.startswith(PROTOCOLS):
            raise ValueError("Invalid protocol in paths: %s " % processor)

    previous_paths = []
    for pos, (_path, _) in enumerate(paths):

        if '$' in _path and (_path.count('$') > 1 or not _path.endswith('$')):
            print >> sys.stderr, "The $ char is a special character meaning the end of the path. It can appear only once and at the end. Expect errors with %s!" % _path

        for _previous_path in previous_paths:
            if _path.startswith(_previous_path.replace('$','')):
                if '$' in _previous_path and _path != _previous_path:
                    # This previous_path has a $ and it is not the same as _path, so forget it
                    continue
                print >> sys.stderr, "ProxyHandler: Path %s (number %s) will not be managed since a previous one manages %s!" % (_path, pos, _previous_path)
                break
        previous_paths.append(_path)

    class AvoidHTTPRedirectHandler(urllib2.HTTPRedirectHandler):
        """ Do not follow any redirection """
        def http_error_302(self, req, fp, code, msg, headers):
            raise urllib2.HTTPError(req.get_full_url(), code, msg, headers, fp)

        http_error_301 = http_error_303 = http_error_307 = http_error_302

    class ProxyHandler(BaseHTTPServer.BaseHTTPRequestHandler):

        if not mimetypes.inited:
            mimetypes.init() # try to read system mime.types
        extensions_map = mimetypes.types_map.copy()

        proxies_count      = 0
        proxies_count_lock = threading.Lock()

        def do_GET(self):
            try:
                f = self.send_head()
                if f:
                    shutil.copyfileobj(f, self.wfile)
                    f.close()
            except:
                self.log_error('Error processing %s' % self.path)
                raise

        def log_message(self, *args, **kwargs):
            if not QUIET:
                BaseHTTPServer.BaseHTTPRequestHandler.log_message(self, *args, **kwargs)

        def do_POST(self):
            try:
                length = int(self.headers['content-length'])
                f = self.send_head(self.rfile.read(length))
                if f:
                    shutil.copyfileobj(f, self.wfile)
                    f.close()
            except:
                self.log_error('Error processing %s' % self.path)
                raise

        def do_HEAD(self):
            self.send_head()

        def send_head(self, data = None):
            for path, processor in paths:
                if self.path.startswith(path.replace('$','')):
                    if path.endswith('$') and self.path != path.replace('$',''):
                        continue
                    if path.replace('$','') == '':
                        path = self.path
                    else:
                        path = self.path.split(path.replace('$',''), 1)[1]
                    if processor.startswith(FILE):
                        base_path = processor.split(FILE, 1)[1]
                        return self.send_head_file(data, path, base_path)
                    elif processor.startswith(PROXY):
                        proxy = processor.split(PROXY, 1)[1]
                        return self.send_head_proxy(data, path, proxy)
                    elif processor.startswith(PROXIES):
                        proxies_str = processor.split(PROXIES, 1)[1]
                        proxies = [ proxy.strip() for proxy in proxies_str.split(',') if proxy.strip() ]
                        return self.send_head_proxies(data, path, proxies)
                    elif processor.startswith(PROXY_SESSION):
                        proxies_str = processor.split(PROXY_SESSION, 1)[1]
                        cookie_name = proxies_str.split(':', 1)[0]
                        proxies_str = proxies_str.split(':', 1)[1]
                        proxies = {}
                        for proxy_str in filter(None, proxies_str.split(',')):
                            route, proxy = proxy_str.split('=', 1)
                            proxies[route.strip()] = proxy.strip()
                        return self.send_head_proxy_session(data, path, cookie_name, proxies)
                    elif processor.startswith(REDIRECT):
                        location = processor.split(REDIRECT, 1)[1]
                        return self.send_head_redirect(data, path, location)

            self.log_error("No path for: %s" % self.path)
            self.send_response(404, 'File not found')
            return None

        def send_head_redirect(self, data, path, location):
            self.send_response(301)
            self.send_header('Location', location)
            self.end_headers()

        def send_head_proxies(self, data, path, proxies):
            with ProxyHandler.proxies_count_lock:
                ProxyHandler.proxies_count += 1
                current_count = ProxyHandler.proxies_count
            proxy_url = proxies[current_count % len(proxies)]
            return self.send_head_proxy(data, path, proxy_url)

        def send_head_proxy_session(self, data, path, cookie_name, proxies):
            cookies_str = self.headers.get('Cookie', self.headers.get('cookie', None))
            proxy_url = None
            if cookies_str is not None:
                for cookie_str in cookies_str.split(';'):
                    if cookie_str.find('='):
                        current_cookie_name = cookie_str.split('=', 1)[0].strip()
                        if current_cookie_name == cookie_name:
                            value = cookie_str.split('=', 1)[1].strip()
                            if value.find('.') >= 0:
                                value = value.rsplit('.',1)[1].strip()
                                if value in proxies:
                                    proxy_url = proxies[value]
                            break
            if proxy_url is None:
                with ProxyHandler.proxies_count_lock:
                    ProxyHandler.proxies_count += 1
                    current_count = ProxyHandler.proxies_count
                keys = proxies.keys()
                proxy_url = proxies[keys[current_count % len(keys)]]
            return self.send_head_proxy(data, path, proxy_url)

        def send_head_proxy(self, data, path, proxy_url):
            request_headers = dict(self.headers)
            request_headers['X-Forwarded-For'] = self.client_address[0]
            request = urllib2.Request("%s%s" % (proxy_url, path), data, headers = request_headers)
            opener = urllib2.build_opener(AvoidHTTPRedirectHandler)
            try:
                urlobj = opener.open(request)
            except urllib2.HTTPError as e:
                self.send_response(e.code, e.msg) # TODO
                for response_header in e.hdrs:
                    self.send_header(response_header, e.hdrs[response_header])
                self.end_headers()
                return None

            response_headers = urlobj.info()
            self.send_response(200) # TODO
            for response_header in response_headers:
                self.send_header(response_header, response_headers[response_header])
            self.end_headers()
            return urlobj

        def send_head_file(self, data, path, base_path):            
            path = path.split('?', 1)[0]
            path = path.split('#', 1)[0]
            path = path.replace('/', os.sep)
            files = filter(lambda x : x and x != '..', path.split(os.sep))
            if len(files) > 0:
                path = os.path.join(*files)
                final_path = os.path.join(base_path, path)
            else:
                final_path = base_path
            try:
                f = open(final_path, 'rb')
            except:
                self.log_error("Could not find %s" % final_path)
                self.send_response(404, 'File not found')
                return None

            extension = ('.' + final_path).rsplit('.', 1)[1]
            mtype = self.extensions_map.get('.' + extension, 'application/octet-stream')
            fs = os.fstat(f.fileno())
            self.send_response(200)
            self.send_header("Content-type", mtype)
            self.send_header("Content-Length", str(fs[6]))
            self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
            self.end_headers()
            return f

    return ProxyHandler

class ProxyServer(socketserver.ThreadingMixIn, BaseHTTPServer.HTTPServer):
    daemon_threads      = True
    request_queue_size  = 50
    allow_reuse_address = True

    def __init__(self, server_address, proxy_handler):
        BaseHTTPServer.HTTPServer.__init__(self, server_address, proxy_handler)

    def get_request(self):
        sock, addr = BaseHTTPServer.HTTPServer.get_request(self)
        sock.settimeout(None)
        return sock, addr

def run(port, proxy_handler):
    server = ProxyServer(('',port), proxy_handler)
    server.serve_forever()

def start(port, paths):
    proxy_handler = generate_proxy_handler(paths)
    t = threading.Thread(target=run, args = (port, proxy_handler))
    t.setName('proxy-server:%s' % port)
    t.setDaemon(True)
    t.start()
    return t

if __name__ == '__main__':
    paths = [
#        ('/web', 'proxy:http://www.weblab.deusto.es'),
#        ('/foo', 'proxy-sessions:weblabsessionid:route1=http://www.weblab.deusto.es'),
#        ('/client', 'file:/var/www/'),
#        ('/client/foo', 'redirect:/foo'),
    ]
    start(8000, paths)
    raw_input('Listening in port 8000, press Enter to finish...')

