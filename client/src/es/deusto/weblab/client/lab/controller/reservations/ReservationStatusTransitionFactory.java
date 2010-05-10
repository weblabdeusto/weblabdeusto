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
 * Author: Jaime Irurzun <jaime.irurzun@gmail.com>
 *
 */

package es.deusto.weblab.client.lab.controller.reservations;

import es.deusto.weblab.client.dto.reservations.CancellingReservationStatus;
import es.deusto.weblab.client.dto.reservations.ConfirmedReservationStatus;
import es.deusto.weblab.client.dto.reservations.ReservationStatus;
import es.deusto.weblab.client.dto.reservations.WaitingConfirmationReservationStatus;
import es.deusto.weblab.client.dto.reservations.WaitingInstancesReservationStatus;
import es.deusto.weblab.client.dto.reservations.WaitingReservationStatus;
import es.deusto.weblab.client.lab.controller.ReservationStatusCallback;
import es.deusto.weblab.client.lab.controller.exceptions.WlUnknownReservationException;

public class ReservationStatusTransitionFactory {

    public static ReservationStatusTransition create(
	    ReservationStatus reservationStatus,
	    ReservationStatusCallback reservationStatusCallback)
	    throws WlUnknownReservationException {

	if (ReservationStatusTransitionFactory.isWaiting(reservationStatus)) {
	    return new WaitingReservationStatusTransition(reservationStatusCallback);
	} else if (ReservationStatusTransitionFactory.isWaitingConfirmation(reservationStatus)) {
	    return new WaitingConfirmationReservationStatusTransition(reservationStatusCallback);
	} else if (ReservationStatusTransitionFactory.isWaitingInstances(reservationStatus)) {
	    return new WaitingInstancesReservationStatusTransition(reservationStatusCallback);
	} else if (ReservationStatusTransitionFactory.isConfirmed(reservationStatus)) {
	    return new ConfirmedReservationStatusTransition(reservationStatusCallback);
	} else if (ReservationStatusTransitionFactory.isCancelling(reservationStatus)) {
	    return new CancellingReservationStatusTransition(reservationStatusCallback);
	} else {
	    throw new WlUnknownReservationException(
		    "Couldn't process the following reservation: "
			    + reservationStatus);
	}
    }

    private static boolean isWaiting(ReservationStatus reservationStatus) {
	return reservationStatus instanceof WaitingReservationStatus;
    }

    private static boolean isConfirmed(ReservationStatus reservationStatus) {
	return reservationStatus instanceof ConfirmedReservationStatus;
    }

    private static boolean isCancelling(ReservationStatus reservationStatus) {
	return reservationStatus instanceof CancellingReservationStatus;
    }

    private static boolean isWaitingConfirmation(ReservationStatus reservationStatus) {
	return reservationStatus instanceof WaitingConfirmationReservationStatus;
    }

    private static boolean isWaitingInstances(ReservationStatus reservationStatus) {
	return reservationStatus instanceof WaitingInstancesReservationStatus;
    }
}