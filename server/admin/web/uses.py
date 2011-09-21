import MySQLdb as dbi
import cgi
import time
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

    result = """<html><head><title>Use</title></head><body>
                <h2>General</h2>
                <b>Use id:</b> %(use_id)s<br/>
                <b>Mobile:</b> %(mobile)s<br/>
                <b>Facebook:</b> %(mobile)s<br/>
                <b>User agent:</b> %(user_agent)s<br/>
                <h2>Commands</h2>
                (<a href="#files">files below</a>)
                <table cellspacing="20">
                <tr> <td><b>Command</b></td> <td><b>Response</b></td> <td><b>Time before</b></td> <td><b>Time after</b></td></tr>
                """

    connection = dbi.connect(host="localhost",user=_USERNAME, passwd=_PASSWORD, db=DB_NAME)
    try:
        cursor = connection.cursor()
        try:
            # Property values
            SENTENCE = "SELECT ep.name, epv.value " + \
                        "FROM UserUsedExperimentProperty as ep, UserUsedExperimentPropertyValue as epv " + \
                        "WHERE epv.experiment_use_id = %s AND epv.property_name_id = ep.id "
            cursor.execute(SENTENCE, (use_id,))
            elements = cursor.fetchall()
            properties = dict(elements)

            result = result % {
                        'use_id'     : use_id,
                        'mobile'     : cgi.escape(properties.get('mobile', "Don't know")),
                        'facebook'   : cgi.escape(properties.get('facebook', "Don't know")),
                        'user_agent' : cgi.escape(properties.get('user_agent', "Don't know")),
                    }

            # Commands
            SENTENCE = "SELECT uc.command, uc.response, uc.timestamp_before, uc.timestamp_before_micro, uc.timestamp_after, uc.timestamp_after_micro " + \
                        "FROM UserCommand as uc " + \
                        "WHERE uc.experiment_use_id = %s "+ \
                        "ORDER BY uc.timestamp_before DESC LIMIT %s" % LIMIT
            cursor.execute(SENTENCE, (use_id,))
            elements = cursor.fetchall()
            for command, response, timestamp_before, timestamp_before_micro, timestamp_after, timestamp_after_micro in elements:
                if timestamp_before is None:
                    before = "<not provided>"
                else:
                    before = "%s:%s" % (timestamp_before.strftime("%d/%m/%y %H:%M:%S"), str(timestamp_before_micro).zfill(6))
                if timestamp_after is None:
                    after  = "<not provided>"
                else:
                    after  = "%s:%s" % (timestamp_after.strftime("%d/%m/%y %H:%M:%S"), str(timestamp_after_micro).zfill(6))
                
                if command is None:
                    command = "(None)"
                if response is None:
                    response = "(None)"
                result += "\t<tr> <td> %s </td> <td> %s </td> <td> %s </td> <td> %s </td> </tr>\n" % ( cgi.escape(command), cgi.escape(response), before, after )

            result += """</table>\n"""
            result += """<br/><br/><a name="files"><h2>Files</h2>\n"""
            result += """<table cellspacing="20">\n"""
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
                    before = "%s:%s" % (timestamp_before.strftime("%d/%m/%y %H:%M:%S"), str(timestamp_before_micro).zfill(6))
                if timestamp_after is None:
                    after  = "<not provided>"
                else:
                    after  = "%s:%s" % (timestamp_after.strftime("%d/%m/%y %H:%M:%S"), str(timestamp_after_micro).zfill(6))
                
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

