#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2005 onwards University of Deusto
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#
# This software consists of contributions made by many individuals,
# listed below:
#
# Author: Iban Eguia <iban.eguia@opendeusto.es>
#

import weblab.experiment.experiment as Experiment

from voodoo.override import Override
from voodoo.log import logged

import urllib2
import json
import random
import sqlite3

DEBUG = True
ROMIE_SERVER = "http://192.168.0.190:8000/"

class RoMIExperiment(Experiment.Experiment):

	def __init__(self, coord_address, locator, cfg_manager, *args, **kwargs):
		super(RoMIExperiment, self).__init__(*args, **kwargs)
		self._cfg_manager = cfg_manager
		self.read_base_config()

	def read_base_config(self):
		"""
		Reads the base config parameters from the config file.
		"""

		self.database = self._cfg_manager.get_value('romie_sqlite')
		self.questions = self._cfg_manager.get_value('questions')

	@Override(Experiment.Experiment)
	@logged("info")
	def do_get_api(self):
		return "2"

	@Override(Experiment.Experiment)
	@logged("info")
	def do_start_experiment(self, client_initial_data, server_initial_data):
		"""
		Callback run when the experiment is started.
		"""
		if(DEBUG):
			print "[RoMIE] do_start_experiment called"

		data = json.loads(server_initial_data)
		self.username = data['request.username']

		return ""

	@Override(Experiment.Experiment)
	@logged("info")
	def do_send_command_to_device(self, command):
		"""
		Callback run when the client sends a command to the experiment
		@param command Command sent by the client, as a string.
		"""
		if(DEBUG):
			print "[RoMIE] Command received: %s" % command

		global ROMIE_SERVER

		if command == 'F':
			return urllib2.urlopen("%sf" % ROMIE_SERVER).read()
		elif command == 'L':
			return urllib2.urlopen("%sl" % ROMIE_SERVER).read()
		elif command == 'R':
			return urllib2.urlopen("%sr" % ROMIE_SERVER).read()
		elif command.startswith("QUESTION"):

			command = command.split()

			difficulty = int(command[1])

			questions = self.questions[difficulty];
			question_nr =random.randint(0, len(questions)-1)
			question = questions[question_nr]

			response_question = {
				'index': question_nr,
				'difficulty': difficulty,
				'question': question['question'],
				'answers': question['answers'],
				'points': question['points'],
				'time': question['time']
			}

			return json.dumps(response_question)

		elif command.startswith("ANSWER"):

			command = command.split()

			response = int(command[1])
			difficulty = int(command[2])
			question = int(command[3])

			return self.questions[difficulty][question]['correct'] == response

		elif command.startswith("FINISH"):
			command = command.split()

			conn = sqlite3.connect(self.database)
			conn.execute("UPDATE forotech SET points = ? WHERE username = ?", (command[1], self.username,))
			conn.commit()
			conn.close()

			return 'OK' #TODO return JSON of best 10
		elif command == 'CHECK_REGISTER':
			conn = sqlite3.connect(self.database)
			cur = conn.cursor()

			cur.execute("SELECT COUNT(*) FROM forotech WHERE username = ?", (self.username,));
			count = cur.fetchone()[0]

			result = ''
			if count == 0:
				result = 'REGISTER'

			conn.close()

			return result
		elif command.startswith('REGISTER'):
			data = json.loads(command.split()[1])

			conn = sqlite3.connect(self.database)
			conn.execute("INSERT INTO forotech values (?,?,?,?,?,?,?)",
				(self.username, data["name"], data["surname"], data["school"], data["bdate"], data["email"], 0,))
			conn.commit()
			conn.close()

			return 'OK'

		return "OK"

	@Override(Experiment.Experiment)
	@logged("info")
	def do_dispose(self):
		"""
		Callback to perform cleaning after the experiment ends.
		"""
		if(DEBUG):
			print "[RoMIE] do_dispose called"

		return "OK"