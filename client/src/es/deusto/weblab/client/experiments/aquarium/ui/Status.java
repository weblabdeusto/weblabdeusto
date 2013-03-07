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

package es.deusto.weblab.client.experiments.aquarium.ui;

import java.util.HashMap;
import java.util.Map;

import com.google.gwt.json.client.JSONObject;
import com.google.gwt.json.client.JSONParser;
import com.google.gwt.user.client.Window;

public class Status {
	
	private final Map<Color, Boolean> data = new HashMap<Color, Boolean>();
	
	public Status(JSONObject obj) {
		for(String name : obj.keySet()) {
			final Color color;
			try {
				color = Color.valueOf(name);
			} catch(Exception e) {
				Window.alert("Invalid color; contact administrator: " + name);
				continue;
			}
			
			this.data.put(color, Boolean.valueOf(obj.get(name).isBoolean().booleanValue()));
		}
	}
	
	public Status(String initialConfiguration) {
		this(JSONParser.parseStrict(initialConfiguration).isObject());
	}
	
	public Boolean getColor(Color color) {
		return this.data.get(color);
	}
}
