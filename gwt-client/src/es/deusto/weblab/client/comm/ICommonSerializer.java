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
* Author: Pablo Orduña <pablo@ordunya.com>
*         Jaime Irurzun <jaime.irurzun@gmail.com>
*
*/

package es.deusto.weblab.client.comm;

import es.deusto.weblab.client.comm.exceptions.SerializationException;
import es.deusto.weblab.client.comm.exceptions.WebLabServerException;
import es.deusto.weblab.client.comm.exceptions.core.SessionNotFoundException;
import es.deusto.weblab.client.comm.exceptions.core.UserProcessingException;
import es.deusto.weblab.client.comm.exceptions.login.InvalidCredentialsException;
import es.deusto.weblab.client.comm.exceptions.login.LoginException;
import es.deusto.weblab.client.dto.SessionID;
import es.deusto.weblab.client.dto.users.User;

public interface ICommonSerializer {
	
	SessionID parseLoginResponse(String responseText) throws SerializationException, InvalidCredentialsException, LoginException, UserProcessingException, WebLabServerException;

	String serializeLoginRequest(String username, String password) throws SerializationException;
	
	void parseLogoutResponse(String responseText) 
		throws SerializationException, SessionNotFoundException, UserProcessingException, WebLabServerException;
	
	String serializeLogoutRequest(SessionID sessionId) throws SerializationException;

	User parseGetUserInformationResponse(String responseText) 
		throws SerializationException, SessionNotFoundException, UserProcessingException, WebLabServerException;

	String serializeGetUserInformationRequest(SessionID sessionId) throws SerializationException;
}
