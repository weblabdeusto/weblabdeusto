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

package es.deusto.weblab.client.comm;

import com.google.gwt.json.client.JSONObject;
import com.google.gwt.json.client.JSONValue;

import es.deusto.weblab.client.comm.exceptions.SerializationException;
import es.deusto.weblab.client.comm.exceptions.WlServerException;
import es.deusto.weblab.client.dto.SessionID;
import es.deusto.weblab.client.dto.users.User;
import es.deusto.weblab.client.testing.util.WlFake;

public class FakeWlCommonSerializer extends WlFake implements IWlCommonSerializer {

	public static final String PARSE_LOGIN_RESPONSE                     = "FakeWebLabSerializer::parseLoginResponse";
	public static final String SERIALIZE_LOGIN_REQUEST                  = "FakeWebLabSerializer::serializeLoginRequest";
	public static final String PARSE_LOGOUT_RESPONSE                    = "FakeWebLabSerializer::parseLogoutResponse";
	public static final String SERIALIZE_LOGOUT_REQUEST                 = "FakeWebLabSerializer::serializeLogoutRequest";
	public static final String PARSE_GET_USER_INFORMATION_RESPONSE      = "FakeWebLabSerializer::parseGetUserInformation";
	public static final String SERIALIZE_GET_USER_INFORMATION_REQUEST   = "FakeWebLabSerializer::serializeGetUserInformationRequest";

	
	@Override
	public SessionID parseLoginResponse(String responseText) throws SerializationException {
		this.append(FakeWlCommonSerializer.PARSE_LOGIN_RESPONSE, new Object[]{responseText});
		return (SessionID)this.retrieveReturn(FakeWlCommonSerializer.PARSE_LOGIN_RESPONSE);
	}

	@Override
	public String serializeLoginRequest(String username, String password) throws SerializationException {
		this.append(FakeWlCommonSerializer.SERIALIZE_LOGIN_REQUEST, new Object[]{	username, password});
		return (String)this.retrieveReturn(FakeWlCommonSerializer.SERIALIZE_LOGIN_REQUEST);
	}
	
	public void parseLogoutResponse(String responseText)
		throws SerializationException {
		this.append(FakeWlCommonSerializer.PARSE_LOGOUT_RESPONSE, new Object[]{
				responseText
		});
	}

	public String serializeLogoutRequest(SessionID sessionId)
			throws SerializationException {
		this.append(FakeWlCommonSerializer.SERIALIZE_LOGOUT_REQUEST, new Object[]{
				sessionId
		});
		return (String)this.retrieveReturn(FakeWlCommonSerializer.SERIALIZE_LOGOUT_REQUEST);
	}
	
	public User parseGetUserInformationResponse(String responseText) {
		this.append(FakeWlCommonSerializer.PARSE_GET_USER_INFORMATION_RESPONSE, new Object[]{
				responseText
		});
		return (User)this.retrieveReturn(FakeWlCommonSerializer.PARSE_GET_USER_INFORMATION_RESPONSE);
	}

	public String serializeGetUserInformationRequest(SessionID sessionId) {
		this.append(FakeWlCommonSerializer.SERIALIZE_GET_USER_INFORMATION_REQUEST, new Object[]{
				sessionId
		});
		return (String)this.retrieveReturn(FakeWlCommonSerializer.SERIALIZE_GET_USER_INFORMATION_REQUEST);
	}

	@SuppressWarnings("unused")
	protected void throwException(JSONObject responseObject) throws WlServerException {
	}

	@SuppressWarnings("unused")
	protected WlServerException buildException(final String faultCode, final String faultString) {
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
