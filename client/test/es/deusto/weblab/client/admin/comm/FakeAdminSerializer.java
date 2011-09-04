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

import es.deusto.weblab.client.comm.FakeCommonSerializer;
import es.deusto.weblab.client.comm.exceptions.SerializationException;
import es.deusto.weblab.client.comm.exceptions.WebLabServerException;
import es.deusto.weblab.client.comm.exceptions.core.SessionNotFoundException;
import es.deusto.weblab.client.comm.exceptions.core.UserProcessingException;
import es.deusto.weblab.client.dto.SessionID;
import es.deusto.weblab.client.dto.users.Permission;


public class FakeAdminSerializer extends FakeCommonSerializer implements IAdminSerializer {

	public static final String PARSE_GET_USER_PERMISSIONS_RESPONSE    = "FakeWebLabSerializer::parseGetUserPermissions";

	public static final String SERIALIZE_GET_USER_PERMISSIONS_REQUEST = "FakeWebLabSerializer::serializeGetUserPermissionsRequest";
	
	@Override
	public Permission[] parseGetUserPermissionsResponse(String responseText)
			throws SerializationException, SessionNotFoundException, UserProcessingException, WebLabServerException {
		this.append(FakeAdminSerializer.PARSE_GET_USER_PERMISSIONS_RESPONSE, new Object[]{
				responseText
		});
		return (Permission [])this.retrieveReturn(FakeAdminSerializer.PARSE_GET_USER_PERMISSIONS_RESPONSE);
	}

	@Override
	public String serializeGetUserPermissionsRequest(SessionID sessionId) throws SerializationException {
		this.append(FakeAdminSerializer.SERIALIZE_GET_USER_PERMISSIONS_REQUEST, new Object[]{
				sessionId
		});
		return (String)this.retrieveReturn(FakeAdminSerializer.SERIALIZE_GET_USER_PERMISSIONS_REQUEST);
	}
}
