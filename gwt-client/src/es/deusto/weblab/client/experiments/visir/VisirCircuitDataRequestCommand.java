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
 * Command to request a specific circuit to the Visir experiment server.
 * The name of that circuit must be known and the circuit must be available.
 * (Currently, the available list of circuits is provided on experiment startup):
 */
public class VisirCircuitDataRequestCommand extends Command {

	private String circuitName;
	
	
	/**
	 * Creates the VisirCircuitDataRequestCommand.
	 * @param circuitName Name of the circuit whose data will be requested.
	 */
	public VisirCircuitDataRequestCommand(String circuitName) {
		this.circuitName = circuitName;
	}
	

	
	/**
	 * Retrieves the name of the circuit.
	 * @return Circuit name.
	 */
	public String getCircuitName() {
		return this.circuitName;
	}

	@Override
	public String getCommandString() {
		return "GIVE_ME_CIRCUIT_DATA " + this.getCircuitName();
	}
}
