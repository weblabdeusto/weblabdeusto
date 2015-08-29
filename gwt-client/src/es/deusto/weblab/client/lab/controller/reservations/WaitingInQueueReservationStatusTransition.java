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
import es.deusto.weblab.client.lab.controller.ReservationStatusCallback;

public abstract class WaitingInQueueReservationStatusTransition extends GeneralWaitingReservationStatusTransition {

	public WaitingInQueueReservationStatusTransition(ReservationStatusCallback reservationStatusCallback) {
		super(reservationStatusCallback);
	}
	
	@Override
	protected int getPollTime(ReservationStatus reservationStatus) {
		final int position = this.getPosition(reservationStatus);
		final int pollTime = (position + 1) * this.getMinPollTime();
		if(pollTime > this.getMaxPollTime())
			return this.getMaxPollTime();
		else
			return pollTime;
	}
	
	protected abstract int getMinPollTime();
	protected abstract int getMaxPollTime();
	protected abstract int getPosition(ReservationStatus reservationStatus);	
}
