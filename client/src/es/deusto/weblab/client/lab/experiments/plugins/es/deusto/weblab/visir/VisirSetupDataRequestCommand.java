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
* Author: Luis Rodriguez Gil <luis.rodriguez@opendeusto.es>
*
*/

package es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.visir;

import com.google.gwt.json.client.JSONObject;
import com.google.gwt.json.client.JSONParser;
import com.google.gwt.json.client.JSONString;
import com.google.gwt.json.client.JSONValue;

import es.deusto.weblab.client.dto.experiments.Command;

/**
 * Command to request the setup data to the Visir experiment server.
 * This data includes the cookie which will be used to initialise a session,
 * the URL with the VISIR client and the circuit's savedata, which defines the
 * palette for a given experiment.
 */
public class VisirSetupDataRequestCommand extends Command {

	private String cookie;
	private String saveData;
	private String url;
	
	public String getCookie() { return this.cookie;  }
	public String getSaveData() { return this.saveData; }
	public String getURL() { return this.url; }

	/**
	 * Parses the response, storing the received parameters for them
	 * to be retrieved through various getters.
	 * @param response Response that was received
	 * @return true if the response was successfully parsed, false otherwise
	 */
	public boolean parseResponse(String response) {
		
		try {
		
			final JSONValue val = JSONParser.parseStrict(response);
			final JSONObject obj = val.isObject();
			if(obj == null)
				return false;
			
			final JSONValue cookieval = obj.get("cookie");
			final JSONValue savedataval = obj.get("savedata");
			final JSONValue urlval = obj.get("url");
			
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
			
		} catch(Throwable e) {
			return false;
		}
		
		return true;
	}
	
	
	@Override
	public String getCommandString() {
		return "GIVE_ME_SETUP_DATA";
	}
}
