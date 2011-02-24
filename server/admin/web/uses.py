import MySQLdb as dbi
import cgi
import time
import calendar

from configuration import _USERNAME, _PASSWORD, DB_NAME

LIMIT   = 150

def utc2local_str(utc_datetime, format="%Y-%m-%d %H:%M:%S"):
    return time.strftime(format, time.localtime(calendar.timegm(utc_datetime.timetuple())))

def use(req, **kwargs):
    if 'use_id' not in kwargs:
        return "You need to provide use_id, being an ID of a use"

    try:
        use_id = int(kwargs['use_id'])
    except:
        return "You need to provide use_id, being an ID of a use"


    connection = dbi.connect(host="localhost",user=_USERNAME, passwd=_PASSWORD, db=DB_NAME)
    try:
        cursor = connection.cursor()
        try:
            SENTENCE = "SELECT uc.command, uc.response, uc.timestamp_before, uc.timestamp_before_micro, uc.timestamp_after, uc.timestamp_after_micro " + \
                        "FROM UserCommand as uc " + \
                        "WHERE uc.experiment_use_id = %s "+ \
                        "ORDER BY uc.timestamp_before DESC LIMIT %s" % LIMIT
            cursor.execute(SENTENCE, (use_id,))
            elements = cursor.fetchall()
            result = """<html><head><title>Latest uses</title></head><body><table cellspacing="20">
                        <tr> <td><b>Command</b></td> <td><b>Response</b></td> <td><b>Time before</b></td> <td><b>Time after</b></td></tr>
                        """
            for command, response, timestamp_before, timestamp_before_micro, timestamp_after, timestamp_after_micro in elements:
                if timestamp_before is None:
                    before = "<not provided>"
                else:
                    before = "%s:%s" % (timestamp_before.strftime("%d/%m/%y %H:%M:%S"), str(timestamp_before_micro).zfill(6))
                if timestamp_after is None:
                    after  = "<not provided>"
                else:
                    after  = "%s:%s" % (timestamp_after.strftime("%d/%m/%y %H:%M:%S"), str(timestamp_after_micro).zfill(6))

                result += "\t<tr> <td> %s </td> <td> %s </td> <td> %s </td> <td> %s </td> </tr>\n" % ( cgi.escape(command), cgi.escape(response), before, after )
        finally: 
            cursor.close()
    finally:
        connection.close()
    return result + """</table></body></html>"""

def index(req):
    connection = dbi.connect(host="localhost",user=_USERNAME, passwd=_PASSWORD, db=DB_NAME)
    try:
        cursor = connection.cursor()
        try:
            SENTENCE = "SELECT uue.id, u.login, u.full_name, e.name, c.name, uue.start_date, uue.origin " + \
                        "FROM UserUsedExperiment as uue, User as u, Experiment as e, ExperimentCategory as c " + \
                        "WHERE u.id = uue.user_id AND e.id = uue.experiment_id AND e.category_id = c.id " + \
                        "ORDER BY uue.start_date DESC LIMIT %s" % LIMIT
            cursor.execute(SENTENCE)
            elements = cursor.fetchall()
            result = """<html><head><title>Latest uses</title></head><body><table cellspacing="20">
                        <tr> <td><b>User</b></td> <td><b>Name</b></td> <td><b>Experiment</b></td> <td><b>Date</b></td> <td><b>From </b> </td> <td><b>Use</b></td></tr>
                        """
            for use_id, user_login, user_full_name, experiment_name, category_name, start_date, uue_from in elements:
                result += "\t<tr> <td> %s </td> <td> %s </td> <td> %s </td> <td> %s </td> <td> %s </td> <td> <a href=\"uses.py/use?use_id=%s\">use</a> </td> </tr>\n" % ( user_login, user_full_name, experiment_name + '@' + category_name, utc2local_str(start_date), uue_from, use_id )
        finally: 
            cursor.close()
    finally:
        connection.close()
    return result + """</table></body></html>"""

