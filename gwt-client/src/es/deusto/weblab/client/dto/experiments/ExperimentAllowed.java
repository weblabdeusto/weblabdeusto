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
* Author: Pablo Orduña <pablo@ordunya.com>
*
*/ 
package es.deusto.weblab.client.dto.experiments;

public class ExperimentAllowed implements Comparable<ExperimentAllowed> {
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

	@Override
	public int hashCode() {
		final int prime = 31;
		int result = 1;
		result = prime * result
				+ ((this.experiment == null) ? 0 : this.experiment.hashCode());
		result = prime * result + this.timeAllowed;
		return result;
	}

	@Override
	public boolean equals(Object obj) {
		if (this == obj)
			return true;
		if (obj == null)
			return false;
		if (getClass() != obj.getClass())
			return false;
		ExperimentAllowed other = (ExperimentAllowed) obj;
		if (this.experiment == null) {
			if (other.experiment != null)
				return false;
		} else if (!this.experiment.equals(other.experiment))
			return false;
		if (this.timeAllowed != other.timeAllowed)
			return false;
		return true;
	}
	
	@Override
	public String toString() {
		return "ExperimentAllowed [experiment=" + this.experiment
				+ ", timeAllowed=" + this.timeAllowed + "]";
	}

	@Override
	public int compareTo(ExperimentAllowed other) {
		if(this.experiment.getExperimentUniqueName().equals(other.experiment.getExperimentUniqueName()))
			return this.timeAllowed - other.timeAllowed;
		
		return this.experiment.getUniqueName().compareTo(other.experiment.getUniqueName());
	}
}
