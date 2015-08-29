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

//Strategy pattern
public abstract class ReservationStatusTransition {
	protected ReservationStatusCallback reservationStatusCallback;

	public ReservationStatusTransition(ReservationStatusCallback reservationStatusCallback){
		this.reservationStatusCallback = reservationStatusCallback;
	}

	public abstract void perform(ReservationStatus reservationStatus);
}
