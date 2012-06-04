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

package es.deusto.weblab.client.experiments.visir;


import java.util.ArrayList;
import java.util.List;

import com.google.gwt.json.client.JSONArray;
import com.google.gwt.json.client.JSONObject;
import com.google.gwt.json.client.JSONParser;
import com.google.gwt.json.client.JSONString;
import com.google.gwt.json.client.JSONValue;

import es.deusto.weblab.client.dto.experiments.Command;

/**
 * Command to request a specific circuit to the Visir experiment server.
 * The name of that circuit must be known and the circuit must be available.
 * (Currently, the available list of circuits is provided on experiment startup):
 */
public class VisirPublishedCircuitsRequestCommand extends Command {
	
	List<String> publishedCircuits; 
	
	/**
	 * Creates the VisirPublishedCircuitsRequestCommand
	 */
	public VisirPublishedCircuitsRequestCommand() {
	
	}
	
	@Override
	public String getCommandString() {
		return "GIVE_ME_PUBLISHED_CIRCUITS";
	}
	
	/**
	 * Retrieves the list of published circuits, after the command response
	 * is successfully parsed.
	 * @return List with the circuit names.
	 * @see parseData
	 */
	public List<String> getPublishedCircuits() {
		return this.publishedCircuits;
	}
	
	/**
	 * Parses the JSON containing the circuit names. Important to remark that it only contains
	 * the NAMES. Hence, to obtain the actual circuit data, it will be necessary to request it
	 * separatedly.
	 * @param response Response that was received
	 * @return true if the response was successfully parsed, false otherwise
	 */
	public boolean parseData(String response) {
		
		try {
		
			final JSONValue val = JSONParser.parseStrict(response);
			final JSONObject obj = val.isObject();
			if(obj == null)
				return false;
			
			final JSONValue circuitsList = obj.get("circuits");
			

			// We will now parse the list of available circuits. This is a list containing
			// the names of available circuits. Their actual data is not included and needs to 
			// be requested separatedly.
			this.publishedCircuits = new ArrayList<String>();
			if(circuitsList == null) {
			} else {
				JSONArray circuitsAvailableArray = circuitsList.isArray();
				
				for( int i = 0 ; i < circuitsAvailableArray.size(); ++i ) {
					final JSONValue circuitName = circuitsAvailableArray.get(i);
					final String circuitNameStr = circuitName.isString().stringValue();
					this.publishedCircuits.add(circuitNameStr);
				}
			}
			
		} catch(Throwable e) {
			return false;
		}
		
		return true;
	}
	
}
