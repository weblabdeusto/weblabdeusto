#!/usr/bin/env python

import os
import sys

from dashboardserver import flask_app as app

sys.stdout = open('stdout.txt', 'w', 0)
sys.stderr = open('stderr.txt', 'w', 0)

import logging
file_handler = logging.FileHandler(filename='errors.log')
file_handler.setLevel(logging.INFO)
application.logger.addHandler(file_handler)