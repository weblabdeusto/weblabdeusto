import os
import sys
import time
import traceback
import subprocess
from flask import Flask, request

sys.path.append('.')

import wcloud.deploymentsettings as deploymentsettings
import wcloud.config.wcloud_settings_default as wcloud_settings_default
import wcloud.config.wcloud_settings as wcloud_settings

app = Flask(__name__)


app.config.from_object(wcloud_settings_default)
app.config.from_object(wcloud_settings)
app.config.from_envvar('WCLOUD_SETTINGS', silent=True)

FILENAME = os.path.join(app.config['DIR_BASE'], 'instances.txt')


def wait_process(process):
    print "Waiting for process to start...",
    time_to_wait = app.config.get('WEBLAB_STARTUP_TIME', 15)
    time.sleep(time_to_wait)
    print "[done]"
    if process.poll() is not None: 
        raise Exception("Error seconds after the system was not running")

def start_weblab(dirname, wait):
    print "Deploying instance: %s" % dirname, 
    process = subprocess.Popen(['nohup','weblab-admin', 'start', dirname],
                stdout = open(os.path.join(dirname, 'stdout.txt'), 'w'),
                stderr = open(os.path.join(dirname, 'stderr.txt'), 'w'),
                stdin  = subprocess.PIPE)
    print "[done]"
    if wait:
        wait_process(process)
    return process



@app.route('/deployments/', methods=['POST','GET'])
def add_deployment():
    try:
        if request.method == 'POST':
            name = request.json['name']
            dirname = os.path.join(app.config['DIR_BASE'], name)
            contents = open(FILENAME).read()
            contents += '\n%s\n' % dirname
            open(FILENAME, 'w').write(contents)
            start_weblab(dirname, True)
            return "Added"
        else:
            print FILENAME
            contents = open(FILENAME).read()
            return contents
    except:
        traceback.print_exc()
        raise


@app.route('/deployments/<name>', methods=['DELETE'])
def manage_deployment(name):
    lines = [ line for line in open(FILENAME).readlines() if '/%s/' % name not in line ]
    open(FILENAME, 'w').writelines(lines)
    return "Removed"


@app.route('/')
def index():
    return "This is the service for managing deployments. Whenever this service loads, it starts all the services. It also listens in a port so as to add or remove deployments"

def main():
    dir_base = app.config['DIR_BASE']
    if not os.path.exists(dir_base):
        os.mkdir(dir_base)
        open(FILENAME, 'w').write("")
        apache_conf_file = os.path.join(dir_base, deploymentsettings.APACHE_CONF_NAME)
        open(apache_conf_file, 'w').write("")
        print "Note: WebLab-Deusto configuration directory (%s) created. Make sure %s is included in the Apache configuration" % (dir_base, apache_conf_file)


    with open(FILENAME) as f:
        for line in f:
            # Start now the WebLab-Deusto instance
            line = line.split('#')[0].strip()
            if line:
                start_weblab(line, False)

if __name__ == '__main__':
    main()
    app.run(debug = False, port = app.config['WEBLAB_STARTER_PORT'], host = '127.0.0.1')
