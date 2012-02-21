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
* Author: Jaime Irurzun <jaime.irurzun@gmail.com>
*
*/

package es.deusto.weblab.client.dto.experiments;

import java.util.Date;

import es.deusto.weblab.client.dto.users.Agent;

public class ExperimentUse {
	
	private int id;
	private Date startDate;
	private Date endDate;
	private Experiment experiment;
	private Agent agent;
	private String origin;
	
	public ExperimentUse() {}
	
	public ExperimentUse(Date startDate, Date endDate, Agent agent, Experiment experiment, String origin) {
		this.agent = agent;
		this.experiment = experiment;
		this.startDate = startDate;
		this.endDate = endDate;
		this.origin = origin;
	}
		
	public int getId() {
		return this.id;
	}
	public void setId(int id) {
		this.id = id;
	}
	public Date getStartDate() {
		return this.startDate;
	}
	public void setStartDate(Date startDate) {
		this.startDate = startDate;
	}
	public Date getEndDate() {
		return this.endDate;
	}
	public void setEndDate(Date endDate) {
		this.endDate = endDate;
	}
	public void setExperiment(Experiment experiment) {
		this.experiment = experiment;
	}
	public Experiment getExperiment() {
		return this.experiment;
	}
	public String getOrigin() {
		return this.origin;
	}
	public void setOrigin(String origin) {
		this.origin = origin;
	}
	public void setAgent(Agent agent) {
		this.agent = agent;
	}
	public Agent getAgent() {
		return this.agent;
	}
}
