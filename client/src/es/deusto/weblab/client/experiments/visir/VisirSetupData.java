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
* Author: Luis Rodriguez Gil <luis.rodriguez@opendeusto.es>
*
*/

package es.deusto.weblab.client.experiments.visir;

import java.util.ArrayList;
import java.util.List;

import com.google.gwt.json.client.JSONArray;
import com.google.gwt.json.client.JSONBoolean;
import com.google.gwt.json.client.JSONObject;
import com.google.gwt.json.client.JSONParser;
import com.google.gwt.json.client.JSONString;
import com.google.gwt.json.client.JSONValue;

/**
 * Request which defines the initial configuration data passed to the VISIR experiment.
 * This used to be a command on its own, but is now passed as the initial configuration
 * of the experiment, using the new weblab API.
 * This data includes the cookie which will be used to initialise a session,
 * the URL with the VISIR client and the circuit's savedata, which defines the
 * palette for a given experiment.
 */
public class VisirSetupData {

	private String cookie;
	private String saveData;
	private String url;
	private boolean teacher;
	
	private List<String> circuitsAvailable;
	
	public List<String> getCircuitsAvailable() {
		return this.circuitsAvailable;
	}
	
	public String getCookie() { 
		return this.cookie;  
	}
	
	public String getSaveData() { 
		return this.saveData; 
	}
	
	public String getURL() { 
		return this.url; 
	}
	
	public boolean isTeacher() {
		return this.teacher;
	}

	/**
	 * Parses the string, storing the received parameters for them
	 * to be retrieved through various getters.
	 * @param response Response that was received
	 * @return true if the response was successfully parsed, false otherwise
	 */
	public boolean parseData(String response) {
		
		try {
		
			final JSONValue val = JSONParser.parseStrict(response);
			final JSONObject obj = val.isObject();
			if(obj == null)
				return false;
			
			final JSONValue cookieval   = obj.get("cookie");
			final JSONValue savedataval = obj.get("savedata");
			final JSONValue urlval      = obj.get("url");
			final JSONValue teacherval  = obj.get("teacher"); 
			
			final JSONValue circuitsList = obj.get("circuits");
			
			if( cookieval == null || savedataval == null || urlval == null)
				return false;
			
			final JSONString cookiestr = cookieval.isString();
			final JSONString savedatastr = savedataval.isString();
			final JSONString urlstr = urlval.isString();
			
			if(cookiestr == null || savedatastr == null || urlstr == null)
				return false;
			
			this.cookie = cookiestr.stringValue();
			this.saveData = savedatastr.stringValue();
			this.url = urlstr.stringValue();
			
			if(teacherval != null){
				JSONBoolean teacherbool = teacherval.isBoolean();
				this.teacher = teacherbool != null && teacherbool.booleanValue();
			}else
				this.teacher = false;
			
			// We will now parse the list of available circuits. This is a list containing
			// the names of available circuits. Their actual data is not included and needs to 
			// be requested separatedly.
			this.circuitsAvailable = new ArrayList<String>();
			if(circuitsList == null) {
			} else {
				JSONArray circuitsAvailableArray = circuitsList.isArray();
				
				for( int i = 0 ; i < circuitsAvailableArray.size(); ++i ) {
					final JSONValue circuitName = circuitsAvailableArray.get(i);
					final String circuitNameStr = circuitName.isString().stringValue();
					this.circuitsAvailable.add(circuitNameStr);
				}
			}
			
		} catch(Throwable e) {
			return false;
		}
		
		return true;
	}
	
}
