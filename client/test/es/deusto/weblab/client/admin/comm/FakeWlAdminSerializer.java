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
import java.util.Date;

import es.deusto.weblab.client.comm.FakeWlCommonSerializer;
import es.deusto.weblab.client.comm.exceptions.SerializationException;
import es.deusto.weblab.client.comm.exceptions.WlServerException;
import es.deusto.weblab.client.comm.exceptions.core.SessionNotFoundException;
import es.deusto.weblab.client.comm.exceptions.core.UserProcessingException;
import es.deusto.weblab.client.dto.SessionID;
import es.deusto.weblab.client.dto.experiments.Experiment;
import es.deusto.weblab.client.dto.experiments.ExperimentUse;
import es.deusto.weblab.client.dto.users.Group;
import es.deusto.weblab.client.dto.users.User;


public class FakeWlAdminSerializer extends FakeWlCommonSerializer implements IWlAdminSerializer {
	
	public static final String PARSE_GET_GROUPS_RESPONSE          = "FakeWebLabSerializer::parseGetGroupsResponse";
	public static final String PARSE_GET_EXPERIMENTS_RESPONSE     = "FakeWebLabSerializer::parseGetExperimentsResponse";
	public static final String PARSE_GET_EXPERIMENT_USES_RESPONSE = "FakeWebLabSerializer::parseGetExperimentUsesResponse";
	public static final String PARSE_GET_USERS_RESPONSE			  = "FakeWebLabSerializer::parseGetUsersResponse";
	
	public static final String SERIALIZE_GET_GROUPS_REQUEST          = "FakeWebLabSerializer::serializeGetGroupsRequest";
	public static final String SERIALIZE_GET_EXPERIMENTS_REQUEST     = "FakeWebLabSerializer::serializeGetExperimentsRequest";
	public static final String SERIALIZE_GET_EXPERIMENT_USES_REQUEST = "FakeWebLabSerializer::serializeGetExperimentUsesRequest";
	public static final String SERIALIZE_GET_USERS_REQUEST 			 = "FakeWebLabSerializer::serializeGetUsersRequest";

	@SuppressWarnings("unchecked")
	@Override
	public ArrayList<Group> parseGetGroupsResponse(String response)
			throws SerializationException, SessionNotFoundException, UserProcessingException, WlServerException {
		this.append(FakeWlAdminSerializer.PARSE_GET_GROUPS_RESPONSE, new Object[]{
				response
		});
		return (ArrayList<Group>)this.retrieveReturn(FakeWlAdminSerializer.PARSE_GET_GROUPS_RESPONSE);
	}

	@SuppressWarnings("unchecked")
	@Override
	public ArrayList<Experiment> parseGetExperimentsResponse(String response)
			throws SerializationException, SessionNotFoundException, UserProcessingException, WlServerException {
		this.append(FakeWlAdminSerializer.PARSE_GET_EXPERIMENTS_RESPONSE, new Object[]{
				response
		});
		return (ArrayList<Experiment>)this.retrieveReturn(FakeWlAdminSerializer.PARSE_GET_EXPERIMENTS_RESPONSE);
	}

	@SuppressWarnings("unchecked")
	@Override
	public ArrayList<ExperimentUse> parseGetExperimentUsesResponse(	String response)
			throws SerializationException, 	SessionNotFoundException, UserProcessingException, WlServerException {
		this.append(FakeWlAdminSerializer.PARSE_GET_EXPERIMENT_USES_RESPONSE, new Object[]{
				response
		});
		return (ArrayList<ExperimentUse>)this.retrieveReturn(FakeWlAdminSerializer.PARSE_GET_EXPERIMENT_USES_RESPONSE);
	}

	@Override
	public String serializeGetGroupsRequest(SessionID sessionId) throws SerializationException {
		this.append(FakeWlAdminSerializer.SERIALIZE_GET_GROUPS_REQUEST, new Object[]{
				sessionId
		});
		return (String)this.retrieveReturn(FakeWlAdminSerializer.SERIALIZE_GET_GROUPS_REQUEST);
	}

	@Override
	public String serializeGetExperimentsRequest(SessionID sessionId) throws SerializationException {
		this.append(FakeWlAdminSerializer.SERIALIZE_GET_EXPERIMENTS_REQUEST, new Object[]{
				sessionId
		});
		return (String)this.retrieveReturn(FakeWlAdminSerializer.SERIALIZE_GET_EXPERIMENTS_REQUEST);
	}

	@Override
	public String serializeGetExperimentUsesRequest(SessionID sessionId, Date fromDate, Date toDate, int groupId, int experimentId) throws SerializationException {
		this.append(FakeWlAdminSerializer.SERIALIZE_GET_EXPERIMENT_USES_REQUEST, new Object[]{
				sessionId
		});
		return (String)this.retrieveReturn(FakeWlAdminSerializer.SERIALIZE_GET_EXPERIMENT_USES_REQUEST);
	}

	@SuppressWarnings("unchecked")
	@Override
	public ArrayList<User> parseGetUsersResponse(String response)
			throws SerializationException, SessionNotFoundException, UserProcessingException, WlServerException {
		
		this.append(FakeWlAdminSerializer.PARSE_GET_USERS_RESPONSE, new Object[]{
				response
		});
		return (ArrayList<User>)this.retrieveReturn(FakeWlAdminSerializer.PARSE_GET_USERS_RESPONSE);
	}

	@Override
	public String serializeGetUsersRequest(SessionID sessionId) throws SerializationException {
		this.append(FakeWlAdminSerializer.SERIALIZE_GET_USERS_REQUEST, new Object[]{
			sessionId
		});
		return (String)this.retrieveReturn(FakeWlAdminSerializer.SERIALIZE_GET_USERS_REQUEST);
	}
}
