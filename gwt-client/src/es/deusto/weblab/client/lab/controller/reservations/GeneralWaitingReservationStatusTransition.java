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
import es.deusto.weblab.client.lab.controller.LabController.IControllerRunnable;
import es.deusto.weblab.client.lab.controller.ReservationStatusCallback;

public abstract class GeneralWaitingReservationStatusTransition extends ReservationStatusTransition {

	public GeneralWaitingReservationStatusTransition(ReservationStatusCallback reservationStatusCallback) {
		super(reservationStatusCallback);
	}
	
	protected abstract int getPollTime(ReservationStatus reservationStatus);
	protected abstract void showReservation(ReservationStatus reservationStatus);
	
	@Override
	public void perform(ReservationStatus reservationStatus) {
		this.reservationStatusCallback.getController().setReservationId(reservationStatus.getReservationId());
		
		this.showReservation(reservationStatus);
		final int pollTime = this.getPollTime(reservationStatus);
		this.reservationStatusCallback.getTimerCreator().createTimer(pollTime, new IControllerRunnable(){
			@Override
			public void run() {
				GeneralWaitingReservationStatusTransition.this.reservationStatusCallback.getCommunications().getReservationStatus(
						GeneralWaitingReservationStatusTransition.this.reservationStatusCallback.getController().getReservationId(), 
						GeneralWaitingReservationStatusTransition.this.reservationStatusCallback
					);
			}
		});
		this.reservationStatusCallback.getPollingHandler().start();
	}
}
