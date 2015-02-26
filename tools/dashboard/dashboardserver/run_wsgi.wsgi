#!/usr/bin/env python

import os
import sys

from dashboardserver import flask_app as app


DASHBOARD_DIR = os.path.dirname(__file__)
if DASHBOARD_DIR == '':
    DASHBOARD_DIR = os.path.abspath('.')

sys.path.insert(0, DASHBOARD_DIR)
os.chdir(DASHBOARD_DIR)

sys.stdout = open('stdout.txt', 'w', 0)
sys.stderr = open('stderr.txt', 'w', 0)

import logging
file_handler = logging.FileHandler(filename='errors.log')
file_handler.setLevel(logging.INFO)
application.logger.addHandler(file_handler)