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
* Author: FILLME
*
*/

package es.deusto.weblab.client.dto.experiments;

import java.util.Date;

import es.deusto.weblab.client.dto.users.User;

public class ExperimentUse {
	private User user;
	private Experiment experiment;
	private Date startTimestamp;
	private Date endTimestamp;
	
	public ExperimentUse(User user, Experiment experiment, Date startTimestamp, Date endTimestamp) {
		super();
		this.user = user;
		this.experiment = experiment;
		this.startTimestamp = startTimestamp;
		this.endTimestamp = endTimestamp;
	}
	
	public User getUser() {
		return this.user;
	}
	public void setUser(User user) {
		this.user = user;
	}
	public Experiment getExperiment() {
		return this.experiment;
	}
	public void setExperiment(Experiment experiment) {
		this.experiment = experiment;
	}
	public Date getStartTimestamp() {
		return this.startTimestamp;
	}
	public void setStartTimestamp(Date startTimestamp) {
		this.startTimestamp = startTimestamp;
	}
	public Date getEndTimestamp() {
		return this.endTimestamp;
	}
	public void setEndTimestamp(Date endTimestamp) {
		this.endTimestamp = endTimestamp;
	}
}
