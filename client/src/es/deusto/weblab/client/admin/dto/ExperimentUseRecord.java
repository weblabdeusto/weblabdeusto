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

package es.deusto.weblab.client.admin.dto;

import java.util.Date;

import com.smartgwt.client.widgets.grid.ListGridRecord;

public class ExperimentUseRecord extends ListGridRecord {
	
	public static final String ID                  = "id";
	public static final String START_DATE          = "start_date";
	public static final String END_DATE            = "end_date";
	public static final String AGENT_LOGIN         = "agent_login";
	public static final String AGENT_NAME          = "agent_name";
	public static final String AGENT_EMAIL         = "agent_email";
	public static final String EXPERIMENT_ID       = "experiment_id";
	public static final String EXPERIMENT_NAME     = "experiment_name";
	public static final String EXPERIMENT_CATEGORY = "experiment_category";
	public static final String ORIGIN              = "origin";
	
	// Calculated fields
	public static final String TIME				   = "time";
	public static final String DURATION			   = "duration";
	
	// Utility fields (for the request, but not part of the record itself)
	public static final String GROUP_ID            = "group";

	public ExperimentUseRecord() {  
    }  
  
    public ExperimentUseRecord(int id, Date startDate, Date endDate, String agentLogin, String agentName, String agentEmail, int experimentId, String experimentName, String experimentCategory, String origin) {  
    	this.setId(id);
    	this.setStartDate(startDate);
    	this.setEndDate(endDate);
    	this.setAgentLogin(agentLogin);
    	this.setAgentName(agentName);
    	this.setAgentEmail(agentEmail);
    	this.setExperimentId(experimentId);
    	this.setExperimentName(experimentName);
    	this.setExperimentCategory(experimentCategory);
    	this.setOrigin(origin);
    }  

    public int getId() {
		return this.getAttributeAsInt(ExperimentUseRecord.ID);
	}
    
    public void setId(int id) {
    	this.setAttribute(ExperimentUseRecord.ID, id);
    }
  
    public Date getStartDate() {  
        return this.getAttributeAsDate(ExperimentUseRecord.START_DATE);  
    }

	public void setStartDate(Date startDate) {  
        this.setAttribute(ExperimentUseRecord.START_DATE, startDate);  
    }  
  
    public Date getEndDate() {  
        return this.getAttributeAsDate(ExperimentUseRecord.END_DATE);  
    }
    
    public void setEndDate(Date endDate) {  
        this.setAttribute(ExperimentUseRecord.END_DATE, endDate);  
    }  
    
	public String getAgentLogin() {
		return this.getAttributeAsString(ExperimentUseRecord.AGENT_LOGIN);
	}
	
	public void setAgentLogin(String agentLogin) {
		this.setAttribute(ExperimentUseRecord.AGENT_LOGIN, agentLogin);
	}

	public String getAgentName() {
		return this.getAttributeAsString(ExperimentUseRecord.AGENT_NAME);
	}
	
	public void setAgentName(String agentName) {
		this.setAttribute(ExperimentUseRecord.AGENT_NAME, agentName);
	}

	public String getAgentEmail() {
		return this.getAttributeAsString(ExperimentUseRecord.AGENT_EMAIL);
	}
	
	public void setAgentEmail(String agentEmail) {
		this.setAttribute(ExperimentUseRecord.AGENT_EMAIL, agentEmail);
	}

	public int getExperimentId() {
		return this.getAttributeAsInt(ExperimentUseRecord.EXPERIMENT_ID);
	}
	
	public void setExperimentId(int experimentId) {
		this.setAttribute(ExperimentUseRecord.EXPERIMENT_ID, experimentId);
	}

	public String getExperimentName() {
		return this.getAttributeAsString(ExperimentUseRecord.EXPERIMENT_NAME);
	}
	
	public void setExperimentName(String experimentName) {
		this.setAttribute(ExperimentUseRecord.EXPERIMENT_NAME, experimentName);
	}

	public String getExperimentCategory() {
		return this.getAttributeAsString(ExperimentUseRecord.EXPERIMENT_CATEGORY);
	}
	
	public void setExperimentCategory(String experimentCategory) {
		this.setAttribute(ExperimentUseRecord.EXPERIMENT_CATEGORY, experimentCategory);
	}
  
    public String getOrigin() {  
        return this.getAttributeAsString(ExperimentUseRecord.ORIGIN);  
    }

	public void setOrigin(String origin) {
		this.setAttribute(ExperimentUseRecord.ORIGIN, origin);
	}
}  