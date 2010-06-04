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

package es.deusto.weblab.client.admin.comm;

import java.util.ArrayList;

import com.google.gwt.i18n.client.DateTimeFormat;
import com.google.gwt.json.client.JSONArray;
import com.google.gwt.json.client.JSONObject;
import com.google.gwt.json.client.JSONValue;

import es.deusto.weblab.client.comm.WlCommonSerializerJSON;
import es.deusto.weblab.client.comm.exceptions.SerializationException;
import es.deusto.weblab.client.comm.exceptions.WlServerException;
import es.deusto.weblab.client.comm.exceptions.core.SessionNotFoundException;
import es.deusto.weblab.client.comm.exceptions.core.UserProcessingException;
import es.deusto.weblab.client.dto.SessionID;
import es.deusto.weblab.client.dto.experiments.Category;
import es.deusto.weblab.client.dto.experiments.Experiment;
import es.deusto.weblab.client.dto.users.Group;

public class WlAdminSerializerJSON extends WlCommonSerializerJSON implements IWlAdminSerializer {

	@Override
	public ArrayList<Group> parseGetGroupsResponse(String responseText) throws SerializationException, SessionNotFoundException, UserProcessingException, WlServerException {
		JSONArray result = this.parseResultArray(responseText);
		return parseGetGroupsRecursively(result);
	}

	private ArrayList<Group> parseGetGroupsRecursively(JSONArray result) throws SerializationException {
		ArrayList<Group> groups = new ArrayList<Group>();
		
		for( int i = 0; i < result.size(); ++i ) {
		    JSONValue value = result.get(i);
		    JSONObject jsonGroup = value.isObject();
		    if(jsonGroup == null)
		    	throw new SerializationException("Expected JSON Object as Group, found: " + value);
		    
			// name
			JSONValue jsonNameValue = jsonGroup.get("name");
			if ( jsonNameValue == null )
				throw new SerializationException("Expected name field in Group");
			String name = this.json2string(jsonNameValue);		    
		    
			// children
			JSONValue jsonChildrenValue = jsonGroup.get("children");
		    if( jsonChildrenValue == null )
		    	throw new SerializationException("Expected children field in Group");
		    JSONArray jsonChildren = jsonChildrenValue.isArray();
			if( jsonChildren == null )
		    	throw new SerializationException("Expected JSON Array as children, found: " + jsonChildrenValue);
		    ArrayList<Group> children = parseGetGroupsRecursively(jsonChildren);
			
		    groups.add(new Group(name, children));
		}		

		return groups;
	}	

	@Override
	public ArrayList<Experiment> parseGetExperimentsResponse(String response)
			throws SerializationException, SessionNotFoundException, UserProcessingException, WlServerException {
		ArrayList<Experiment> experiments = new ArrayList<Experiment>();
		
		JSONArray result = this.parseResultArray(response);
		for( int i = 0; i < result.size(); ++i ) {
		    JSONValue value = result.get(i);
		    JSONObject jsonExperiment = value.isObject();
		    if(jsonExperiment == null)
		    	throw new SerializationException("Expected JSON Object as Experiment, found: " + value);
		    Experiment experiment = new Experiment();
		    
		    // name
		    JSONValue jsonNameValue = jsonExperiment.get("name");
		    if(jsonNameValue == null)
		    	throw new SerializationException("Expected name field in Experiment");
		    experiment.setName(this.json2string(jsonExperiment.get("name")));
		    
		    // category
		    JSONValue jsonCategoryValue = jsonExperiment.get("category");
		    if(jsonCategoryValue == null)
		    	throw new SerializationException("Expected category field in Experiment");
		    JSONObject jsonCategory = jsonCategoryValue.isObject();
		    if(jsonCategory == null)
		    	throw new SerializationException("Expected JSON Object as Category, found: " + jsonCategoryValue);
		    experiment.setCategory(new Category(this.json2string(jsonCategory.get("name"))));
		    
		    // startDate && endDate
		    String startDateString = this.json2string(jsonExperiment.get("start_date"));
		    String endDateString   = this.json2string(jsonExperiment.get("end_date"));
		    DateTimeFormat formatter1 = DateTimeFormat.getFormat("yyyy-MM-dd");
		    DateTimeFormat formatter2 = DateTimeFormat.getFormat("yyyy-MM-dd HH:mm:ss");
		    DateTimeFormat formatter3 = DateTimeFormat.getFormat("yyyy-MM-ddTHH:mm:ss");
		    try {
				experiment.setStartDate(formatter1.parse(startDateString));
				experiment.setEndDate(formatter1.parse(endDateString));
		    } catch( IllegalArgumentException iae ) {
				try{
				    experiment.setStartDate(formatter2.parse(startDateString));
				    experiment.setEndDate(formatter2.parse(endDateString));
				}catch(IllegalArgumentException iae2){
					try{
					    experiment.setStartDate(formatter3.parse(startDateString));
					    experiment.setEndDate(formatter3.parse(endDateString));
					}catch(IllegalArgumentException iae3){
					    throw new SerializationException("Couldn't parse date: " + startDateString + "; or: " + endDateString);
					}
				}
		    }		 
		    experiments.add(experiment);   
		}		

		return experiments;
	}
	
	@Override
	public String serializeGetGroupsRequest(SessionID sessionId) throws SerializationException {
		final JSONObject params = new JSONObject();
		params.put("session_id", this.serializeSessionId(sessionId));
		return this.serializeRequest("get_groups", params);
	}

	@Override
	public String serializeGetExperimentsRequest(SessionID sessionId) throws SerializationException {
		final JSONObject params = new JSONObject();
		params.put("session_id", this.serializeSessionId(sessionId));
		return this.serializeRequest("get_experiments", params);
	}
}
