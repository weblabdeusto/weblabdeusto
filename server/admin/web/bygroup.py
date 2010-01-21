import MySQLdb as dbi
import time
import calendar

from configuration import USERNAME, PASSWORD, DB_NAME, GROUPS

def index(req):
    connection = dbi.connect(host="localhost",user=USERNAME, passwd=PASSWORD, db=DB_NAME)
    result = """<html><head><title>Uses per experiment</title></head><body>"""
    try:
        cursor = connection.cursor()
        try:
            for group in GROUPS:
                SENTENCE = "SELECT user_login, user_full_name, wl_User.user_id " + \
                            "FROM wl_User, wl_UserIsMemberOf " + \
                            "WHERE wl_User.user_id = wl_UserIsMemberOf.user_id AND group_id = GetGroupIDByName('%s')" % group
                cursor.execute(SENTENCE)
                users = cursor.fetchall()
                uses_per_user = {}
                user_names    = {}
                total_uses    = 0
                for user, user_full_name, user_id in users:
                    SENTENCE = "SELECT COUNT(uue_user_id) " + \
                                "FROM wl_UserUsedExperiment " + \
                                "WHERE uue_user_id = %s AND uue_experiment_id = GetExperimentIDByName('%s', '%s')" % (user_id, GROUPS[group][0], GROUPS[group][1])
                    cursor.execute(SENTENCE)
                    uses = cursor.fetchall()[0][0]
                    uses_per_user[user] = uses
                    user_names[user] = user_full_name
                    total_uses += uses

                result += "<br><br>\n"
                result += "<b>Experiment: %s</b><br>\n" % (GROUPS[group][0] + '@' + GROUPS[group][1])
                result += "<b>Group: %s</b><br>\n" % group
                result += "<b>Total uses: %s</b><br>\n" % total_uses
                result += "<br><br>\n"
                result += '<table cellspacing="10">\n'
                result += "<tr><td><b>Username</b></td><td><b>Name</b></td><td><b>Uses</b></td></tr>\n" 
                for user in uses_per_user:
                    result += "<tr><td>%s</td><td>%s</td><td>%s</td></tr>\n" % (user, user_names[user].title(), uses_per_user[user])
                result += "</table>\n"
        finally: 
            cursor.close()
    finally:
        connection.close()
    return result + """</body></html>"""

