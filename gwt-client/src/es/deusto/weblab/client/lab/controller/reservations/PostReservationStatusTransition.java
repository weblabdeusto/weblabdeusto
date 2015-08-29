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
import es.deusto.weblab.client.dto.reservations.PostReservationReservationStatus;
import es.deusto.weblab.client.dto.reservations.ReservationStatus;
import es.deusto.weblab.client.lab.controller.ReservationStatusCallback;
import es.deusto.weblab.client.lab.experiments.exceptions.ExperimentException;

public class PostReservationStatusTransition extends ReservationStatusTransition{

	public PostReservationStatusTransition(ReservationStatusCallback reservationStatusCallback) {
		super(reservationStatusCallback);
	}

	@Override
	public void perform(ReservationStatus reservationStatus) {
		this.reservationStatusCallback.getController().setReservationId(reservationStatus.getReservationId());

		final ExperimentID experimentID = this.reservationStatusCallback.getExperimentBeingReserved();
		try {
			this.reservationStatusCallback.getUimanager().onExperimentReserved(
					experimentID,
					this.reservationStatusCallback.getExperimentBaseBeingReserved()
				);
		} catch (ExperimentException e) {
			this.reservationStatusCallback.getUimanager().onError(e.getMessage());
			return;
		}
		
		final String initialData = ((PostReservationReservationStatus)reservationStatus).getInitialData();
		final String endData = ((PostReservationReservationStatus)reservationStatus).getEndData();
		this.reservationStatusCallback.getExperimentBaseBeingReserved().postEndWrapper(initialData, endData);
	}
}
