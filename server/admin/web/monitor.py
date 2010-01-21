import os
import subprocess
from configuration import DIRECTORY

def index(req):
    os.chdir(DIRECTORY)
    p = subprocess.Popen("python Monitor.py -a -f", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out = p.stdout.read()
    err = p.stderr.read()
    return """<html><head><title>Monitor</title></head><body><br><br><b>stdout:</b><br><pre>%s</pre><br><br><b>stderr:</b><br><pre>%s</pre></body></html>""" % (out, err)
