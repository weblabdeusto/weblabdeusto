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
* Author: Pablo Orduña <pablo@ordunya.com>
*
*/ 
package es.deusto.weblab.client.dto.experiments;

public class ExperimentAllowed {
	private Experiment experiment;
	private int timeAllowed;
	
	public ExperimentAllowed(){}
	
	public ExperimentAllowed(Experiment experiment, int timeAllowed){
		this.experiment = experiment;
		this.timeAllowed = timeAllowed;
	}

	public Experiment getExperiment() {
		return this.experiment;
	}

	public void setExperiment(Experiment experiment) {
		this.experiment = experiment;
	}

	public int getTimeAllowed() {
		return this.timeAllowed;
	}

	public void setTimeAllowed(int timeAllowed) {
		this.timeAllowed = timeAllowed;
	}
}
