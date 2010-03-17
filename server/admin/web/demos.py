import MySQLdb as dbi
import time
import socket
import calendar

from configuration import USERNAME, PASSWORD, DB_NAME
LIMIT   = 300

def utc2local_str(utc_datetime, format="%Y-%m-%d %H:%M:%S"):
    return time.strftime(format, time.localtime(calendar.timegm(utc_datetime.timetuple())))

def index(req):
    connection = dbi.connect(host="localhost",user=USERNAME, passwd=PASSWORD, db=DB_NAME)
    try:
        cursor = connection.cursor()
        try:
            SENTENCE = "select experiment_name, experiment_category_name, uue_start_date, uue_from " + \
                        "from wl_UserUsedExperiment, wl_User, wl_Experiment, wl_ExperimentCategory " + \
                        "WHERE user_login = 'demo' AND user_id = uue_user_id AND experiment_id = uue_experiment_id AND wl_Experiment.experiment_category_id = wl_ExperimentCategory.experiment_category_id " + \
                        "order by uue_start_date desc limit %s" % LIMIT
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

