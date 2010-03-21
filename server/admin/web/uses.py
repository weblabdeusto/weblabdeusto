import MySQLdb as dbi
import time
import calendar

from configuration import _USERNAME, _PASSWORD, DB_NAME

LIMIT   = 150

def utc2local_str(utc_datetime, format="%Y-%m-%d %H:%M:%S"):
    return time.strftime(format, time.localtime(calendar.timegm(utc_datetime.timetuple())))

def index(req):
    connection = dbi.connect(host="localhost",user=_USERNAME, passwd=_PASSWORD, db=DB_NAME)
    try:
        cursor = connection.cursor()
        try:
            SENTENCE = "SELECT u.login, e.name, c.name, uue.start_date, uue.origin " + \
                        "FROM UserUsedExperiment as uue, User as u, Experiment as e, ExperimentCategory as c " + \
                        "WHERE u.id = uue.user_id AND e.id = uue.experiment_id AND e.category_id = c.id " + \
                        "ORDER BY uue.start_date DESC LIMIT %s" % LIMIT
            cursor.execute(SENTENCE)
            elements = cursor.fetchall()
            result = """<html><head><title>Latest uses</title></head><body><table cellspacing="20">
                        <tr> <td><b>User</b></td> <td><b>Experiment</b></td> <td><b>Date</b></td> <td><b>From </b> </td></tr>
                        """
            for user_login, experiment_name, category_name, start_date, uue_from in elements:
                result += "\t<tr> <td> %s </td> <td> %s </td> <td> %s </td> <td> %s </td> </tr>\n" % ( user_login, experiment_name + '@' + category_name, utc2local_str(start_date), uue_from )
        finally: 
            cursor.close()
    finally:
        connection.close()
    return result + """</table></body></html>"""

