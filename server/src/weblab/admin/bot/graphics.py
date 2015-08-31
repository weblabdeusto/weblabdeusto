#!/usr/bin/env python
#-*-*- encoding: utf-8 -*-*-
#
# Copyright (C) 2005-2009 University of Deusto
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
import sys
import json

from weblab.admin.bot.misc import show_time, flush
import platform

METHODS = ["login", "list_experiments", "reserve_experiment", "get_reservation_status", "logout", "finished_experiment", "send_file", "send_command", "poll", "get_user_information"]
CALL_TIMES = ('avg_call_times', 'min_call_times', 'max_call_times')

GET_FIGURE_FILENAME_CODE="""def get_figure_filename(protocol, method, date):
    return "figures" + os.sep + "figure_" + date + "_" + protocol + "_" + method + ".png"
"""

def get_figure_filename(protocol, method, date):
    " The exec() after this will rewrite this function. This is only written so as to avoid warnings. "
    pass

exec(GET_FIGURE_FILENAME_CODE)

def generate_html(protocols, configuration, methods, date, default_system_info, running_configuration):

    # Retrieve this information in Linux systems
    try:
        model_name = [ line for line in open("/proc/cpuinfo").readlines() if line.startswith("model name") ][0]
        model_name = ':'.join(model_name.split(': ')[1:]).strip()
        while '  ' in model_name:
            model_name = model_name.replace('  ',' ')

        ram = [ line.split(' ')[-2] for line in open("/proc/meminfo").readlines() if line.startswith("MemTotal:")][0]
        memory = '%.2fGB' % ( int(ram) / (1024.0 * 1024.0))
    except:
        system_info = default_system_info
    else:
        system_info = "%s %s" % (model_name, memory)

    all_system_info = "%s; %s; Python %s" % (system_info, platform.platform(), platform.python_version())

    page = """<html><head><title>Bot stats as of %s</title></head><body>
    <h1>Bot stats as of %s</h1>
    <h2>Stats information</h2>
    Configuration: %s %s<br/>
    System: %s<br/>
    <a name="index"><h2>Index</h2></a>
    <ul>
    """ % (date, date, running_configuration, str(configuration), all_system_info)

    for protocol in protocols:
        page += """\t<li><a href="#%s">%s</a>: <ul>""" % (protocol, protocol)
        for method in methods:
            page += """\t\t<li><a href="#%s_%s">%s</a></li>\n""" % (protocol, method, method)
        page += """\t</ul></li>\n"""

    page += """</ul><h2>Results</h2>\n"""
    page += """<center><table border="0"><tr>"""
    for protocol in protocols:
        page += """<th><a name="%s"><h3>%s</h3></a><center></th>\n""" % (protocol, protocol)
    page += "</tr>"

    for method in methods:
        page += "<tr>"

        central_pos = len(protocols) / 2
        for pos, protocol in enumerate(protocols):
            page += """<td><center>"""
            if pos == central_pos:
                page += """<a name="%s_%s"><h4>%s</h4></a><br/>\n""" % (protocol, method, method)
            else:
                page += """<br/><br/>"""
            fname = get_figure_filename(protocol, method, date)
            real_fname = os.path.dirname(fname) + os.sep + "without_bounds_" + os.path.basename(fname)
            page += """<a href="%s"><img width="400" src="%s"/></a>\n""" % (real_fname, fname)
            page += """<br/>\n"""
            if pos == central_pos:
                page += """<a href="#index">Back to index</a>"""
            page += """</center></td>"""

        page += """</tr>"""

    page += """</table></center></body></html>"""
    return page

def print_results(raw_information, configuration, date, cfg, verbose = True):
    working_methods = METHODS[:]

    all_data = {
        # method : {
        #      protocol : {
        #          max:  (x,y),
        #          min:  (x,y),
        #          mean: (x,y)
        #      },
        # }
    }

    LINES = ('std','max','min','avg')

    protocols = set()

    for method in METHODS:
        method_data = {}
        all_data[method] = method_data

        for line in LINES:
            def func_on_results(results):
                return getattr(results, line + '_call_times')[method]

            data = {}
            data['protocols'] = raw_information.keys()
            for protocol in data['protocols']:
                try:
                    x, y = raw_information[protocol]
                    y = map(func_on_results, y)
                except KeyError:
                    continue
                except: 
                    import traceback
                    traceback.print_exc()
                    continue
                else:
                    protocols.add(protocol)
                    if not protocol in method_data:
                        method_data[protocol] = {}
                    protocol_data = method_data[protocol]
                    protocol_data[line] = x,y

    for method in METHODS:
        if len(all_data[method]) == 0:
            working_methods.remove(method)
    
    # START PRINTING THIS PART

    CODE="""#!/usr/bin/env python
import os
import math
import matplotlib
if %(backend)r != '':
    matplotlib.use(%(backend)r)
import matplotlib.pyplot as plt

%(get_figure_filename)s

def print_figures():
    
    date            = %(date)r
    working_methods = %(working_methods)r
    all_data        = %(all_data)s

    sorter = lambda (x1, y1), (x2, y2): cmp(x1, x2)

    for method in working_methods:
        method_data = all_data[method]

        max_ys = []
        for protocol in method_data:
            protocol_data = method_data[protocol]
            _,  max_y  = zip(*sorted(zip(*protocol_data['max']), sorter))
            max_ys.append(max(max_y))

        ylim = (0, math.ceil(max(max_ys) + 0.1))

        for protocol in method_data:
            for with_bounds in True, False:
                protocol_data = method_data[protocol]
                fig = plt.figure()
                ax = fig.add_subplot(111)
                ax.set_xlabel("Users")
                ax.set_ylabel("Time (sec)")


                max_x,  max_y  = zip(*sorted(zip(*protocol_data['max']), sorter))
                mean_x, mean_y = zip(*sorted(zip(*protocol_data['avg']), sorter))
                std_x,  std_y  = zip(*sorted(zip(*protocol_data['std']), sorter))
                min_x,  min_y  = zip(*sorted(zip(*protocol_data['min']), sorter))

                ax.plot(max_x, max_y, 'r-')
                ax.errorbar(mean_x, mean_y, yerr=std_y, fmt='g-')
                ax.plot(min_x, min_y, 'b-')

                fname = get_figure_filename(protocol, method, date)
                if with_bounds:
                    ax.set_ybound(*ylim)
                else:
                    current_bounds = list(ax.get_ybound())
                    current_bounds[0] = 0
                    ax.set_ybound(*current_bounds)
                    fname = os.path.dirname(fname) + os.sep + "without_bounds_" + os.path.basename(fname)

                plt.savefig(fname)

if __name__ == '__main__':
    print_figures()
    """ % {
        'backend'             : cfg.MATPLOTLIB_BACKEND,
        'get_figure_filename' : GET_FIGURE_FILENAME_CODE,
        'working_methods'     : working_methods,
        'all_data'            : json.dumps(all_data, indent=4),
        'date'                : date
    }

    generate_figures_script = "figures%sgenerate_figures_%s.py" % (os.sep, date)
    open(generate_figures_script,'w').write(CODE)

    print("Executing %s..." % generate_figures_script,)
    os.system("%s %s" % (sys.executable, generate_figures_script))
    print("[done]")


    html = generate_html(protocols, configuration, working_methods, date, cfg.SYSTEM, cfg.RUNNING_CONFIGURATION)
    html_filename = 'botclient_%s.html' % date
    open(html_filename, 'w').write(html)

    # END PRINTING THIS PART

    if verbose:
        print("HTML file available in",html_filename)
        print("Finished plotting; %s" % show_time())
        flush()

if __name__ == '__main__':
    DATE = "D_2012_04_12_T_09_53_03"

    from weblab.admin.bot.information_retriever import get_raw_information
    raw_information = get_raw_information(DATE)
    print_results(raw_information, "configuration...", DATE)

