#!/usr/bin/env python
#-*-*- encoding: utf-8 -*-*-
#
# Copyright (C) 2005-2009 University of Deusto
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#
# This software consists of contributions made by many individuals, 
# listed below:
#
# Author: Pablo Orduña <pablo@ordunya.com>
# 

class MetaScheduler(object):
    def query_best_reservation_status(self, schedulers, reservation_id):
        if len(schedulers) == 0:
            raise ValueError("There must be at least one scheduler, zero provided!")

        all_reservation_status = []
        for scheduler in schedulers:
            reservation_status = scheduler.get_reservation_status(reservation_id)
            all_reservation_status.append(reservation_status)
        return self.select_best_reservation_status(all_reservation_status)

    def select_best_reservation_status(self, all_reservation_status):
        if len(all_reservation_status) == 0:
            raise ValueError("There must be at least one reservation status, zero provided!")

        all_reservation_status.sort()
        return all_reservation_status[0]

