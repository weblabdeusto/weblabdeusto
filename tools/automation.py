#!/usr/bin/env python

"""
This script only reserves a laboratory, submits a command, and checks a result. You may adapt it 
if you want to test how a laboratory you have made performs. For instance, if you have a motor or 
so and you are not sure if it can go up and down 100 times, you want to verify that by modifying 
and running this code.
"""

import sys
import time

from weblab.core.reservations import Reservation
from weblab.core.coordinator.clients.weblabdeusto import WebLabDeustoClient
from weblab.data.command import Command
from weblab.data.experiments import ExperimentId

URL = "http://www.weblab.deusto.es/weblab/"
USERNAME = "porduna"
PASSWORD = ""
EXP_ID = ExperimentId("robot-movement", "Robot experiments")
N = 50

weblab      = WebLabDeustoClient( URL )
session_id  = weblab.login(USERNAME, PASSWORD)

for n in xrange(N):
    print "Reserving (%s)..." % n,
    sys.stdout.flush()
    reservation = weblab.reserve_experiment(session_id, EXP_ID, "{}", "{}")

    while reservation.status in (Reservation.WAITING_CONFIRMATION or Reservation.WAITING):
        time.sleep(1)
        reservation = weblab.get_reservation_status( reservation.reservation_id )
        print ".",
        sys.stdout.flush()

    if reservation.status != Reservation.CONFIRMED:
        raise Exception("Confirmed reservation expected for reservation_id (%r). Found status: %r" % (reservation.reservation_id, reservation.status))

    print "[done]"
    sys.stdout.flush()

    print "Confirmed reservation, programming file..."
    sys.stdout.flush()

    reservation_id = reservation.reservation_id

    # 
    # This code here is Robot dependent. Replace it with your code to check it.
    # 
    response = weblab.send_command(reservation_id, Command("program:Interactive Demo"))

    if response == 'File sended & running':
        print "File programmed. Exiting."
        sys.stdout.flush()

    weblab.finished_experiment(reservation_id)

print "Finished testing %s times" % N
