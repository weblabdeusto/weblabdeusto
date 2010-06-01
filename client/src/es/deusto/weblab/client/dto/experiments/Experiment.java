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

import java.util.Date;


public class Experiment{
	
	private String name;
	private Category category;
	private Date startDate;
	private Date endDate;
	
	public Experiment(){}
	
	public Experiment(String name, Category category, Date startDate, Date endDate){
		this.name      = name;
		this.category  = category;
		this.startDate = startDate;
		this.endDate   = endDate;
	}
	
	public ExperimentID getExperimentID(){
		final ExperimentID experimentID = new ExperimentID();
		experimentID.setCategory(this.category);
		experimentID.setExperimentName(this.name);
		return experimentID;
	}
	
	public Category getCategory() {
		return this.category;
	}
	public void setCategory(Category category) {
		this.category = category;
	}
	public Date getEndDate() {
		return this.endDate;
	}
	public void setEndDate(Date endDate) {
		this.endDate = endDate;
	}
	public String getName() {
		return this.name;
	}
	public void setName(String name) {
		this.name = name;
	}
	public Date getStartDate() {
		return this.startDate;
	}
	public void setStartDate(Date startDate) {
		this.startDate = startDate;
	}
	
	public String getUniqueName() {
		return this.name + "@" + this.category.getCategory();
	}
	
	@Override
	public boolean equals(Object other) {
		if ( other instanceof Experiment ) {
			return this.name.equals(((Experiment)other).name) && this.category.equals(((Experiment)other).category);	
		} else {
			return false;
		}
		
	}
}
