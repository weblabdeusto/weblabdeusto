#!/usr/bin/env python

import sys
import time
import subprocess
import optparse
import shlex

# subprocess.check_output was not present in Python 2.6
def check_output(*cmd): 
    process = subprocess.Popen(stdout=subprocess.PIPE, *cmd)
    output, unused_err = process.communicate()
    retcode = process.poll()
    if retcode:
        raise Exception("Command %s returned %s" % (repr(cmd), retcode))
    return output

try:
    check_output(shlex.split('git --help'))
except:
    try:
        check_output(shlex.split('git.cmd --help'))
    except:
        print >> sys.stderr, "git command could not be run! Check your PATH"
        sys.exit(-1)
    else:
        git_command = 'git.cmd'
else:
    git_command = 'git'


def get_version():
    output = check_output([git_command,'--no-pager','show'])
    return output.split('\n')[0].split()[1].strip()

def get_number_of_versions(version):
    # git log 9bfcfb14afefd80473d4028c24f6b5019ebc3a5b --format="%h"
    cmd = shlex.split('%s --no-pager log %s --format="%%at"' % (git_command, version))
    output = check_output(cmd)
    lines = [ line for line in output.split('\n') ]
    timestamp = int(lines[0].strip().replace('"','').replace("'",''))
    date_str = time.strftime('%A, %B %d, %Y', time.localtime(timestamp))
    return len(lines), date_str

def generate(filename):
    version = get_version()
    number, date = get_number_of_versions(version)
    msg = r"""var wlVersionMessage = "WebLab-Deusto r<a href=\"https://github.com/weblabdeusto/weblabdeusto/commits/%(version)s\">%(version_number)s</a> | Last update: %(date)s";""" % {
        'version'         : version,
        'version_number'  : number,
        'date'            : date,
    }
    if filename == '-':
        print msg
    else:
        open(filename, 'w').write(msg)

if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option('-f','--file', dest='file', metavar='FILE', default=None, help='File where to write the code')
    options, args = parser.parse_args()
    if options.file is None:
        parser.error("FILE missing")
    else:
        generate(options.file)
