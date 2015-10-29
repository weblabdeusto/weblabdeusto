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
from __future__ import print_function, unicode_literals
import os
import time
from collections import OrderedDict
from weblab.util import data_filename
import flask_admin

def weblab_httpd_config_generate(directory):
    print("Generating HTTPd configuration files... ", end='')
    result = httpd_config_generate(directory)
    print("[done]")
    return result

def httpd_config_generate(directory):
    debugging_variables = {}
    execfile(os.path.join(directory, 'debugging.py'), debugging_variables)
    ports = debugging_variables.get('PORTS', {}).get('json')
    base_url = debugging_variables.get('BASE_URL', '')
    if base_url in ('','/'):
        base_url = ''

    static_directories = OrderedDict() #{
        # url path : disk path
    # }
    static_directories[base_url + '/weblab/client'] =                            data_filename('weblab/core/static/oldclient').replace('\\','/') # \ => / for Windows
    flask_admin_static = os.path.join(os.path.dirname(flask_admin.__file__), 'static')
    static_directories[base_url + '/weblab/admin/static'] =                      flask_admin_static.replace('\\','/')
    # TODO: Avoid repeated paths
    static_directories[base_url + '/weblab/instructor/static'] =                 data_filename('weblab/admin/web/static').replace('\\','/')
    static_directories[base_url + '/weblab/profile/static'] =                    data_filename('weblab/admin/web/static').replace('\\','/')
    static_directories[base_url + '/weblab/web/static'] =                        data_filename('weblab/core/static').replace('\\','/')
    static_directories[base_url + '/weblab/static'] =                            data_filename('weblab/core/static').replace('\\','/')
    static_directories[base_url + '/weblab/gwt/weblabclientlab'] =               data_filename('war/weblabclientlab').replace('\\','/')
    static_directories[base_url + '/weblab/web/pub'] =                           os.path.abspath(os.path.join(directory, 'pub')).replace('\\','/')

    files = {}
    apache_contents = _apache_generation(directory, base_url, ports, static_directories)
    files['apache'] = _set_contents(directory, 'httpd/apache_weblab_generic.conf', apache_contents)
    simple_httpd_contents = _simple_httpd_generation(directory, base_url, ports, static_directories)
    files['simple'] = _set_contents(directory, 'httpd/simple_server_config.py', simple_httpd_contents)
    
    # TODO: support nginx

    return files

def _set_contents(directory, filename, new_contents):
    original_path = os.path.join(directory, filename)
    destination_path = os.path.join(directory, filename + "-backup-" + time.strftime("%Y-%m-%d_%H-%M-%S"))
    if os.path.exists(original_path):
        original_contents = open(original_path).read()
        open(destination_path, 'w').write(original_contents)
    open(original_path, 'w').write(new_contents)
    return os.path.abspath(original_path)


def _apache_generation(directory, base_url, ports, static_directories):
    apache_conf = (
    "\n"
    """<LocationMatch (.*)nocache\.js$>\n"""
    """   Header Set Cache-Control "max-age=0, no-store"\n"""
    """</LocationMatch>\n"""
    """\n"""
    """<Files *.cache.*>\n"""
    """   Header Set Cache-Control "max-age=2592000"\n"""
    """</Files>\n"""
    """\n"""
    """# Apache redirects the regular paths to the particular directories \n"""
#    """RedirectMatch ^%(root)s$ %(root)s/weblab/\n"""
#    """RedirectMatch ^%(root)s/$ %(root)s/weblab/\n"""
    """RedirectMatch ^%(root)s/weblab$ %(root)s/weblab/\n"""
    """RedirectMatch ^%(root)s/weblab/client/$ %(root)s/weblab/client/index.html\n"""
    """\n""")
    
    for static_url, static_directory in static_directories.items():
        apache_conf += """Alias %(static_url)s   %(static_directory)s\n""" % dict(static_url=static_url, static_directory=static_directory)

    apache_conf += (
    """\n"""
    """<Location %(root)s/weblab/>\n"""
    """    <IfModule authz_core_module>\n"""
    """        Require all granted\n"""
    """    </IfModule>\n"""
    """\n"""
    """    <IfModule !authz_core_module>\n"""
    """        Order allow,deny\n"""
    """        Allow from All\n"""
    """    </IfModule>\n"""
    """</Location>\n"""
    """\n"""
    """<Directory "%(directory)s">\n"""
    """    Options Indexes\n"""
    """\n"""
    """    <IfModule authz_core_module>\n"""
    """        Require all granted\n"""
    """    </IfModule>\n"""
    """\n"""
    """    <IfModule !authz_core_module>\n"""
    """        Order allow,deny\n"""
    """        Allow from All\n"""
    """    </IfModule>\n"""
    """</Directory>\n"""
    """\n""")

    previous = []
    for static_directory in static_directories.values():
        if static_directory in previous:
            continue
        previous.append(static_directory)
        apache_conf += ("""<Directory "%(static_directory)s">\n"""
        """    Options Indexes FollowSymLinks\n"""
        """\n"""
        """    <IfModule authz_core_module>\n"""
        """        Require all granted\n"""
        """    </IfModule>\n"""
        """\n"""
        """    <IfModule !authz_core_module>\n"""
        """        Order allow,deny\n"""
        """        Allow from All\n"""
        """    </IfModule>\n"""
        """</Directory>\n"""
        """\n""") % dict(static_directory=static_directory)

    apache_conf += (
    """# Apache redirects the requests retrieved to the particular server, using a stickysession if the sessions are based on memory\n"""
    """ProxyPreserveHost On\n"""
    """ProxyVia On\n"""
    """\n""")

    for static_url, static_directory in static_directories.items():
        apache_conf += """ProxyPass %(static_url)s !\n""" % dict(static_url=static_url)

    apache_conf += (
    """\n"""
    """ProxyPass                       %(root)s/weblab/                 balancer://%(root-no-slash)s_weblab_cluster/           stickysession=weblabsessionid lbmethod=bybusyness\n"""
    """ProxyPassReverse                %(root)s/weblab/                 balancer://%(root-no-slash)s_weblab_cluster/           stickysession=weblabsessionid\n"""
    "\n")
    apache_conf += "\n"
    apache_conf += """<Proxy balancer://%(root-no-slash)s_weblab_cluster>\n"""

    for pos, port in enumerate(ports):
        d = { 'port' : port, 'route' : 'route%s' % (pos+1), 'root' : '%(root)s' }
        apache_conf += """    BalancerMember http://localhost:%(port)s/weblab route=%(route)s\n""" % d

    apache_conf += """</Proxy>\n"""
    apache_img_dir = '/client/images'

    apache_root_without_slash = base_url[1:] if base_url.startswith('/') else base_url

    server_conf_dict = { 'root' : base_url,  'root-no-slash' : apache_root_without_slash.replace('/','_'),
                'directory' : os.path.abspath(directory).replace('\\','/'),
                'war_path' : data_filename('war').replace('\\','/') }

    apache_conf = apache_conf % server_conf_dict
    apache_conf_path = os.path.join('', 'apache_weblab_generic.conf')
    return apache_conf 


def _simple_httpd_generation(directory, base_url, ports, static_directories):
    proxy_paths = [
        ('%(root)s$',                    'redirect:%(root)s/weblab/'),
        ('%(root)s/$',                   'redirect:%(root)s/weblab/'),
        ('%(root)s/weblab/client$',      'redirect:%(root)s/weblab/client/index.html'),
    ]
    for key, directory in static_directories.items():
        proxy_paths.append((key, 'file:{0}'.format(directory)))

    proxy_path = "proxy-sessions:weblabsessionid:"
    for pos, port in enumerate(ports):
        d = { 'port' : port, 'route' : 'route%s' % (pos+1), 'root' : '%(root)s' }
        proxy_path += '%(route)s=http://localhost:%(port)s/weblab/,' % d
    proxy_paths.append(('%(root)s/weblab/', proxy_path))

    proxy_paths.append(('%(root)s/weblab',              'redirect:%(root)s/weblab/'))
    proxy_paths.append(('',                            'redirect:%(root)s/weblab/'))

    if base_url in ('','/'):
        root    = ''
    else:
        root    = base_url

    apache_img_dir = '/client/images'

    server_conf_dict = { 'root' : root, 
                'directory' : os.path.abspath(directory).replace('\\','/')
            }

    proxy_paths = eval(repr(proxy_paths) % server_conf_dict)
    proxy_paths_str = "PATHS = [ \n"
    for proxy_path in proxy_paths:
        proxy_paths_str += "    %s,\n" % repr(proxy_path)
    proxy_paths_str += "]\n"

    return proxy_paths_str

if __name__ == '__main__':
    httpd_config_generate("/tmp/foo")
