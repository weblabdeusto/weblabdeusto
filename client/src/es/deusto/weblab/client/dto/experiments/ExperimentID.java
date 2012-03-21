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

public class ExperimentID {
	private Category category;
	private String experimentName;
	
	public ExperimentID(){}
	
	public ExperimentID(Category category, String experimentName){
		this.category = category;
		this.experimentName = experimentName;
	}
	
	public Category getCategory() {
		return this.category;
	}
	public void setCategory(Category category) {
		this.category = category;
	}
	public String getExperimentName() {
		return this.experimentName;
	}
	public void setExperimentName(String experimentName) {
		this.experimentName = experimentName;
	}
	
	@Override
	public String toString(){
		return "<ExperimentID> " 
				+ "<experimentName>" 
					+ this.experimentName 
				+ "</experimentName>"
				+ this.category
			 + "</ExperimentID>";
	}
	
	@Override
	public boolean equals(Object o){
	    return o instanceof ExperimentID 
	    	&& ((ExperimentID)o).experimentName.equals(this.experimentName)
	    	&& this.category.equals(((ExperimentID)o).category);
	}
}
