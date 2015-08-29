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

public class PostReservationReservationStatus extends ReservationStatus {
	private boolean finished;
	private String initialData;
	private String endData;
	
	public PostReservationReservationStatus(String reservationId, boolean finished, String initialData, String endData) {
		super(reservationId);
		
		this.finished = finished;
		this.initialData = initialData;
		this.endData = endData;
	}

	/**
	 * @return the finished
	 */
	public boolean isFinished() {
		return this.finished;
	}

	/**
	 * @param finished the finished to set
	 */
	public void setFinished(boolean finished) {
		this.finished = finished;
	}

	/**
	 * @return the initialData
	 */
	public String getInitialData() {
		return this.initialData;
	}

	/**
	 * @param initialData the initialData to set
	 */
	public void setInitialData(String initialData) {
		this.initialData = initialData;
	}

	/**
	 * @return the endData
	 */
	public String getEndData() {
		return this.endData;
	}

	/**
	 * @param endData the endData to set
	 */
	public void setEndData(String endData) {
		this.endData = endData;
	}
}
