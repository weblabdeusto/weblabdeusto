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

import es.deusto.weblab.client.dto.reservations.PostReservationReservationStatus;
import es.deusto.weblab.client.dto.reservations.ReservationStatus;
import es.deusto.weblab.client.lab.controller.ReservationStatusCallback;

public class PostReservationStatusTransition extends ReservationStatusTransition{

	public PostReservationStatusTransition(ReservationStatusCallback reservationStatusCallback) {
		super(reservationStatusCallback);
	}

	@Override
	public void perform(ReservationStatus reservationStatus) {
		// TODO
		System.out.println("POST RESERVATION STATUS TRANSITION");
		System.out.println("Initial: " + ((PostReservationReservationStatus)reservationStatus).getInitialData());
		System.out.println("End: " + ((PostReservationReservationStatus)reservationStatus).getEndData());
	}
}
