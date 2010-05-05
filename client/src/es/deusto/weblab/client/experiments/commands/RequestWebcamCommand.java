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
* Author: Luis Rodríguez <luis.rodriguez@opendeusto.es>
*
*/ 
package es.deusto.weblab.client.experiments.commands;

import es.deusto.weblab.client.dto.experiments.Command;

public class RequestWebcamCommand extends Command{
	
	public RequestWebcamCommand(){

	}
	
	@Override
	public String getCommandString() {
		return "WEBCAMURL"; 
	}
	
	/**
	 * Retrieves the webcam URL from the response to the RequestWebcam command.
	 * Note: The webcam request command follows the following format:
	 * WEBCAMURL=http://www.whatever/webcam
	 * 
	 * @param requestResponse String containing the response to the command
	 * @return Webcam URL. Null if the string can't be parsed.
	 */
	public static String retrieveWebcamURL(String requestResponse) {
		final int eqsign = requestResponse.indexOf("=");
		if(eqsign == -1)
			return null;
		String url = requestResponse.substring(eqsign+1);
		return url;
	}
	
	
}
