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

package es.deusto.weblab.client.lab.experiments;


public interface IHasExperimentParameters {
	public ExperimentParameter [] getParameters();
	
	// Typical parameters
	public static final ExperimentParameterDefault WEBCAM_REFRESH_TIME = new ExperimentParameterDefault("webcam.refresh.millis", "Time to refresh the webcam image,  in milliseconds", 200);
}
