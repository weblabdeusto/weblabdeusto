import MySQLdb as dbi
import time
import calendar

from configuration import _USERNAME, _PASSWORD, DB_NAME, GROUPS, GROUP_KEYS

def index(req):
    for group in GROUPS:
        if not group in GROUP_KEYS:
            return """<html><body>Missing group %s in GROUP_KEYS</body></html>""" % group
    for group in GROUP_KEYS:
        if not group in GROUPS:
            return """<html><body>Missing group %s in GROUPS</body></html>""" % group

    connection = dbi.connect(host="localhost",user=_USERNAME, passwd=_PASSWORD, db=DB_NAME)
    result = """<html><head><title>Uses per experiment</title></head><body>"""
    try:
        cursor = connection.cursor()
        try:
            for group in GROUP_KEYS:
                SENTENCE = "SELECT u.login, u.full_name, u.id " + \
                            "FROM %(DB)s.User as u, %(DB)s.UserIsMemberOf as m, %(DB)s.Group as g " % { 'DB': DB_NAME } + \
                            "WHERE u.id = m.user_id AND m.group_id = g.id AND g.name = '%(GROUP)s'" % { 'GROUP': group }
                cursor.execute(SENTENCE)
                users = cursor.fetchall()
                uses_per_user = {}
                user_names    = {}
                total_uses    = 0
                for user, user_full_name, user_id in users:
                    SENTENCE = "SELECT COUNT(uue.user_id) " + \
                                "FROM UserUsedExperiment as uue, Experiment as e, ExperimentCategory as c " + \
                                "WHERE uue.user_id = %s AND uue.experiment_id = e.id AND e.name = '%s' AND e.category_id = c.id AND c.name = '%s'" % (user_id, GROUPS[group][0], GROUPS[group][1])
                    cursor.execute(SENTENCE)
                    uses = cursor.fetchall()[0][0]
                    uses_per_user[user] = uses
                    user_names[user] = user_full_name
                    total_uses += uses
                result += "<br><br>\n"
                result += "<b>Experiment: %s</b><br>\n" % (GROUPS[group][0] + '@' + GROUPS[group][1])
                result += "<b>Group: %s</b><br>\n" % group
                result += "<b>Total uses: %s</b><br>\n" % total_uses
                result += "<b>Total users: %s</b><br>\n" % len(user_names)
                result += "<b>Mean by user: %.2f</b><br>\n" % (1.0 * total_uses / len(user_names))
                result += "<br><br>\n"
                result += '<table cellspacing="10">\n'
                result += "<tr><td><b>Username</b></td><td><b>Name</b></td><td><b>Uses</b></td></tr>\n" 
                sorted_keys = sorted(zip(uses_per_user.keys(), uses_per_user.values()), cmp = lambda (key1, value1), (key2, value2) : -1 * cmp(value1, value2))
                for user, _ in sorted_keys:
                    result += "<tr><td><a href=\"uses.py/user?login=%s\">%s</a></td><td>%s</td><td>%s</td></tr>\n" % (user, user, user_names[user].title(), uses_per_user[user])
                result += "</table>\n"
        finally: 
            cursor.close()
    finally:
        connection.close()
    return result + """</body></html>"""

