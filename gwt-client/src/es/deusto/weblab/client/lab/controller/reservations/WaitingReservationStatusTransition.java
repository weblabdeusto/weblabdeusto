/*
* Copyright (C) 2005 onwards University of Deusto
* All rights reserved.
*
* This software is licensed as described in the file COPYING, which
* you should have received as part of this distribution.
*
* This software consists of contributions made by many individuals, 
* listed below:
*
* Author: Pablo Orduña <pablo@ordunya.com>
*
*/ 
package es.deusto.weblab.client.lab.controller.reservations;

import es.deusto.weblab.client.dto.reservations.ReservationStatus;
import es.deusto.weblab.client.dto.reservations.WaitingReservationStatus;
import es.deusto.weblab.client.lab.controller.ReservationStatusCallback;
import es.deusto.weblab.client.lab.controller.LabController;

public class WaitingReservationStatusTransition extends WaitingInQueueReservationStatusTransition {

	public WaitingReservationStatusTransition(ReservationStatusCallback reservationStatusCallback) {
		super(reservationStatusCallback);
	}

	@Override
	protected int getMinPollTime() {
		return this.reservationStatusCallback.getConfigurationManager().getIntProperty(
				LabController.WAITING_MIN_POLLING_TIME_PROPERTY, 
				LabController.DEFAULT_WAITING_MIN_POLLING_TIME
			);
	}

	@Override
	protected int getMaxPollTime() {
		return this.reservationStatusCallback.getConfigurationManager().getIntProperty(
				LabController.WAITING_MAX_POLLING_TIME_PROPERTY, 
				LabController.DEFAULT_WAITING_MAX_POLLING_TIME
			);
	}

	@Override
	protected void showReservation(ReservationStatus reservationStatus) {
		this.reservationStatusCallback.getUimanager().onWaitingReservation(
				(WaitingReservationStatus)reservationStatus
			);
	}

	@Override
	protected int getPosition(ReservationStatus reservationStatus) {
		return ((WaitingReservationStatus)reservationStatus).getPosition();
	}
}
