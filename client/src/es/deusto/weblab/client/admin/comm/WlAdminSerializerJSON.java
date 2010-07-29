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
		final JSONArray result = this.parseResultArray(responseText);
		return this.parseGetGroupsRecursively(result);
	}

	private ArrayList<Group> parseGetGroupsRecursively(JSONArray result) throws SerializationException {
		final ArrayList<Group> groups = new ArrayList<Group>();
		
		for( int i = 0; i < result.size(); ++i ) {
		    final JSONValue value = result.get(i);
		    final JSONObject jsonGroup = value.isObject();
		    if(jsonGroup == null)
		    	throw new SerializationException("Expected JSON Object as Group, found: " + value);

			// id
			final JSONValue jsonIdValue = jsonGroup.get("id");
			if ( jsonIdValue == null )
				throw new SerializationException("Expected id field in Group");
			final int id = this.json2int(jsonIdValue);		    
			
			// name
			final JSONValue jsonNameValue = jsonGroup.get("name");
			if ( jsonNameValue == null )
				throw new SerializationException("Expected name field in Group");
			final String name = this.json2string(jsonNameValue);		    
		    
			// children
			final JSONValue jsonChildrenValue = jsonGroup.get("children");
		    if( jsonChildrenValue == null )
		    	throw new SerializationException("Expected children field in Group");
		    final JSONArray jsonChildren = jsonChildrenValue.isArray();
			if( jsonChildren == null )
		    	throw new SerializationException("Expected JSON Array as children, found: " + jsonChildrenValue);
		    final ArrayList<Group> children = this.parseGetGroupsRecursively(jsonChildren);
			
		    groups.add(new Group(id, name, children));
		}		

		return groups;
	}	
	
	@Override
	public ArrayList<User> parseGetUsersResponse(String response)
			throws SerializationException, SessionNotFoundException,
			UserProcessingException, WlServerException {
		
		final ArrayList<User> users = new ArrayList<User>();
		
		final JSONArray result = this.parseResultArray(response);
		for(int i = 0; i < result.size(); ++i) {
			final JSONValue value = result.get(i);
			final JSONObject jsonUser = value.isObject();
			if(jsonUser == null)
				throw new SerializationException("Expected JSON Object as User, found: " + value);
			users.add(this.parseUser(jsonUser));
		}
		
		return users;
	}

	@Override
	public ArrayList<Experiment> parseGetExperimentsResponse(String response)
			throws SerializationException, SessionNotFoundException, UserProcessingException, WlServerException {
		final ArrayList<Experiment> experiments = new ArrayList<Experiment>();
		
		final JSONArray result = this.parseResultArray(response);
		for( int i = 0; i < result.size(); ++i ) {
		    final JSONValue value = result.get(i);
		    final JSONObject jsonExperiment = value.isObject();
		    if(jsonExperiment == null)
		    	throw new SerializationException("Expected JSON Object as Experiment, found: " + value);
		    experiments.add(this.parseExperiment(jsonExperiment));   
		}		

		return experiments;
	}

	@Override
	public ArrayList<ExperimentUse> parseGetExperimentUsesResponse(	String response)
			throws SerializationException, 	SessionNotFoundException, UserProcessingException, WlServerException {
		final ArrayList<ExperimentUse> experimentUses = new ArrayList<ExperimentUse>();
		
		final JSONArray result = this.parseResultArray(response);
		for( int i = 0; i < result.size(); ++i ) {
		    final JSONValue value = result.get(i);
		    final JSONObject jsonExperimentUse = value.isObject();
		    if(jsonExperimentUse == null)
		    	throw new SerializationException("Expected JSON Object as ExperimentUse, found: " + value);
		    final ExperimentUse experimentUse = new ExperimentUse();
		    
		    // id
		    final JSONValue jsonIdValue = jsonExperimentUse.get("id");
		    if(jsonIdValue == null)
		    	throw new SerializationException("Expected id field in ExperimentUse");
		    experimentUse.setId(this.json2int(jsonIdValue));
		    
		    // startDate && endDate
		    final String startDateString = this.json2string(jsonExperimentUse.get("start_date"));
		    final String endDateString   = this.json2string(jsonExperimentUse.get("end_date"));
		    final DateTimeFormat formatter1 = DateTimeFormat.getFormat("yyyy-MM-dd");
		    final DateTimeFormat formatter2 = DateTimeFormat.getFormat("yyyy-MM-dd HH:mm:ss");
		    final DateTimeFormat formatter3 = DateTimeFormat.getFormat("yyyy-MM-ddTHH:mm:ss");
		    try {
		    	experimentUse.setStartDate(formatter1.parse(startDateString));
		    	experimentUse.setEndDate(formatter1.parse(endDateString));
		    } catch( final IllegalArgumentException iae ) {
				try{
					experimentUse.setStartDate(formatter2.parse(startDateString));
					experimentUse.setEndDate(formatter2.parse(endDateString));
				}catch(final IllegalArgumentException iae2){
					try{
						experimentUse.setStartDate(formatter3.parse(startDateString));
						experimentUse.setEndDate(formatter3.parse(endDateString));
					}catch(final IllegalArgumentException iae3){
					    throw new SerializationException("Couldn't parse date: " + startDateString + "; or: " + endDateString);
					}
				}
		    }		 	
		    
		    // experiment
		    final JSONValue jsonExperimentValue = jsonExperimentUse.get("experiment");
		    if(jsonExperimentValue == null)
		    	throw new SerializationException("Expected experiment field in ExperimentUse");
		    final JSONObject jsonExperiment = jsonExperimentValue.isObject();
		    if(jsonExperiment == null)
		    	throw new SerializationException("Expected JSON Object as Experiment, found: " + jsonExperimentValue);
		    experimentUse.setExperiment(this.parseExperiment(jsonExperiment));
		    
		    // agent (User or ExternalEntity)
		    final JSONValue jsonAgentValue = jsonExperimentUse.get("agent");
		    if(jsonAgentValue == null)
		    	throw new SerializationException("Expected agent field in ExperimentUse");
		    final JSONObject jsonAgent = jsonAgentValue.isObject();
		    if(jsonAgent == null)
		    	throw new SerializationException("Expected JSON Object as Agent, found: " + jsonAgentValue);
		    final JSONValue jsonAgentLoginValue = jsonAgent.get("login");
		    if(jsonAgentLoginValue == null) {
		    	experimentUse.setAgent(this.parseExternalEntity(jsonAgent));
		    } else {
		    	experimentUse.setAgent(this.parseUser(jsonAgent));
		    }

		    // origin
		    final JSONValue jsonOriginValue = jsonExperimentUse.get("origin");
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
