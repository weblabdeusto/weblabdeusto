import MySQLdb as dbi
import time
import calendar

from configuration import DB_NAME, USERNAME, PASSWORD

def utc2local_str(utc_datetime, format="%Y-%m-%d %H:%M:%S"):
    return time.strftime(format, time.localtime(calendar.timegm(utc_datetime.timetuple())))

def index(req):
    connection = dbi.connect(host="localhost",user=USERNAME, passwd=PASSWORD, db=DB_NAME)
    try:
        cursor = connection.cursor()
        try:
            SENTENCE = "SELECT user_login, response, uue_finish_date, uue_user_experiment_use_id " + \
                        "FROM wl_UserUsedExperiment, wl_User, wl_UserCommand  " + \
                        "WHERE user_id = uue_user_id AND uue_experiment_id = " + LOGIC_EXP_ID + " AND experiment_use_id = uue_user_experiment_use_id AND SUBSTRING(response, 1, 2) = 'OK' " + \
                        "ORDER BY uue_experiment_id "
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

