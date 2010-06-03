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

import es.deusto.weblab.client.comm.FakeWlCommonSerializer;
import es.deusto.weblab.client.comm.exceptions.SerializationException;
import es.deusto.weblab.client.comm.exceptions.WlServerException;
import es.deusto.weblab.client.comm.exceptions.core.SessionNotFoundException;
import es.deusto.weblab.client.comm.exceptions.core.UserProcessingException;
import es.deusto.weblab.client.dto.SessionID;
import es.deusto.weblab.client.dto.users.Group;


public class FakeWlAdminSerializer extends FakeWlCommonSerializer implements IWlAdminSerializer {
	
	public static final String PARSE_GET_GROUPS_RESPONSE          = "FakeWebLabSerializer::parseGetGroupsResponse";
	
	public static final String SERIALIZE_GET_GROUPS_REQUEST       = "FakeWebLabSerializer::serializeGetGroupsRequest";

	@Override
	public ArrayList<Group> parseGetGroupsResponse(String response)
		throws SerializationException, SessionNotFoundException, UserProcessingException, WlServerException {
		this.append(FakeWlAdminSerializer.PARSE_GET_GROUPS_RESPONSE, new Object[]{
				response
		});
		return (ArrayList<Group>)this.retrieveReturn(FakeWlAdminSerializer.PARSE_GET_GROUPS_RESPONSE);
	}

	@Override
	public String serializeGetGroupsRequest(SessionID sessionId) throws SerializationException {
		this.append(FakeWlAdminSerializer.SERIALIZE_GET_GROUPS_REQUEST, new Object[]{
				sessionId
		});
		return (String)this.retrieveReturn(FakeWlAdminSerializer.SERIALIZE_GET_GROUPS_REQUEST);
	}

}
