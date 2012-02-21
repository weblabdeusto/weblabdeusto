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
*          Jaime Irurzun <jaime.irurzun@gmail.com>
 *
 */

package es.deusto.weblab.client.comm;

import com.google.gwt.json.client.JSONObject;
import com.google.gwt.json.client.JSONValue;

import es.deusto.weblab.client.comm.exceptions.SerializationException;
import es.deusto.weblab.client.comm.exceptions.WebLabServerException;
import es.deusto.weblab.client.dto.SessionID;
import es.deusto.weblab.client.dto.users.User;
import es.deusto.weblab.client.testing.util.WebLabFake;

public class FakeCommonSerializer extends WebLabFake implements ICommonSerializer {

	public static final String PARSE_LOGIN_RESPONSE                     = "FakeWebLabSerializer::parseLoginResponse";
	public static final String SERIALIZE_LOGIN_REQUEST                  = "FakeWebLabSerializer::serializeLoginRequest";
	public static final String PARSE_LOGOUT_RESPONSE                    = "FakeWebLabSerializer::parseLogoutResponse";
	public static final String SERIALIZE_LOGOUT_REQUEST                 = "FakeWebLabSerializer::serializeLogoutRequest";
	public static final String PARSE_GET_USER_INFORMATION_RESPONSE      = "FakeWebLabSerializer::parseGetUserInformation";
	public static final String SERIALIZE_GET_USER_INFORMATION_REQUEST   = "FakeWebLabSerializer::serializeGetUserInformationRequest";

	
	@Override
	public SessionID parseLoginResponse(String responseText) throws SerializationException {
		this.append(FakeCommonSerializer.PARSE_LOGIN_RESPONSE, new Object[]{responseText});
		return (SessionID)this.retrieveReturn(FakeCommonSerializer.PARSE_LOGIN_RESPONSE);
	}

	@Override
	public String serializeLoginRequest(String username, String password) throws SerializationException {
		this.append(FakeCommonSerializer.SERIALIZE_LOGIN_REQUEST, new Object[]{	username, password});
		return (String)this.retrieveReturn(FakeCommonSerializer.SERIALIZE_LOGIN_REQUEST);
	}
	
	@Override
	public void parseLogoutResponse(String responseText)
		throws SerializationException {
		this.append(FakeCommonSerializer.PARSE_LOGOUT_RESPONSE, new Object[]{
				responseText
		});
	}

	@Override
	public String serializeLogoutRequest(SessionID sessionId)
			throws SerializationException {
		this.append(FakeCommonSerializer.SERIALIZE_LOGOUT_REQUEST, new Object[]{
				sessionId
		});
		return (String)this.retrieveReturn(FakeCommonSerializer.SERIALIZE_LOGOUT_REQUEST);
	}
	
	@Override
	public User parseGetUserInformationResponse(String responseText) {
		this.append(FakeCommonSerializer.PARSE_GET_USER_INFORMATION_RESPONSE, new Object[]{
				responseText
		});
		return (User)this.retrieveReturn(FakeCommonSerializer.PARSE_GET_USER_INFORMATION_RESPONSE);
	}

	@Override
	public String serializeGetUserInformationRequest(SessionID sessionId) {
		this.append(FakeCommonSerializer.SERIALIZE_GET_USER_INFORMATION_REQUEST, new Object[]{
				sessionId
		});
		return (String)this.retrieveReturn(FakeCommonSerializer.SERIALIZE_GET_USER_INFORMATION_REQUEST);
	}

	@SuppressWarnings("unused")
	protected void throwException(JSONObject responseObject) throws WebLabServerException {
	}

	@SuppressWarnings("unused")
	protected WebLabServerException buildException(final String faultCode, final String faultString) {
		return null;
	}

	@SuppressWarnings("unused")
	protected String json2string(JSONValue value) throws SerializationException {
		return null;
	}

	@SuppressWarnings("unused")
	protected double json2double(JSONValue value) throws SerializationException {
		return 0;
	}

	@SuppressWarnings("unused")
	protected int json2int(JSONValue value) throws SerializationException {
		return 0;
	}	
}
