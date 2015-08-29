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
package es.deusto.weblab.client.dto.reservations;

public class WaitingInstancesReservationStatus extends ReservationStatus {
	private int position;
	
	public WaitingInstancesReservationStatus(String reservationId){
		super(reservationId);
	}
	
	public WaitingInstancesReservationStatus(String reservationId, int position){
		super(reservationId);
		this.position = position;
	}

	public int getPosition() {
		return this.position;
	}

	public void setPosition(int position) {
		this.position = position;
	}
}
