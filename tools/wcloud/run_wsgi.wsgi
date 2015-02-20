#!/usr/bin/env python
import os
import sys

os.environ['http_proxy'] = 'http://proxy-s-priv.deusto.es:3128/'
os.environ['https_proxy'] = 'https://proxy-s-priv.deusto.es:3128/'

WCLOUD_DIR = os.path.dirname(__file__)
sys.path.insert(0, WCLOUD_DIR)
os.chdir(WCLOUD_DIR)

sys.stdout = open('stdout.txt', 'w', 0)
sys.stderr = open('stderr.txt', 'w', 0)

from wcloud import app as application

import logging
file_handler = logging.FileHandler(filename='errors.log')
file_handler.setLevel(logging.INFO)
application.logger.addHandler(file_handler)

