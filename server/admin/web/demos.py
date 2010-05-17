import MySQLdb as dbi
import time
import socket
import calendar
import re
import subprocess

from configuration import _USERNAME, _PASSWORD, DB_NAME
LIMIT   = 300

_IPv4_EXPR = re.compile("^([1-2]?[0-9]?[0-9]\.){3}[1-2]?[0-9]?[0-9]$")
_CACHE     = {}

def utc2local_str(utc_datetime, format="%Y-%m-%d %H:%M:%S"):
    return time.strftime(format, time.localtime(calendar.timegm(utc_datetime.timetuple())))

def index(req):
    connection = dbi.connect(host="localhost",user=_USERNAME, passwd=_PASSWORD, db=DB_NAME)
    try:
        cursor = connection.cursor()
        try:
            SENTENCE = "SELECT e.name, c.name, uue.start_date, uue.origin " + \
                        "FROM UserUsedExperiment as uue, User as u, Experiment as e, ExperimentCategory as c " + \
                        "WHERE u.login = 'demo' AND u.id = uue.user_id AND e.id = uue.experiment_id AND e.category_id = c.id " + \
                        "ORDER BY uue.start_date DESC LIMIT %s" % LIMIT
            cursor.execute(SENTENCE)
            elements = cursor.fetchall()
            result = """<html><head><title>Latest uses of demo</title></head><body><table cellspacing="20">
                        <tr> <td><b>Experiment</b></td> <td><b>Date</b></td> <td><b>From </b> </td> <td><b>From (resolved) </b></td></tr>
                        """
            cached = set()
            for experiment_name, category_name, start_date, uue_from in elements:
                cached.add(uue_from)
                if uue_from in _CACHE:
                    resolved = _CACHE[uue_from]
                else:
                    try:
                        resolved = socket.gethostbyaddr(uue_from)[0]
                    except Exception, e:
                        if uue_from.startswith("127.") or uue_from.startswith("192.168"):
                            resolved = "local network"
                        else:
                            # A malicious user could inject a message if he says that he's behind a proxy.
                            # We don't want this message to inject anything to the whois command
                            if _IPv4_EXPR.match(uue_from.strip()) is not None:
                                try:
                                    p = subprocess.Popen(("whois", uue_from.strip()), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                                    p.wait()
                                    lines = [ line for line in p.stdout.read().split("\n") if line.startswith("country:") ]
                                    if lines > 0:
                                        resolved = lines[0].split(":")[1].strip()
                                    else:
                                        resolved = "Could not retrieve info even from whois"
                                except Exception, e:
                                    resolved = "Could not retrieve info and whois failed %s" % str(e)
                            else:
                                resolved = str(e)
                    _CACHE[uue_from] = resolved

                result += "\t<tr> <td> %s </td> <td> %s </td> <td> %s </td> <td> %s </td> </tr>\n" % ( experiment_name + '@' + category_name, utc2local_str(start_date), uue_from, resolved )
            # Clean the cache
            for key in cached:
                if not key in _CACHE:
                    _CACHE.pop(key)
        finally: 
            cursor.close()
    finally:
        connection.close()
    return result + """</table></body></html>"""

