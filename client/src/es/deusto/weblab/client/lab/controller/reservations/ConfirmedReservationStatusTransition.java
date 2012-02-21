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

import es.deusto.weblab.client.dto.experiments.ExperimentID;
import es.deusto.weblab.client.dto.reservations.ConfirmedReservationStatus;
import es.deusto.weblab.client.dto.reservations.ReservationStatus;
import es.deusto.weblab.client.lab.controller.ReservationStatusCallback;
import es.deusto.weblab.client.lab.experiments.exceptions.ExperimentException;

public class ConfirmedReservationStatusTransition extends ReservationStatusTransition{
	public ConfirmedReservationStatusTransition(ReservationStatusCallback reservationStatusCallback) {
		super(reservationStatusCallback);
	}

	@Override
	public void perform(final ReservationStatus reservationStatus) {
		this.reservationStatusCallback.getController().setReservationId(reservationStatus.getReservationId());

		
		this.reservationStatusCallback.getPollingHandler().start();
		
		final ConfirmedReservationStatus confirmedStatus = (ConfirmedReservationStatus)reservationStatus;
		if(confirmedStatus.isLocal()){
			final ExperimentID experimentID = this.reservationStatusCallback.getExperimentBeingReserved();
			try {
				this.reservationStatusCallback.getUimanager().onExperimentReserved(
						experimentID,
						this.reservationStatusCallback.getExperimentBaseBeingReserved()
					);
				this.reservationStatusCallback.getExperimentBaseBeingReserved().start(confirmedStatus.getTime(), confirmedStatus.getInitialConfiguration());
				this.reservationStatusCallback.getExperimentBaseBeingReserved().setTime(confirmedStatus.getTime());
			} catch (final ExperimentException e) {
				this.reservationStatusCallback.getUimanager().onError(e.getMessage());
				return;
			}	
		}else{
			this.reservationStatusCallback.getUimanager().onRemoteExperimentReserved(confirmedStatus.getUrl(), confirmedStatus.getRemoteReservationId());
		}
	}
}
