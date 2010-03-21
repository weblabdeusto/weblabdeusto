import MySQLdb as dbi
import time
import calendar

from configuration import DB_NAME, _USERNAME, _PASSWORD, LOGIC_EXP_ID

def utc2local_str(utc_datetime, format="%Y-%m-%d %H:%M:%S"):
    return time.strftime(format, time.localtime(calendar.timegm(utc_datetime.timetuple())))

def index(req):
    connection = dbi.connect(host="localhost",user=_USERNAME, passwd=_PASSWORD, db=DB_NAME)
    try:
        cursor = connection.cursor()
        try:
            SENTENCE = "SELECT u.login, uc.response, uue.end_date, uue.id " + \
                        "FROM UserUsedExperiment as uue, User as u, UserCommand as uc " + \
                        "WHERE u.id = uue.user_id AND uue.experiment_id = " + LOGIC_EXP_ID + " AND uc.experiment_use_id = uue.id AND SUBSTRING(uc.response, 1, 2) = 'OK' " + \
                        "ORDER BY uue.experiment_id "
            cursor.execute(SENTENCE)
            elements = cursor.fetchall()
            result = """<html><head><title>Best results</title></head><body><table cellspacing="10">
                        <tr> <td><b>User</b></td> <td><b>Points</b></td> <td><b>Date</b></td></tr>
                        """
        finally: 
            cursor.close()
    finally:
        connection.close()

    final_elements = {}
    for user_login, points, end_date, use_id in elements:
        final_elements[use_id] = (user_login, int(points[len('OK: '):]), end_date)

    final_values = final_elements.values()
    final_values.sort(lambda x, y: -1 * cmp(x[1], y[1]) or cmp(x[2], y[2]))

    for user_login, points, end_date in final_values:
        result += "\t<tr> <td> %s </td> <td> %s </td> <td> %s </td> </tr>\n" % ( user_login, points, utc2local_str(end_date) )

    return result + """</table></body></html>"""

