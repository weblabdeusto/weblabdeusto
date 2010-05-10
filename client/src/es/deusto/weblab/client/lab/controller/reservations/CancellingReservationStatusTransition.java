/*
* Copyright (C) 2005-2009 University of Deusto
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

public class CancellingReservationStatusTransition extends ReservationStatusTransition{

	public CancellingReservationStatusTransition(ReservationStatusCallback reservationStatusCallback) {
		super(reservationStatusCallback);
	}

	@Override
	public void perform(ReservationStatus reservationStatus) {
		this.reservationStatusCallback.getUimanager().onErrorAndFinishReservation("Cancelling reservation received");
	}
}
