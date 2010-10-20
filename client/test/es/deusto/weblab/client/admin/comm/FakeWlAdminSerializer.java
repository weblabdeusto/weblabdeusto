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
* Author: Pablo Orduña <pablo@ordunya.com>
*         Jaime Irurzun <jaime.irurzun@gmail.com>
*
*/

package es.deusto.weblab.client.admin.comm;

import es.deusto.weblab.client.comm.FakeWlCommonSerializer;
import es.deusto.weblab.client.comm.exceptions.SerializationException;
import es.deusto.weblab.client.comm.exceptions.WlServerException;
import es.deusto.weblab.client.comm.exceptions.core.SessionNotFoundException;
import es.deusto.weblab.client.comm.exceptions.core.UserProcessingException;
import es.deusto.weblab.client.dto.SessionID;
import es.deusto.weblab.client.dto.users.Permission;


public class FakeWlAdminSerializer extends FakeWlCommonSerializer implements IWlAdminSerializer {

	public static final String PARSE_GET_USER_PERMISSIONS_RESPONSE    = "FakeWebLabSerializer::parseGetUserPermissions";

	public static final String SERIALIZE_GET_USER_PERMISSIONS_REQUEST = "FakeWebLabSerializer::serializeGetUserPermissionsRequest";
	
	@Override
	public Permission[] parseGetUserPermissionsResponse(String responseText)
			throws SerializationException, SessionNotFoundException, UserProcessingException, WlServerException {
		this.append(FakeWlAdminSerializer.PARSE_GET_USER_PERMISSIONS_RESPONSE, new Object[]{
				responseText
		});
		return (Permission [])this.retrieveReturn(FakeWlAdminSerializer.PARSE_GET_USER_PERMISSIONS_RESPONSE);
	}

	@Override
	public String serializeGetUserPermissionsRequest(SessionID sessionId) throws SerializationException {
		this.append(FakeWlAdminSerializer.SERIALIZE_GET_USER_PERMISSIONS_REQUEST, new Object[]{
				sessionId
		});
		return (String)this.retrieveReturn(FakeWlAdminSerializer.SERIALIZE_GET_USER_PERMISSIONS_REQUEST);
	}
}
