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
* Author: Jaime Irurzun <jaime.irurzun@gmail.com>
*
*/

package es.deusto.weblab.client.admin.dto;

import com.smartgwt.client.widgets.grid.ListGridRecord;

public class ExperimentRecord extends ListGridRecord {
	
	public static final String ID       = "id";
	public static final String NAME     = "name";
	public static final String CATEGORY = "category";

	public ExperimentRecord() {  
    }  
	
    public ExperimentRecord(int id, String name, String category) {  
    	this.setId(id);
    	this.setName(name);
    	this.setCategory(category);
    }

	private void setId(int id) {
		this.setAttribute(ID, id);
	}  
  
    public int getId() {  
    	return this.getAttributeAsInt(ID);  
    }

	private void setName(String name) {
		this.setAttribute(NAME, name);
	}
  
    public String getName() {  
    	return this.getAttributeAsString(NAME);  
    }

	private void setCategory(String category) {
		this.setAttribute(CATEGORY, category);		
	}
  
    public String getCategory() {  
    	return this.getAttributeAsString(CATEGORY);  
    }
}  