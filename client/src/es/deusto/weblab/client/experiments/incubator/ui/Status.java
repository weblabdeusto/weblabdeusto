/*
* Copyright (C) 2012 onwards University of Deusto
* All rights reserved.
*
* This software is licensed as described in the file COPYING, which
* you should have received as part of this distribution.
*
* This software consists of contributions made by many individuals, 
* listed below:
*
* Author: FILLME
*
*/

package es.deusto.weblab.client.experiments.incubator.ui;

import com.google.gwt.json.client.JSONObject;

public class Status {
	
	private final double temperature;
	private final int size;
	private final int lightsOn; // Mask based
	
	public Status(JSONObject status) {
		this.temperature = status.get("temp").isNumber().doubleValue();
		
		int mask = 0;
		int counter = 0;
		for(String key : status.keySet()) {
			if(key.length() == 1 && Character.isDigit(key.charAt(0))) { // We'll never have more than 9 cameras
				counter++;
				final int pos = Integer.parseInt(key) - 1;
				if(status.get(key).isString().equals("on")) 
					mask |= 1 << pos;
			}
		}
		
		this.size = counter;
		this.lightsOn = mask;
	}
	
	public boolean isLightOn(int pos) {
		return (this.lightsOn & (1 << pos)) == 0;
	}
	
	public int getSize() {
		return this.size;
	}
	
	public double getTemperature() {
		return this.temperature;
	}
}
