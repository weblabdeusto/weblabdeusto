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

package es.deusto.weblab.client.admin.comm;

import java.util.ArrayList;
import java.util.Date;

import com.google.gwt.i18n.client.DateTimeFormat;
import com.google.gwt.json.client.JSONArray;
import com.google.gwt.json.client.JSONNumber;
import com.google.gwt.json.client.JSONObject;
import com.google.gwt.json.client.JSONString;
import com.google.gwt.json.client.JSONValue;

import es.deusto.weblab.client.comm.WlCommonSerializerJSON;
import es.deusto.weblab.client.comm.exceptions.SerializationException;
import es.deusto.weblab.client.comm.exceptions.WlServerException;
import es.deusto.weblab.client.comm.exceptions.core.SessionNotFoundException;
import es.deusto.weblab.client.comm.exceptions.core.UserProcessingException;
import es.deusto.weblab.client.dto.SessionID;
import es.deusto.weblab.client.dto.experiments.Experiment;
import es.deusto.weblab.client.dto.experiments.ExperimentUse;
import es.deusto.weblab.client.dto.users.Group;
import es.deusto.weblab.client.dto.users.User;

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

			// id
			JSONValue jsonIdValue = jsonGroup.get("id");
			if ( jsonIdValue == null )
				throw new SerializationException("Expected id field in Group");
			int id = this.json2int(jsonIdValue);		    
			
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
			
		    groups.add(new Group(id, name, children));
		}		

		return groups;
	}	
	
	@Override
	public ArrayList<User> parseGetUsersResponse(String response)
			throws SerializationException, SessionNotFoundException,
			UserProcessingException, WlServerException {
		
		ArrayList<User> users = new ArrayList<User>();
		
		JSONArray result = this.parseResultArray(response);
		for(int i = 0; i < result.size(); ++i) {
			JSONValue value = result.get(i);
			JSONObject jsonUser = value.isObject();
			if(jsonUser == null)
				throw new SerializationException("Expected JSON Object as User, found: " + value);
			users.add(this.parseUser(jsonUser));
		}
		
		return users;
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
		    experiments.add(this.parseExperiment(jsonExperiment));   
		}		

		return experiments;
	}

	@Override
	public ArrayList<ExperimentUse> parseGetExperimentUsesResponse(	String response)
			throws SerializationException, 	SessionNotFoundException, UserProcessingException, WlServerException {
		ArrayList<ExperimentUse> experimentUses = new ArrayList<ExperimentUse>();
		
		JSONArray result = this.parseResultArray(response);
		for( int i = 0; i < result.size(); ++i ) {
		    JSONValue value = result.get(i);
		    JSONObject jsonExperimentUse = value.isObject();
		    if(jsonExperimentUse == null)
		    	throw new SerializationException("Expected JSON Object as ExperimentUse, found: " + value);
		    ExperimentUse experimentUse = new ExperimentUse();
		    
		    // id
		    JSONValue jsonIdValue = jsonExperimentUse.get("id");
		    if(jsonIdValue == null)
		    	throw new SerializationException("Expected id field in ExperimentUse");
		    experimentUse.setId(this.json2int(jsonIdValue));
		    
		    // startDate && endDate
		    String startDateString = this.json2string(jsonExperimentUse.get("start_date"));
		    String endDateString   = this.json2string(jsonExperimentUse.get("end_date"));
		    DateTimeFormat formatter1 = DateTimeFormat.getFormat("yyyy-MM-dd");
		    DateTimeFormat formatter2 = DateTimeFormat.getFormat("yyyy-MM-dd HH:mm:ss");
		    DateTimeFormat formatter3 = DateTimeFormat.getFormat("yyyy-MM-ddTHH:mm:ss");
		    try {
		    	experimentUse.setStartDate(formatter1.parse(startDateString));
		    	experimentUse.setEndDate(formatter1.parse(endDateString));
		    } catch( IllegalArgumentException iae ) {
				try{
					experimentUse.setStartDate(formatter2.parse(startDateString));
					experimentUse.setEndDate(formatter2.parse(endDateString));
				}catch(IllegalArgumentException iae2){
					try{
						experimentUse.setStartDate(formatter3.parse(startDateString));
						experimentUse.setEndDate(formatter3.parse(endDateString));
					}catch(IllegalArgumentException iae3){
					    throw new SerializationException("Couldn't parse date: " + startDateString + "; or: " + endDateString);
					}
				}
		    }		 	
		    
		    // experiment
		    JSONValue jsonExperimentValue = jsonExperimentUse.get("experiment");
		    if(jsonExperimentValue == null)
		    	throw new SerializationException("Expected experiment field in ExperimentUse");
		    JSONObject jsonExperiment = jsonExperimentValue.isObject();
		    if(jsonExperiment == null)
		    	throw new SerializationException("Expected JSON Object as Experiment, found: " + jsonExperimentValue);
		    experimentUse.setExperiment(this.parseExperiment(jsonExperiment));
		    
		    // agent (User or ExternalEntity)
		    JSONValue jsonAgentValue = jsonExperimentUse.get("agent");
		    if(jsonAgentValue == null)
		    	throw new SerializationException("Expected agent field in ExperimentUse");
		    JSONObject jsonAgent = jsonAgentValue.isObject();
		    if(jsonAgent == null)
		    	throw new SerializationException("Expected JSON Object as Agent, found: " + jsonAgentValue);
		    JSONValue jsonAgentLoginValue = jsonAgent.get("login");
		    if(jsonAgentLoginValue == null) {
		    	experimentUse.setAgent(this.parseExternalEntity(jsonAgent));
		    } else {
		    	experimentUse.setAgent(this.parseUser(jsonAgent));
		    }

		    // origin
		    JSONValue jsonOriginValue = jsonExperimentUse.get("origin");
		    if(jsonOriginValue == null)
		    	throw new SerializationException("Expected origin field in ExperimentUse");
		    experimentUse.setOrigin(this.json2string(jsonOriginValue));
		    
		    experimentUses.add(experimentUse);   
		}		

		return experimentUses;
	}

	@Override
	public String serializeGetGroupsRequest(SessionID sessionId) throws SerializationException {
		final JSONObject params = new JSONObject();
		params.put("session_id", this.serializeSessionId(sessionId));
		return this.serializeRequest("get_groups", params);
	}
	
	@Override
	public String serializeGetUsersRequest(SessionID sessionId)
			throws SerializationException {
		final JSONObject params = new JSONObject();
		params.put("session_id", this.serializeSessionId(sessionId));
		return this.serializeRequest("get_users", params);
	}

	@Override
	public String serializeGetExperimentsRequest(SessionID sessionId) throws SerializationException {
		final JSONObject params = new JSONObject();
		params.put("session_id", this.serializeSessionId(sessionId));
		return this.serializeRequest("get_experiments", params);
	}

	@Override
	public String serializeGetExperimentUsesRequest(SessionID sessionId, Date fromDate, Date toDate, int groupId, int experimentId) throws SerializationException {
		final JSONObject params = new JSONObject();
		params.put("session_id", this.serializeSessionId(sessionId));
		if ( fromDate != null ) {
			params.put("from_date", new JSONString(fromDate.toString()));	
		} else {
			params.put("from_date", new JSONObject(null));	
		}
		if ( toDate != null ) {
			params.put("to_date", new JSONString(toDate.toString()));
		} else {
			params.put("to_date", new JSONObject(null));
		}
		if ( groupId != -1 ) {
			params.put("group_id", new JSONNumber(groupId));
		} else {
			params.put("group_id", new JSONObject(null));
		}
		if ( experimentId != -1 ) {
			params.put("experiment_id", new JSONNumber(experimentId));
		} else {
			params.put("experiment_id", new JSONObject(null));
		}
		return this.serializeRequest("get_experiment_uses", params);
	}

}
