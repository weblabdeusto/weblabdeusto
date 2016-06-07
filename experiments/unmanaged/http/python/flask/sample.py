#!/usr/local/bin python
#-*-*- encoding: utf-8 -*-*-

import json
import random
import datetime

from flask import Flask, request, url_for, redirect, jsonify, Response

app = Flask(__name__)
app.config['WEBLAB_USERNAME'] = 'admin'
app.config['WEBLAB_PASSWORD'] = 'password'

###############################
# 
# Store in DATA dictionaries 
# representing users.
# 
DATA = {
}

##################################
# 
# Store in EXPIRED_DATA, expired
# addresses pointing to their
# previous URLs
# 
EXPIRED_DATA = {
}

#####################################
# 
# Main method. Authorized users
# come here directly, with a secret
# which is their identifier. This
# should be stored in a Redis or 
# SQL database.
#
@app.route('/lab/<session_id>/')
def index(session_id):
    data = DATA.get(session_id, None)
    if data is None:
        back_url = EXPIRED_DATA.get(session_id, None)
        if back_url is None:
            return "Session identifier not found"
        else:
            return redirect(back_url)
            
    
    data['last_poll'] = datetime.datetime.now()
    return """<html>
    <head>
        <meta http-equiv="refresh" content="10">
    </head>
    <body>
        Hi %(username)s. You still have %(seconds)s seconds
    </body>
    </head>
    """ % dict(username=data['username'], seconds=(data['max_date'] - datetime.datetime.now()).seconds)

def get_json():
    # Retrieve the submitted JSON
    if request.data:
        data = request.data
    else:
        keys = request.form.keys() or ['']
        data = keys[0]
    return json.loads(data)


#############################################################
# 
# WebLab-Deusto API:
# 
# First, this method creates new sessions. We store the 
# sessions on memory in this dummy example.
#

def check_http_credentials(testing=False):
    auth = request.authorization
    if auth:
        username = auth.username
        password = auth.password
    else:
        username = password = "No credentials"

    weblab_username = app.config['WEBLAB_USERNAME']
    weblab_password = app.config['WEBLAB_PASSWORD']
    if username != weblab_username or password != weblab_password:
        if testing:
            return Response(json.dumps(dict(valid=False, error_messages=["Invalid credentials"])), status=401, headers = {'WWW-Authenticate':'Basic realm="Login Required"', 'Content-Type': 'application/json'})

        print("In theory this is weblab. However, it provided as credentials: {} : {}".format(username, password))
        return Response(response=("You don't seem to be a WebLab-Instance"), status=401, headers = {'WWW-Authenticate':'Basic realm="Login Required"'})
    
    return None

@app.route("/foo/weblab/sessions/api")
def api_version():
    return jsonify(api_version="1")

@app.route("/foo/weblab/sessions/test")
def test():
    response = check_http_credentials(testing=True)
    if response is not None:
        return response
    return jsonify(valid=True)

@app.route("/foo/weblab/sessions/", methods=['POST'])
def start_experiment():
    response = check_http_credentials()
    if response is not None:
        return response

    # Parse it: it is a JSON file containing two fields:
    request_data = get_json()

    client_initial_data = request_data['client_initial_data']
    server_initial_data = request_data['server_initial_data']

    print server_initial_data

    # Parse the initial date + assigned time to know the maximum time
    start_date_str = server_initial_data['priority.queue.slot.start']
    start_date_str, microseconds = start_date_str.split('.')
    start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d %H:%M:%S") + datetime.timedelta(microseconds = int(microseconds))
    max_date = start_date + datetime.timedelta(seconds = float(server_initial_data['priority.queue.slot.length']))

    # Create a global session
    session_id = str(random.randint(0, 10e8)) # Not especially secure 0:-)
    DATA[session_id] = {
        'username'  : server_initial_data['request.username'],
        'max_date'  : max_date,
        'last_poll' : datetime.datetime.now(),
        'back'      : request_data['back']
    }

    link = url_for('index', session_id=session_id, _external = True)
    print "Assigned session_id: %s" % session_id
    print "See:",link
    return jsonify(url=link, session_id=session_id)

#############################################################
# 
# WebLab-Deusto API:
# 
# This method provides the current status of a particular 
# user.
# 
@app.route('/foo/weblab/sessions/<session_id>/status')
def status(session_id):
    response = check_http_credentials()
    if response is not None:
        return response

    data = DATA.get(session_id, None)
    if data is not None:
        print "Did not poll in", datetime.datetime.now() - data['last_poll'], "seconds"
        print "User %s still has %s seconds" % (data['username'], (data['max_date'] - datetime.datetime.now()).seconds)
        if (datetime.datetime.now() - data['last_poll']).seconds > 30:
            print "Kick out the user, please"
            return jsonify(should_finish=-1)
            
    print "Ask in 10 seconds..."
    # 
    # If the user is considered expired here, we can return -1 instead of 10. 
    # The WebLab-Deusto scheduler will mark it as finished and will reassign
    # other user.
    # 
    return jsonify(should_finish=10)


#############################################################
# 
# WebLab-Deusto API:
# 
# This method is called to kick one user out. This may happen
# when an administrator defines so, or when the assigned time
# is over.
# 
@app.route('/foo/weblab/sessions/<session_id>', methods=['POST'])
def dispose_experiment(session_id):
    response = check_http_credentials()
    if response is not None:
        return response

    request_data = get_json()
    if 'action' in request_data and request_data['action'] == 'delete':
        if session_id in DATA:
            data = DATA.pop(session_id, None)
            if data is not None:
                EXPIRED_DATA[session_id] = data['back']
            return jsonify(message='Deleted')
        return jsonify(message='Not found')
    return jsonify(message='Unknown action')

if __name__ == "__main__":
    app.run(debug=True, host = '0.0.0.0')
