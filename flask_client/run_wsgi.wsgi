#!/usr/bin/env python

import os
import sys

WEBLABCLIENT_DIR = os.path.dirname(__file__)

sys.path.insert(0, WEBLABCLIENT_DIR)
os.chdir(WEBLABCLIENT_DIR)

sys.stdout = open('stdout.txt', 'w', 0)
sys.stderr = open('stderr.txt', 'w', 0)


from flaskclient import flask_app
flask_app.config.from_object('config')
flask_app.config["DEBUG"] = False;

import logging
file_handler = logging.FileHandler(filename='errors.log')
file_handler.setLevel(logging.INFO)
flask_app.logger.addHandler(file_handler)
