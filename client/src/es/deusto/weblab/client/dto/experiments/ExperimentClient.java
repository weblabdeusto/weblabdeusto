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

package es.deusto.weblab.client.dto.experiments;

import java.util.Map;
import java.util.Set;

import com.google.gwt.json.client.JSONValue;

public class ExperimentClient {
	private final String clientId;
	private final Map<String, JSONValue> configuration;
	
	public ExperimentClient(String clientId, Map<String, JSONValue> configuration) {
		this.clientId = clientId;
		this.configuration = configuration;
	}
	
	public String getClientId() {
		return this.clientId;
	}
	
	public Set<String> keySet() {
		return this.configuration.keySet();
	}
	
	public JSONValue get(String key) {
		return this.configuration.get(key);
	}
}
