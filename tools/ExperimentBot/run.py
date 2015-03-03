
from weblab.core.coordinator.clients.weblabdeusto import WebLabDeustoClient
import os
import time
from weblab.core.reservations import WaitingReservation, ConfirmedReservation, WaitingConfirmationReservation
from weblab.data.command import Command
from weblab.data.experiments import ExperimentId

import threading

import config

threads = {}

users_in = 0

def user_t():
    do_full_experiment_use()


def main():

    print "Starting all threads... "
    for i in range(config.NUM_USERS):
        t = threading.Thread(None, user_t)
        threads[t] = t
        t.start()
    print " done."

    while True:
        print "Users in the experiment: %d" % users_in
        time.sleep(5)

        for t in threads.values():
            if t.is_alive(): break
        else:
            break

    print "GOING OUT."


def do_full_experiment_use():
    """
    Uses the configured experiment trying to resemble the way a human would do it.
    This method will block for a while.
    :return:
    """
    wc = WebLabDeustoClient(config.WEBLAB_BASE_URL)
    sessionid = wc.login(config.LOGIN, config.PASSWORD)
    if not sessionid: raise Exception("Wrong login")

    # Reserve the flash dummy experiment.
    experiment_id = ExperimentId(config.EXP_NAME, config.EXP_CATEGORY)
    waiting = wc.reserve_experiment(sessionid, experiment_id, "{}", "{}", None)
    # print "Reserve response: %r" % waiting

    reservation_id = waiting.reservation_id

    while True:
        status = wc.get_reservation_status(reservation_id)
        # print "Reservation status: %r" % status

        if type(status) is WaitingReservation:
            time.sleep(0.5)
        elif type(status) is ConfirmedReservation:
            break
        elif type(status) is WaitingConfirmationReservation:
            time.sleep(0.5)
        else:
            print "Unknown reservation status."

    print "Experiment reserved."

    global users_in
    users_in += 1

    # Send some commands.

    for i in range(config.COMMANDS_PER_USER):
        # What's commandstring actually for??
        cmd = Command(config.COMMAND)
        result = wc.send_command(reservation_id, cmd)
        if not result.commandstring.startswith("Received command"):
            raise Exception("Unrecognized command response")
        # print "Command result: %r" % result
        time.sleep(config.TIME_BETWEEN_COMMANDS)

    users_in -= 1

    result = wc.logout(sessionid)
    print "Logout result: %r" % result


if __name__ == '__main__':
    main()