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

try:
	import bluetooth

	BT_name = 'linvor'
	BT_address = '00:12:02:09:05:16'
	BT_port = 1

	BT_socket = bluetooth.BluetoothSocket(bluetooth_RFCOMM)
	BT_socket.connect((BT_address, BT_port))

	BT_available = True
except:
	BT_available = False
	print 'No bluetooth device is available'

class RoMIE:
	def _wait_ack():
		received = ''
		while 'ACK' not in received and 'NAK' not in received:
			received += BT_socket.recv(1024)
		if 'NAK' in received:
			# TODO finish experiment
			pass

		return received

	def forward():
		BT_socket.send('F')
		response = wait_ack()

	def turn_left():
		BT_socket.send('L')
		response = wait_ack()

	def turn_right():
		BT_socket.send('F')
		response = wait_ack()

	def check_wall():
		BT_socket.send('S')
		response = wait_ack()

DEBUG = True

class RoMIExperiment(Experiment.Experiment):

	def __init__(self, coord_address, locator, cfg_manager, *args, **kwargs):
		super(RoMIExperiment, self).__init__(*args, **kwargs)
		self._cfg_manager = cfg_manager
		self.read_base_config()

	def read_base_config(self):
		"""
		Reads the base config parameters from the config file.
		"""
		pass

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

		self.romie = RoMIE();

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

		if command == 'F':
			self.romie.forward()
		elif command == 'L':
			self.romie.turn_left()
		elif command == 'R':
			self.romie.ruen_right()
		elif command == 'S':
			self.romie.check_wall()

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