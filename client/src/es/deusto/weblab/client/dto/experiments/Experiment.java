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

import java.util.Date;


public class Experiment{

	private int id;
	private String name;
	private Category category;
	private Date startDate;
	private Date endDate;
	
	public Experiment(){}
	
	public Experiment(int id, String name, Category category, Date startDate, Date endDate){
		this.id        = id;
		this.name      = name;
		this.category  = category;
		this.startDate = startDate;
		this.endDate   = endDate;
	}
	
	public ExperimentID getExperimentUniqueName(){
		final ExperimentID experimentID = new ExperimentID();
		experimentID.setCategory(this.category);
		experimentID.setExperimentName(this.name);
		return experimentID;
	}

	public void setId(int id) {
		this.id = id;
	}
	public int getId() {
		return this.id;
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

	/* (non-Javadoc)
	 * @see java.lang.Object#toString()
	 */
	@Override
	public String toString() {
		return "Experiment [id=" + this.id + ", name=" + this.name
				+ ", category=" + this.category + ", startDate="
				+ this.startDate + ", endDate=" + this.endDate + "]";
	}
}
