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
package es.deusto.weblab.client.dto.reservations;

public class ConfirmedReservationStatus extends ReservationStatus {
	private int time;
	private String initialConfiguration;
	
	public ConfirmedReservationStatus(int time){
		this.time = time;
		this.initialConfiguration = null;
	}

	public ConfirmedReservationStatus(int time, String initialConfiguration){
		this.time = time;
		this.initialConfiguration = initialConfiguration;
	}

	public int getTime() {
		return this.time;
	}

	public void setTime(int time) {
		this.time = time;
	}
	
	public String getInitialConfiguration(){
		return this.initialConfiguration;
	}
	
	public void setInitialConfiguration(String initialConfiguration){
		this.initialConfiguration = initialConfiguration;
	}
}
