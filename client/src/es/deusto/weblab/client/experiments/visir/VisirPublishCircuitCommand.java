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


import es.deusto.weblab.client.dto.experiments.Command;

/**
 * Command to publish the current circuit.
 */
public class VisirPublishCircuitCommand extends Command {
	
	// Data provided for the request itself.
	private String circuitData;
	
	// Data parsed from the response to the request.
	private String assignedCircuitName;
	
	/**
	 * Creates the VisirPublishCircuitCommand
	 */
	public VisirPublishCircuitCommand(String circuitData) {
		this.circuitData = circuitData;
	}
	
	@Override
	/**
	 * Retrieves the command string to send to the server.
	 * It will have the following format:
	 * PUBLISH_CIRCUIT <circuit_data>
	 * <circuit_data> will the the XML describing the circuit, with no quotes.
	 * It is noteworthy that the name of the circuit is NOT specified. It will be
	 * assigned by the server and returned as a response.
	 */
	public String getCommandString() {
		return "PUBLISH_CIRCUIT" + " " + this.circuitData;
	}
	
	/**
	 * Parses the response. Particularly, it will retrieve the circuit name
	 * assigned by the server. After parsing through this method, this name
	 * might be obtained through getAssignedCircuitName.
	 * @return True if the response was successfully parsed, 
	 * false otherwise. 
	 * @see getAssignedCircuitName
	 */
	public boolean parseResponse(String response) {
		// For now, the format of the response is simply the following:
		// <assigned_circuit_name>
		this.assignedCircuitName = response;
		return true;
	}
	
	
	/**
	 * Obtains the assigned circuit name. That is, the name that the server automatically
	 * assigns to the published circuit. Before this name is available, the command must
	 * have been issued and its response parsed through parseResponse.
	 * @see parseResponse
	 */
	public String getAssignedCircuitName() {
		return this.assignedCircuitName;
	}
		
}
