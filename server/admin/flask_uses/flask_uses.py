
from flask import *


import MySQLdb as dbi
import cgi
import time
import calendar

from configuration import _USERNAME, _PASSWORD, DB_NAME, _FILES_PATH

LIMIT   = 150


app = Flask(__name__)
app.debug = True

import libraries


def utc2local_str(utc_datetime, format="%Y-%m-%d %H:%M:%S"):
    return time.strftime(format, time.localtime(calendar.timegm(utc_datetime.timetuple())))

@app.route("/uses/file/<int:file_id>")
def file(file_id):
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

@app.route("/uses/use/<int:use_id>")
def use(use_id):
    result = ""
    
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

            use = {
                        'use_id'          : use_id,
                        'mobile'          : cgi.escape(properties.get('mobile', "Don't know")),
                        'facebook'        : cgi.escape(properties.get('facebook', "Don't know")),
                        'referer'         : cgi.escape(properties.get('referer', "Don't know")),
                        'user_agent'      : cgi.escape(properties.get('user_agent', "Don't know")),
                        'external_user'   : cgi.escape(properties.get('external_user', "Himself")),
                        'route'           : cgi.escape(properties.get('route', "Don't know")),
                        'reservation_id'  : cgi.escape(reservation_id   or 'not stored'),
                        'login'           : cgi.escape(login            or 'not stored'),
                        'full_name'       : cgi.escape(full_name        or 'not stored'),
                        'experiment_name' : cgi.escape(experiment_name  or 'not stored'),
                        'category_name'   : cgi.escape(category_name    or 'not stored'),
                        'date'            : cgi.escape(str(start_date)),
                        'origin'          : cgi.escape(origin           or 'not stored'),
                        'ip'              : cgi.escape(properties.get('from_direct_ip', "Don't know")),
                        'device'          : cgi.escape(device           or 'not stored'),
                    }

            # Commands
            SENTENCE = "SELECT uc.command, uc.response, uc.timestamp_before, uc.timestamp_before_micro, uc.timestamp_after, uc.timestamp_after_micro " + \
                        "FROM UserCommand as uc " + \
                        "WHERE uc.experiment_use_id = %s "+ \
                        "ORDER BY uc.timestamp_before DESC LIMIT %s" % LIMIT
            cursor.execute(SENTENCE, (use_id,))
            elements = cursor.fetchall()
            commands = []
            for command, response, timestamp_before, timestamp_before_micro, timestamp_after, timestamp_after_micro in elements:
                if timestamp_before is None:
                    before = "<not provided>"
                else:
                    before = "%s:%s" % (utc2local_str(timestamp_before), str(timestamp_before_micro).zfill(6))
                if timestamp_after is None:
                    after  = "<not provided>"
                else:
                    after  = "%s:%s" % (utc2local_str(timestamp_after), str(timestamp_after_micro).zfill(6))
                
                if command is None:
                    command = "(None)"
                if response is None:
                    response = "(None)"
                    
                commands.append( (before, after, cgi.escape(command), cgi.escape(response),) )

            SENTENCE = "SELECT uf.id, uf.file_info, uf.file_hash, uf.response, uf.timestamp_before, uf.timestamp_before_micro, uf.timestamp_after, uf.timestamp_after_micro " + \
                        "FROM UserFile as uf " + \
                        "WHERE uf.experiment_use_id = %s "+ \
                        "ORDER BY uf.timestamp_before DESC LIMIT %s" % LIMIT
            cursor.execute(SENTENCE, (use_id,))
            
            files = []
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
                    
                print "YES"
                    
                files.append((cgi.escape(file_hash), cgi.escape(file_info), cgi.escape(response), before, after, url_for('file', file_id=file_id),))
               
            html = render_template('use.html', use=use, commands=commands, files=files)

        finally: 
            cursor.close()
    finally:
        connection.close()
    return html

@app.route('/uses/user/<login>')
def user(login):
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

            elements_to_display = []
            for use_id, user_login, user_full_name, experiment_name, category_name, start_date, uue_from in elements:
                login = (user_login.split('@')[1] if '@' in user_login else user_login)
                use_url = url_for('use', use_id = use_id)
                start_date = utc2local_str(start_date)
                elements_to_display.append( (use_id, user_login, user_full_name, experiment_name, category_name, start_date, uue_from, login, None, use_url) )

            html = render_template('uses.html', elements = elements_to_display)
        finally: 
            cursor.close()
    finally:
        connection.close()
    return html

 
@app.route('/test')
def tindex():
    return render_template('uses.html', hello="Hello world")

@app.route('/uses')
def index():
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
            elements_to_display = []
            for use_id, user_login, user_full_name, experiment_name, category_name, start_date, uue_from in elements:
                login = (user_login.split('@')[1] if '@' in user_login else user_login)
                user_url = url_for('user', login = login)
                use_url = url_for('use', use_id = use_id)
                start_date = utc2local_str(start_date)
                elements_to_display.append( (use_id, user_login, user_full_name, experiment_name, category_name, start_date, uue_from, login, user_url, use_url) )

            html = render_template('uses.html', elements = elements_to_display)
        
        finally: 
            cursor.close()
    finally:
        connection.close()
        
    return html



if __name__ == "__main__":
    app.run(port=11000)