import MySQLdb as dbi
import time
import socket
import calendar
import re
import subprocess

from configuration import _USERNAME, _PASSWORD, DB_NAME, LOCATIONS_DB_NAME, _LOCATIONS_USERNAME, _LOCATIONS_PASSWORD
LIMIT   = 1000

_IPv4_EXPR = re.compile("^([1-2]?[0-9]?[0-9]\.){3}[1-2]?[0-9]?[0-9]$")
_CACHE     = {}

def utc2local_str(utc_datetime, format="%Y-%m-%d %H:%M:%S"):
    return time.strftime(format, time.localtime(calendar.timegm(utc_datetime.timetuple())))

class _HostResolver(object):
    # 
    # Optionally, the ip_address <-> host name can be stored in a database.
    # In order to do so, the database LOCATIONS_DB_NAME must be created and must be
    # accessible by the user _LOCATIONS_USERNAME, _LOCATIONS_PASSWORD. 
    # 
    # The content of this database is as simple as:
    # 
    # CREATE TABLE Locations(ip_address VARCHAR(255), resolved VARCHAR(255));
    # 
    # 
    def get_results(self, ip_address):
        try:
            connection = dbi.connect(host="localhost",user=_LOCATIONS_USERNAME, passwd=_LOCATIONS_PASSWORD, db=LOCATIONS_DB_NAME)
        except:
            return 
        try:
            cursor = connection.cursor()
            try:
                sentence = "SELECT resolved FROM Locations WHERE ip_address = %s"
                cursor.execute(sentence, (ip_address,))
                results = cursor.fetchall()
                if len(results) == 0:
                    return
                else:
                    return results[0][0]
            finally:
                cursor.close()
        finally:
            connection.close()

    def store_results(self, ip_address, resolved):
        try:
            connection = dbi.connect(host="localhost",user=_LOCATIONS_USERNAME, passwd=_LOCATIONS_PASSWORD, db=LOCATIONS_DB_NAME)
        except:
            return 
        try:
            cursor = connection.cursor()
            try:
                sentence = "INSERT INTO Locations(ip_address, resolved) VALUES(%s,%s)"
                cursor.execute(sentence, (ip_address, resolved))
            finally:
                cursor.close()
        finally:
            connection.close()


    def retrieve_from_cache(self, ip_address):
        return _CACHE.get(ip_address) or self.get_results(ip_address)

    def store_in_cache(self, ip_address, resolved):
        _CACHE[ip_address] = resolved
        self.store_results(ip_address, resolved)

    def resolve(self, ip_address):
        cached = self.retrieve_from_cache(ip_address)
        if cached is not None:
            return cached
        try:
            resolved = socket.gethostbyaddr(ip_address)[0]
        except Exception, e:
            if ip_address.startswith("127.") or ip_address.startswith("192.168"):
                resolved = "local network"
            else:
                # A malicious user could inject a message if he says that he's behind a proxy.
                # We don't want this message to inject anything to the whois command
                if _IPv4_EXPR.match(ip_address.strip()) is not None:
                    try:
                        p = subprocess.Popen(("whois", ip_address.strip()), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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
        self.store_in_cache(ip_address, resolved)
        return resolved

_resolver = _HostResolver()

def index(req):
    connection = dbi.connect(host="localhost",user=_USERNAME, passwd=_PASSWORD, db=DB_NAME)
    try:
        cursor = connection.cursor()
        try:
            SENTENCE = "SELECT u.full_name, e.name, c.name, uue.start_date, uue.origin " + \
                        "FROM UserUsedExperiment as uue, User as u, Experiment as e, ExperimentCategory as c, `Group` as g, UserIsMemberOf as uimo " + \
                        "WHERE g.name = 'Demos' AND g.id = uimo.group_id AND u.id = uimo.user_id AND u.id = uue.user_id AND e.id = uue.experiment_id AND e.category_id = c.id " + \
                        "ORDER BY uue.start_date DESC LIMIT %s" % LIMIT
            cursor.execute(SENTENCE)
            elements = cursor.fetchall()
            result = """<html><head><title>Latest uses of demo</title></head><body><table cellspacing="20">
                        <tr> <td><b>Name</b></td><td><b>Experiment</b></td> <td><b>Date</b></td> <td><b>From </b> </td> <td><b>From (resolved) </b></td></tr>
                        """
            for name, experiment_name, category_name, start_date, uue_from in elements:
                resolved = _resolver.resolve(uue_from)
                result += "\t<tr> <td> %s </td><td> %s </td> <td> %s </td> <td> %s </td> <td> %s </td> </tr>\n" % ( name, experiment_name + '@' + category_name, utc2local_str(start_date), uue_from, resolved )
        finally: 
            cursor.close()
    finally:
        connection.close()
    return result + """</table></body></html>"""

