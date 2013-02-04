#!/usr/bin/env python
import os

os.environ['http_proxy'] = 'http://proxy-s-priv.deusto.es:3128/'
os.environ['https_proxy'] = 'https://proxy-s-priv.deusto.es:3128/'

import sys

os.environ['WCLOUD_SETTINGS'] = '/home/weblab/weblab/tools/wcloud/secret_settings.py'

class MyFile(file):
    def write(self, *args, **kwargs):
        out = file.write(self, *args, **kwargs)
        self.flush()
        return out

f = MyFile("/tmp/logs_wcloud", 'w')
sys.stdout = sys.stderr = f

WCLOUD_DIR = os.path.dirname(__file__)

sys.path.insert(0, WCLOUD_DIR)

activate_this = '/home/weblab/.virtualenvs/weblab/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

from wcloud import app as application
