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

import java.util.HashMap;
import java.util.Map;

import com.google.gwt.json.client.JSONObject;
import com.google.gwt.json.client.JSONString;

public class Status {
	
	private final double temperature;
	private final int size;
	private final Map<String, Boolean> lights = new HashMap<String, Boolean>();
	
	public Status(JSONObject status) {
		this.temperature = status.get("temp").isNumber().doubleValue();
		
		int counter = 0;
		for(String key : status.keySet()) {
			final JSONString value = status.get(key).isString();
			if(value == null)
				continue;
			
			this.lights.put(key, value.stringValue().equals("on"));
			if(key.length() == 1 && Character.isDigit(key.charAt(0)))
				counter++;
		}
		
		this.size = counter;
	}
	
	public boolean isLightOn(String pos) {
		return this.lights.get(pos).booleanValue();
	}
	
	public int getSize() {
		return this.size;
	}
	
	public double getTemperature() {
		return this.temperature;
	}
}
