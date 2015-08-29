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

public class ConfirmedReservationStatus extends ReservationStatus {
	private int time;
	private String initialConfiguration;
	private String url;
	private String remoteReservationId;
	
	public ConfirmedReservationStatus(String reservationId, int time){
		super(reservationId);
		this.time = time;
		this.initialConfiguration = null;
		this.url = "";
		this.remoteReservationId = "";
	}

	public ConfirmedReservationStatus(String reservationId, int time, String initialConfiguration, String url, String remoteReservationId){
		super(reservationId);
		this.time = time;
		this.initialConfiguration = initialConfiguration;
		this.url = url;
		this.remoteReservationId = remoteReservationId;
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
	
	public String getUrl(){
		return this.url;
	}
	
	public void setUrl(String url){
		this.url = url;
	}
	
	public String getRemoteReservationId(){
		return this.remoteReservationId;
	}
	
	public void setRemoteReservationId(String remoteReservationId){
		this.remoteReservationId = remoteReservationId;
	}
	
	public boolean isRemote(){
		return this.remoteReservationId != null && this.remoteReservationId.length() != 0;
	}
	
	public boolean isLocal(){
		return !isRemote();
	}
}
