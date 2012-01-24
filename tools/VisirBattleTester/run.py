#!/usr/local/env python

import time
import sys, os
import json

sys.path.append(os.sep.join(('..','..','server','src')))

import libraries
import visir_commands

from weblab.core.reservations import Reservation
from weblab.core.coordinator.clients.weblabdeusto import WebLabDeustoClient
from weblab.data.command import Command
from weblab.data.experiments import ExperimentId

weblab      = WebLabDeustoClient("http://www.weblab.deusto.es/weblab/")
session_id  = weblab.login("tester", "t3st3r6")
reservation = weblab.reserve_experiment(session_id, ExperimentId("visir", "Visir experiments"), "{}", "{}")

while reservation.status in (Reservation.WAITING_CONFIRMATION or Reservation.WAITING):
    time.sleep(1)
    reservation = weblab.get_reservation_status( reservation.reservation_id )

if reservation.status != Reservation.CONFIRMED:
    raise Exception("Confirmed reservation expected for reservation_id (%r). Found status: %r" % (reservation.reservation_id, reservation.status))

reservation_id = reservation.reservation_id

response = weblab.send_command(reservation_id, Command("GIVE_ME_SETUP_DATA"))
cookie   = json.loads(response.commandstring)['cookie']

login_response = weblab.send_command(reservation_id, Command(visir_commands.visir_login_request % cookie))

visir_sessionid = visir_commands.parse_login_response(login_response)

response = weblab.send_command(reservation_id, Command(visir_commands.visir_request_11k % visir_sessionid))
print visir_commands.parse_command_response(response)


response = weblab.send_command(reservation_id, Command(visir_commands.visir_request_900 % visir_sessionid))
print visir_commands.parse_command_response(response)

response = weblab.send_command(reservation_id, Command(visir_commands.visir_request_1k % visir_sessionid))
print visir_commands.parse_command_response(response)


response = weblab.send_command(reservation_id, Command(visir_commands.visir_request_10k % visir_sessionid))
print visir_commands.parse_command_response(response)

weblab.finished_experiment(reservation_id)

