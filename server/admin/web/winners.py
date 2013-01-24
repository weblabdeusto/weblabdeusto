import MySQLdb as dbi
import time
import calendar

from configuration import DB_NAME, _USERNAME, _PASSWORD

def utc2local_str(utc_datetime, format="%Y-%m-%d %H:%M:%S"):
    return time.strftime(format, time.localtime(calendar.timegm(utc_datetime.timetuple())))

def index(req):
    connection = dbi.connect(host="localhost",user=_USERNAME, passwd=_PASSWORD, db=DB_NAME)
    try:
        cursor = connection.cursor()
        try:
            SENTENCE = "SELECT u.login, u.full_name, uc.response, uue.end_date, uue.id " + \
                        "FROM UserUsedExperiment as uue, User as u, UserCommand as uc, Experiment as e, ExperimentCategory as ec " + \
                        "WHERE u.id = uue.user_id AND uue.experiment_id = e.id AND e.name = 'ud-logic' AND e.category_id = ec.id AND ec.name = 'PIC experiments' AND uc.experiment_use_id = uue.id AND SUBSTRING(uc.response, 1, 2) = 'OK' " + \
                        "ORDER BY uue.experiment_id "
            cursor.execute(SENTENCE)
            elements = cursor.fetchall()
            result = """<html><head><title>Best results</title></head><body><table cellspacing="10">
                        <tr> <td><b>User</b></td> <td><b>Name</b></td> <td><b>Points</b></td> <td><b>Date</b></td></tr>
                        """
        finally: 
            cursor.close()
    finally:
        connection.close()

    final_elements = {}
    for user_login, full_name, points, end_date, use_id in elements:
        final_elements[use_id] = (user_login, full_name, int(points[len('OK: '):]), end_date)

    final_values = [ value for value in final_elements.values() if value[2] is not None and value[3] is not None ]
    final_values.sort(lambda x, y: -1 * cmp(x[2], y[2]) or cmp(x[3], y[3]))

    for user_login, full_name, points, end_date in final_values:
        result += "\t<tr> <td> %s </td> <td> %s </td> <td> %s </td> <td> %s </td> </tr>\n" % ( user_login, full_name, points, utc2local_str(end_date) )

    return result + """</table></body></html>"""

