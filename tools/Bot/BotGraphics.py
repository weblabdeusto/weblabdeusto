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

import os

from BotMisc import show_time, flush
import Configuration

import matplotlib
matplotlib.use(Configuration.MATPLOTLIB_BACKEND)
import matplotlib.pyplot as plt

METHODS = ["login", "list_experiments", "reserve_experiment", "get_reservation_status", "logout", "finished_experiment", "send_file", "send_command", "poll", "get_user_information"]
CALL_TIMES = ('avg_call_times', 'min_call_times', 'max_call_times')

def colours():
    yield "r", "red"
    yield "g", "green"
    yield "b", "blue"

def get_figure_filename(xxx_call_times, method, date):
    return "figures" + os.sep + "figure_" + date + "_" + xxx_call_times + "_" + method + ".png"

def generate_html(xxx_call_times, methods, date):
    page = """<html><head><title>Bot stats as of %s</title></head><body>
    <h1>Bot stats as of %s</h1>
    <h2>Stats information</h2>
    Configuration: %s<br/>
    System: %s<br/>
    <a name="index"><h2>Index</h2></a>
    <ul>
    """ % (date, date,Configuration.RUNNING_CONFIGURATION, Configuration.SYSTEM)

    for xxx_call_time in xxx_call_times:
        page += """\t<li><a href="#%s">%s</a>: <ul>""" % (xxx_call_time, xxx_call_time)
        for method in methods:
            page += """\t\t<li><a href="#%s_%s">%s</a></li>\n""" % (xxx_call_time, method, method)
        page += """\t</ul></li>\n"""

    page += """</ul><h2>Results</h2>\n"""
    for xxx_call_time in xxx_call_times:
        page += """<br/><br/><a name="%s"><h3>%s</h3></a><center>\n""" % (xxx_call_time, xxx_call_time)

        for method in methods:
            page += """<a name="%s_%s"><h4>%s</h4></a>\n""" % (xxx_call_time, method, method)
            figure_filename = get_figure_filename(xxx_call_time, method, date)
            page += """<a href="%s"><img width="500" src="%s"/></a>\n""" % (figure_filename, figure_filename)
            page += """<br/>\n"""
            page += """<a href="#index">Back to index</a>"""
        page += """</center>"""

    page += """</body></html>"""
    return page

def print_results(raw_information, date, verbose = True):
    working_methods = METHODS[:]

    for xxx_call_times in CALL_TIMES:
        for method in METHODS:
            if verbose:
                print "Plotting with method: %s and xxx_call_times: %s; %s" % (method, xxx_call_times, show_time())
                flush()
            def func_on_results(results):
                return getattr(results, xxx_call_times)[method]

            colours_it = colours()
            fig = plt.figure()
            ax = fig.add_subplot(111)

            xlabel = "Protocols:\n"
            any_worked = False
            for protocol in raw_information.keys():
                try:
                    x, y = raw_information[protocol]
                    y = map(func_on_results, y)
                    code, colour = colours_it.next()
                    ax.plot(x,y, '%s-' % code)
                    xlabel += "%s: %s; " % (protocol, colour)
                except KeyError, ke:
                    continue
                except: 
                    import traceback
                    traceback.print_exc()
                    continue
                else:
                    any_worked = True

            if any_worked:
                ax.set_xlabel(xlabel)
                plt.savefig(get_figure_filename(xxx_call_times, method, date))
            else:
                if verbose:
                    print "Skipping method %s" % method
                    flush()
                if method in working_methods:
                    working_methods.remove(method)


    html = generate_html(CALL_TIMES, working_methods, date)
    html_filename = 'botclient_%s.html' % date
    open(html_filename, 'w').write(html)

    if verbose:
        print "HTML file available in",html_filename
        print "Finished plotting; %s" % show_time()
        flush()

if __name__ == '__main__':
    DATE = "D_2009_08_10_T_09_34_44"
    #DATE = "D_2009_08_11_T_00_38_30"

    from BotInformationRetriever import get_raw_information
    raw_information = get_raw_information(DATE)
    print_results(raw_information, DATE)

