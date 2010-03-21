import MySQLdb as dbi
import time
import socket
import calendar

from configuration import _USERNAME, _PASSWORD, DB_NAME
LIMIT   = 300

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
            for experiment_name, category_name, start_date, uue_from in elements:
                try:
                    resolved = socket.gethostbyaddr(uue_from)[0]
                except Exception, e:
                    resolved = str(e)
                result += "\t<tr> <td> %s </td> <td> %s </td> <td> %s </td> <td> %s </td> </tr>\n" % ( experiment_name + '@' + category_name, utc2local_str(start_date), uue_from, resolved )
        finally: 
            cursor.close()
    finally:
        connection.close()
    return result + """</table></body></html>"""

