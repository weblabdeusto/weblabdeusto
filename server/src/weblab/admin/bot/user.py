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
# Author: Jaime Irurzun <jaime.irurzun@gmail.com>
#         Pablo Orduña <pablo@ordunya.com>
#
from __future__ import print_function, unicode_literals

import sys

import time
import threading
import traceback

import voodoo.counter as counter

import weblab.data.command as Command
import weblab.core.reservations as Reservation
import weblab.experiment.util as _Util

import weblab.admin.bot.client as Client
import weblab.admin.bot.exc as Exceptions

class BotUser(threading.Thread):
    """ Abstract class, do not instance directly. """

    def __init__(self, url_maps, protocol, username, password, experiment_name, category_name, program, initial_delay):
        threading.Thread.__init__(self)
        self.setName(counter.next_name("BotUser"))
        self.url, self.url_login = url_maps[protocol]
        self.protocol = protocol
        self.username = username
        self.password = password
        self.experiment_name = experiment_name
        self.experiment_category_name = category_name
        self.program = _Util.serialize(program)
        self.bot = Client.create_bot(protocol, url=self.url, url_login=self.url_login)
        self.initial_delay = initial_delay

    def dispose(self):
        del self.bot

    def time(self):
        return self.bot.time()

    def get_number_of_exceptions(self):
        return self.bot.get_number_of_exceptions()

    def get_exceptions(self):
        return self.bot.get_exceptions()

    def get_calls(self):
        return self.bot.get_calls()

    def get_calls_by_name(self):
        return self.bot.get_calls_by_name()

    def get_log(self):
        return self.bot.get_log()

    def run(self):
        time.sleep(self.initial_delay)
        self.bot.start()
        try:
            try:
                self.run_user()
            except Exception:
                # TODO: do something with this
                traceback.print_exc()
        finally:
            weblabsessionid = self.bot.weblabsessionid
            if weblabsessionid.find('.') >= 0:
                self.route = weblabsessionid.split('.')[-1]
            else:
                self.route = '<unknown>'
            self.bot.finish()

    def __repr__(self):
        return "<BotUser type='%s' />" % self.__class__.__name__

class StandardBotUser(BotUser):

    #
    # The following two methods are implemented in the client
    #
    def _get_waiting_reservation_poll_time(self, position):
        # See WaitingInQueueReservationProcessor.getPollTime
        min_time = 1  # WebLabControllerImpl.DEFAULT_WAITING_MIN_POLL_TIME
        max_time = 10 # WebLabControllerImpl.DEFAULT_WAITING_MAX_POLL_TIME

        poll_time = (position + 1) * min_time
        if poll_time > max_time:
            return max_time
        else:
            return poll_time

    def _get_waiting_confirmation_poll_time(self):
        # See WebLabControllerImpl.DEFAULT_WAITING_CONFIRMATION_POLL_TIME
        return 1.2

    def run_user(self):
        self.bot.raise_exceptions = True
        self.bot.do_login(self.username, self.password)
        self.bot.do_get_user_information()
        experiments = self.bot.do_list_experiments()
        if experiments is not None:
            experiments_found = [ exp
                                    for exp in experiments
                                    if exp.name == self.experiment_name
                                        and exp.category.name == self.experiment_category_name
                            ]
            if len(experiments_found) > 0:
                reservation = self.bot.do_reserve_experiment(experiments_found[0].to_experiment_id(), "{}", "{}")
            else:
                raise Exceptions.ExperimentDoesNotExistError("Desired experiment doesn't exist: %s." % self.experiment_name)

            while isinstance(reservation, Reservation.WaitingReservation) or isinstance(reservation, Reservation.WaitingConfirmationReservation):
                if isinstance(reservation, Reservation.WaitingReservation):
                    time.sleep(self._get_waiting_reservation_poll_time(reservation.position))
                elif isinstance(reservation, Reservation.WaitingConfirmationReservation):
                    time.sleep(self._get_waiting_confirmation_poll_time())
                reservation = self.bot.do_get_reservation_status()
                sys.stdout.flush()

            if not isinstance(reservation, Reservation.ConfirmedReservation):
                exc = self.bot.calls[-1].exception
                raise Exceptions.UserAssertionError("At this point, it should be a ConfirmedReservation. Found: <%s>; <%s>" % (reservation, exc) )
            self.bot.do_send_file(self.program,"program")

            #for _ in xrange(10):
            self.bot.do_send_command(Command.Command("ChangeSwitch on 0"))

            self.bot.do_finished_experiment()
        self.bot.do_logout()

class DisconnectedBotUser(StandardBotUser):
    # TODO
    pass

class NotRespondingBotUser(StandardBotUser):
    # TODO
    pass
