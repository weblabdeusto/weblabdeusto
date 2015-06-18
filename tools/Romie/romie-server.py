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

# IF TAG: "Tag: 4F 00 56 87 C4 ACK"
# TODO check "S"'s return

try:
	import bluetooth

	BT_address = '00:12:02:09:05:16'
	BT_port = 1

	BT_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
	BT_socket.connect((BT_address, BT_port))

	BT_available = True
except:
 	BT_available = False
 	print 'No bluetooth device is available'

class RoMIE:
	def _wait_ack(self):
		if not BT_available: return

		received = ''
		while 'ACK' not in received and 'NAK' not in received:
			received += BT_socket.recv(1024)
		if 'NAK' in received:
			pass

		return received

	def forward(self):
		if not BT_available: return 'Bluetooth error'

		BT_socket.send('F')
		response = self._wait_ack()
		return response

	def turn_left(self):
		if not BT_available: return 'Bluetooth error'

		BT_socket.send('L')
		response = self._wait_ack()
		return response

	def turn_right(self):
		if not BT_available: return 'Bluetooth error'

		BT_socket.send('R')
		response = self._wait_ack()
		return response

	def check_wall(self):
		if not BT_available: return 'Bluetooth error'

		BT_socket.send('S')
		response = self._wait_ack()
		return response

import BaseHTTPServer
import urlparse

class RoMIEHandler(BaseHTTPServer.BaseHTTPRequestHandler):

	def __init__(self,req,client_addr,server):
		BaseHTTPServer.BaseHTTPRequestHandler.__init__(self,req,client_addr,server)

	def do_GET(self):
		parsedParams = urlparse.urlparse(self.path)
		queryParsed = urlparse.parse_qs(parsedParams.query)

		global romie;
		response = '';

		if parsedParams.path == "/l":
			response = romie.turn_left()
		elif parsedParams.path == "/r":
			response = romie.turn_right()
		elif parsedParams.path == "/f":
			response = romie.forward()
		elif parsedParams.path == "/s":
			response = romie.check_wall()

		if response is not '' or True:
			self.send_response(200)
			self.send_header('Content-Type', 'text/html')
			self.end_headers()
			self.wfile.write(response)

romie = RoMIE()
httpd = BaseHTTPServer.HTTPServer(('', 8000), RoMIEHandler)

print "RoMIE server listening"
httpd.serve_forever()
