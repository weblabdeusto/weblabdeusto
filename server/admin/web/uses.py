import MySQLdb as dbi
import cgi
import time
import datetime
import calendar

from configuration import _USERNAME, _PASSWORD, DB_NAME, _FILES_PATH

LIMIT   = 150

def utc2local_str(utc_datetime, format="%Y-%m-%d %H:%M:%S"):
    return time.strftime(format, time.localtime(calendar.timegm(utc_datetime.timetuple())))

def file(req, **kwargs):
    if 'file_id' not in kwargs:
        return "You need to provide file_id, being an ID of a use"

    try:
        file_id = int(kwargs['file_id'])
    except:
        return "You need to provide file_id, being an ID of a use"

    connection = dbi.connect(host="localhost",user=_USERNAME, passwd=_PASSWORD, db=DB_NAME)
    try:
        cursor = connection.cursor()
        try:
            # Commands
            SENTENCE = "SELECT uf.file_sent " + \
                        "FROM UserFile as uf " + \
                        "WHERE uf.id = %s "
            cursor.execute(SENTENCE, (file_id,))
            file_path = cursor.fetchone()[0]
        finally: 
            cursor.close()
    finally:
        connection.close()

    return open(_FILES_PATH + file_path).read()

def use(req, **kwargs):
    if 'use_id' not in kwargs:
        return "You need to provide use_id, being an ID of a use"

    try:
        use_id = int(kwargs['use_id'])
    except:
        return "You need to provide use_id, being an ID of a use"

    result = """<html><head><title>Use</title>
                <style type="text/css">
table
{
border-collapse:collapse;
}
table, td, th
{
border:1px solid;
}
td
{
padding:15px;
}

                </style></head><body>
                <h2>General</h2>
                <b>Login:</b> %(login)s<br/>
                <b>Name:</b> %(full_name)s<br/>
                <b>Experiment:</b> %(experiment_name)s@%(category_name)s<br/>
                <b>Date:</b> %(date)s<br/>
                <b>Origin:</b> %(origin)s<br/>
                <b>Device used:</b> %(device)s<br/>
                <b>Server IP (if federated):</b> %(ip)s<br/>
                <b>Use id:</b> %(use_id)s<br/>
                <b>Reservation id:</b> %(reservation_id)s<br/>
                <b>Mobile:</b> %(mobile)s<br/>
                <b>Facebook:</b> %(facebook)s<br/>
                <b>Referer:</b> %(referer)s<br/>
                <b>User agent:</b> %(user_agent)s<br/>
                <b>Route:</b> %(route)s</br/>
                <b>In the name of:</b> %(external_user)s<br/>
                <b>Longest command:</b> %(longest_command)s</br>
                <h2>Commands</h2>
                (<a href="#files">files below</a>)
                <table>
                <tr> <td><b>Time before</b></td> <td><b>Time after</b></td> <td><b>Command</b></td> <td><b>Response</b></td> </tr>
                """

    connection = dbi.connect(host="localhost",user=_USERNAME, passwd=_PASSWORD, db=DB_NAME)
    try:
        cursor = connection.cursor()
        try:
            SENTENCE = "SELECT u.login, u.full_name, e.name, c.name, uue.start_date, uue.origin, uue.reservation_id, uue.coord_address " + \
                        "FROM UserUsedExperiment as uue, User as u, Experiment as e, ExperimentCategory as c " + \
                        "WHERE u.id = uue.user_id AND e.id = uue.experiment_id AND e.category_id = c.id AND uue.id = %s "

            cursor.execute(SENTENCE, (use_id,))
            elements = cursor.fetchall()
            login, full_name, experiment_name, category_name, start_date, origin, reservation_id, device = elements[0]

            # Property values
            SENTENCE = "SELECT ep.name, epv.value " + \
                        "FROM UserUsedExperimentProperty as ep, UserUsedExperimentPropertyValue as epv " + \
                        "WHERE epv.experiment_use_id = %s AND epv.property_name_id = ep.id "
            cursor.execute(SENTENCE, (use_id,))
            elements = cursor.fetchall()
            properties = dict(elements)

            result = result % {
                        'use_id'          : use_id,
                        'mobile'          : cgi.escape(properties.get('mobile', "Don't know")).replace('%','%%'),
                        'facebook'        : cgi.escape(properties.get('facebook', "Don't know")).replace('%','%%'),
                        'referer'         : cgi.escape(properties.get('referer', "Don't know")).replace('%','%%'),
                        'user_agent'      : cgi.escape(properties.get('user_agent', "Don't know")).replace('%','%%'),
                        'external_user'   : cgi.escape(properties.get('external_user', "Himself")).replace('%','%%'),
                        'route'           : cgi.escape(properties.get('route', "Don't know")).replace('%','%%'),
                        'reservation_id'  : cgi.escape(reservation_id   or 'not stored').replace('%','%%'),
                        'login'           : cgi.escape(login            or 'not stored').replace('%','%%'),
                        'full_name'       : cgi.escape(full_name        or 'not stored').replace('%','%%'),
                        'experiment_name' : cgi.escape(experiment_name  or 'not stored').replace('%','%%'),
                        'category_name'   : cgi.escape(category_name    or 'not stored').replace('%','%%'),
                        'date'            : cgi.escape(str(start_date)).replace('%','%%'),
                        'origin'          : cgi.escape(origin           or 'not stored').replace('%','%%'),
                        'longest_command' : '%s',
                        'ip'              : cgi.escape(properties.get('from_direct_ip', "Don't know")).replace('%','%%'),
                        'device'          : cgi.escape(device           or 'not stored').replace('%','%%'),
                    }

            # Commands
            SENTENCE = "SELECT uc.command, uc.response, uc.timestamp_before, uc.timestamp_before_micro, uc.timestamp_after, uc.timestamp_after_micro " + \
                        "FROM UserCommand as uc " + \
                        "WHERE uc.experiment_use_id = %s "+ \
                        "ORDER BY uc.timestamp_before DESC LIMIT %s" % LIMIT
            cursor.execute(SENTENCE, (use_id,))
            elements = cursor.fetchall()
            command_results = ""
            max_time_taken = 0
            for command, response, timestamp_before, timestamp_before_micro, timestamp_after, timestamp_after_micro in elements:
                if timestamp_before is None:
                    before = "<not provided>"
                else:
                    before = "%s:%s" % (utc2local_str(timestamp_before), str(timestamp_before_micro).zfill(6))
                if timestamp_after is None:
                    after  = "<not provided>"
                else:
                    after  = "%s:%s" % (utc2local_str(timestamp_after), str(timestamp_after_micro).zfill(6))

                if timestamp_after is not None and timestamp_before is not None:
                    time_taken = timestamp_after.replace(microsecond=timestamp_after_micro) - timestamp_before.replace(microsecond=timestamp_before_micro)
                else:
                    time_taken = datetime.timedelta(0)
                current_seconds = time_taken.days * 24 * 3600 + time_taken.seconds + time_taken.microseconds * 1e-6
                if current_seconds > max_time_taken:
                    max_time_taken = current_seconds
                
                if command is None:
                    command = "(None)"
                if response is None:
                    response = "(None)"
                command_results += "\t<tr> <td> %s </td> <td> %s </td> <td> %s </td> <td> %s </td> </tr>\n" % ( before, after, cgi.escape(command).replace("%","%%"), cgi.escape(response).replace("%","%%") )
            result = (result % max_time_taken) + command_results

            result += """</table>\n"""
            result += """<br/><br/><a name="files"><h2>Files</h2>\n"""
            result += """<table>\n"""
            result += """<tr> <td><b>File hash</b></td> <td><b>File info</b></td> <td><b>Response</b></td> <td><b>Time before</b></td> <td><b>Time after</b></td> <td><b>link</b></td></tr>"""

            SENTENCE = "SELECT uf.id, uf.file_info, uf.file_hash, uf.response, uf.timestamp_before, uf.timestamp_before_micro, uf.timestamp_after, uf.timestamp_after_micro " + \
                        "FROM UserFile as uf " + \
                        "WHERE uf.experiment_use_id = %s "+ \
                        "ORDER BY uf.timestamp_before DESC LIMIT %s" % LIMIT
            cursor.execute(SENTENCE, (use_id,))
            elements = cursor.fetchall()
            for file_id, file_info, file_hash, response, timestamp_before, timestamp_before_micro, timestamp_after, timestamp_after_micro in elements:
                if timestamp_before is None:
                    before = "<not provided>"
                else:
                    before = "%s:%s" % (utc2local_str(timestamp_before), str(timestamp_before_micro).zfill(6))
                if timestamp_after is None:
                    after  = "<not provided>"
                else:
                    after  = "%s:%s" % (utc2local_str(timestamp_after), str(timestamp_after_micro).zfill(6))
                
                if file_hash is None:
                    file_hash = "(None)"
                if file_info is None:
                    file_info = "(None)"
                if response is None:
                    response = "(None)"
                result += "\t<tr> <td> %s </td> <td> %s </td> <td> %s </td> <td> %s </td> <td> %s </td> <td> <a href=\"file?file_id=%s\">link</a> </td> </tr>\n" % ( cgi.escape(file_hash), cgi.escape(file_info), cgi.escape(response), before, after, file_id )

        finally: 
            cursor.close()
    finally:
        connection.close()
    return result + """</table></body></html>"""

def user(req, login):
    connection = dbi.connect(host="localhost",user=_USERNAME, passwd=_PASSWORD, db=DB_NAME)
    try:
        cursor = connection.cursor()
        try:
            SENTENCE = "SELECT uue.id, u.login, u.full_name, e.name, c.name, uue.start_date, uue.origin " + \
                        "FROM UserUsedExperiment as uue, User as u, Experiment as e, ExperimentCategory as c " + \
                        "WHERE u.login = %s AND u.id = uue.user_id AND e.id = uue.experiment_id AND e.category_id = c.id " + \
                        "ORDER BY uue.start_date DESC LIMIT %s" % LIMIT
            cursor.execute(SENTENCE, (login,) )
            elements = [ list(row) for row in cursor.fetchall()]
            for row in elements:
                uue_id = row[0]
                origin = row[-1]
                SENTENCE = "SELECT uuepv.value " + \
                            "FROM UserUsedExperimentPropertyValue as uuepv, UserUsedExperimentProperty as uuep " + \
                            "WHERE uuepv.experiment_use_id = %s AND uuepv.property_name_id = uuep.id AND uuep.name = 'from_direct_ip'"
                cursor.execute(SENTENCE, uue_id)
                direct_ips = list(cursor.fetchall())
                if len(direct_ips) > 0:
                    direct_ip = direct_ips[0][0]
                    if direct_ip != origin:
                        row[-1] = '%s@%s' % (cgi.escape(origin), cgi.escape(direct_ip))

            result = """<html><head><title>Latest uses</title></head><body><table cellspacing="10">
                        <tr> <td><b>User</b></td> <td><b>Name</b></td> <td><b>Experiment</b></td> <td><b>Date</b></td> <td><b>From </b> </td> <td><b>Use</b></td></tr>
                        """
            for use_id, user_login, user_full_name, experiment_name, category_name, start_date, uue_from in elements:
                result += "\t<tr> <td> %s </td> <td> %s </td> <td> %s </td> <td> %s </td> <td> %s </td> <td> <a href=\"use?use_id=%s\">use</a> </td> </tr>\n" % ( user_login, user_full_name, experiment_name + '@' + category_name, utc2local_str(start_date), uue_from, use_id )
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
            elements = [ list(row) for row in cursor.fetchall()]
            for row in elements:
                uue_id = row[0]
                origin = row[-1]
                SENTENCE = "SELECT uuepv.value " + \
                            "FROM UserUsedExperimentPropertyValue as uuepv, UserUsedExperimentProperty as uuep " + \
                            "WHERE uuepv.experiment_use_id = %s AND uuepv.property_name_id = uuep.id AND uuep.name = 'from_direct_ip'"
                cursor.execute(SENTENCE, uue_id)
                direct_ips = list(cursor.fetchall())
                if len(direct_ips) > 0:
                    direct_ip = direct_ips[0][0]
                    if direct_ip != origin:
                        row[-1] = '%s@%s' % (cgi.escape(origin), cgi.escape(direct_ip))
                        SENTENCE = "SELECT uuepv.value " + \
                            "FROM UserUsedExperimentPropertyValue as uuepv, UserUsedExperimentProperty as uuep " + \
                            "WHERE uuepv.experiment_use_id = %s AND uuepv.property_name_id = uuep.id AND uuep.name = 'external_user'"
                        cursor.execute(SENTENCE, uue_id)
                        external_users = list(cursor.fetchall())
                        if len(external_users) > 0:
                            external_user = external_users[0][0]
                            row[1] = "%s@%s" % (cgi.escape(external_user), cgi.escape(row[1]))


            result = """<html><head><title>Latest uses</title></head><body><table cellspacing="10">
                        <tr> <td><b>User</b></td> <td><b>Name</b></td> <td><b>Experiment</b></td> <td><b>Date</b></td> <td><b>From </b> </td> <td><b>Use</b></td></tr>
                        """
            for use_id, user_login, user_full_name, experiment_name, category_name, start_date, uue_from in elements:
                result += "\t<tr> <td> <a href=\"uses.py/user?login=%s\">%s</a> </td> <td> %s </td> <td> %s </td> <td> %s </td> <td> %s </td> <td> <a href=\"uses.py/use?use_id=%s\">use</a> </td> </tr>\n" % ( user_login.split('@')[1] if '@' in user_login else user_login, user_login, user_full_name, experiment_name + '@' + category_name, utc2local_str(start_date), uue_from, use_id )
        finally: 
            cursor.close()
    finally:
        connection.close()
    return result + """</table></body></html>"""

