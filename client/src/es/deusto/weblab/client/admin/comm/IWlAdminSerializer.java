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

import es.deusto.weblab.client.comm.IWlCommonSerializer;
import es.deusto.weblab.client.comm.exceptions.SerializationException;
import es.deusto.weblab.client.comm.exceptions.WlServerException;
import es.deusto.weblab.client.comm.exceptions.core.SessionNotFoundException;
import es.deusto.weblab.client.comm.exceptions.core.UserProcessingException;
import es.deusto.weblab.client.dto.SessionID;
import es.deusto.weblab.client.dto.experiments.Experiment;
import es.deusto.weblab.client.dto.experiments.ExperimentUse;
import es.deusto.weblab.client.dto.users.Group;
import es.deusto.weblab.client.dto.users.User;

public interface IWlAdminSerializer extends IWlCommonSerializer {

	ArrayList<Experiment> parseGetExperimentsResponse(String response)
		throws SerializationException, SessionNotFoundException, UserProcessingException, WlServerException;	

	ArrayList<Group> parseGetGroupsResponse(String response)
		throws SerializationException, SessionNotFoundException, UserProcessingException, WlServerException;

	ArrayList<ExperimentUse> parseGetExperimentUsesResponse(String response)
		throws SerializationException, SessionNotFoundException, UserProcessingException, WlServerException;

	ArrayList<User> parseGetUsersResponse(String response)
		throws SerializationException, SessionNotFoundException, UserProcessingException, WlServerException;
	
	String serializeGetExperimentsRequest(SessionID sessionId) throws SerializationException;

	String serializeGetGroupsRequest(SessionID sessionId) throws SerializationException;

	String serializeGetExperimentUsesRequest(SessionID sessionId, Date fromDate, Date toDate, int groupId, int experimentId) throws SerializationException;

	String serializeGetUsersRequest(SessionID sessionId) throws SerializationException;
}
