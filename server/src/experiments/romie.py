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

		self.questions = {}
		general_question_file = self._cfg_manager.get_value("general_questions")
		self.questions['general'] = json.loads(open(general_question_file).read())

	@Override(Experiment.Experiment)
	@logged("info")
	def do_get_api(self):
		return "2"

	@Override(Experiment.Experiment)
	@logged("info")
	def do_start_experiment(self, *args, **kwargs):
		"""
		Callback run when the experiment is started.
		"""
		if(DEBUG):
			print "[RoMIE] do_start_experiment called"

		return ""

	@Override(Experiment.Experiment)
	@logged("info")
	def do_send_command_to_device(self, command):
		"""
		Callback run when the client sends a command to the experiment
		@param command Command sent by the client, as a string.
		"""
		if(DEBUG):
			print "[RoMIE] do_send_command_to_device called"

		global ROMIE_SERVER

		if command == 'F':
			return urllib2.urlopen("%sf" % ROMIE_SERVER).read()
		elif command == 'L':
			return urllib2.urlopen("%sl" % ROMIE_SERVER).read()
		elif command == 'R':
			return urllib2.urlopen("%sr" % ROMIE_SERVER).read()
		elif command.startswith("QUESTION"):
			difficulty = int(command[9])
			category = command[11:]

			questions = self.questions[category][difficulty];
			question_nr =random.randint(0, len(questions)-1)
			question = questions[question_nr]

			response_question = {
				'question_nr': question_nr,
				'question': question['question'],
				'answers': question['answers']
			}

			return json.dumps(response_question)

		elif command.startswith("RESPONSE"):

			response = int(command[9])
			difficulty = int(command[11])
			question = int(command[13:command.index('|')-1])
			category = command[command.index('|')+2:]

			return self.questions[category][difficulty][question]['correct'] == response

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