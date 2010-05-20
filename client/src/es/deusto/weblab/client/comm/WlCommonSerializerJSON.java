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

import com.google.gwt.json.client.JSONArray;
import com.google.gwt.json.client.JSONBoolean;
import com.google.gwt.json.client.JSONException;
import com.google.gwt.json.client.JSONNumber;
import com.google.gwt.json.client.JSONObject;
import com.google.gwt.json.client.JSONParser;
import com.google.gwt.json.client.JSONString;
import com.google.gwt.json.client.JSONValue;

import es.deusto.weblab.client.comm.exceptions.SerializationException;
import es.deusto.weblab.client.comm.exceptions.WlServerException;
import es.deusto.weblab.client.comm.exceptions.core.SessionNotFoundException;
import es.deusto.weblab.client.comm.exceptions.core.UserProcessingException;
import es.deusto.weblab.client.comm.exceptions.login.InvalidCredentialsException;
import es.deusto.weblab.client.comm.exceptions.login.LoginException;
import es.deusto.weblab.client.dto.SessionID;
import es.deusto.weblab.client.dto.users.Role;
import es.deusto.weblab.client.dto.users.User;

public abstract class WlCommonSerializerJSON implements IWlCommonSerializer {

	public static final String ERR_CLIENT_INVALID_CREDENTIALS = "JSON:Client.InvalidCredentials";
	public static final String ERR_CLIENT_SESSION_NOT_FOUND = "JSON:Client.SessionNotFound";
	public static final String ERR_LOGIN_GENERAL = "JSON:Server.Login";
	public static final String ERR_UPS_GENERAL = "JSON:Server.UserProcessing";
	public static final String ERR_WEBLAB_GENERAL = "JSON:Server.WebLab";
	public static final String ERR_VOODOO_GENERAL = "JSON:Server.Voodoo";
	public static final String ERR_PYTHON_GENERAL = "JSON:Server.Python";

    public String serializeRequest(String method, JSONObject params){
		final JSONObject request = new JSONObject();
		request.put("params", params);
		request.put("method", new JSONString(method));
		return request.toString();
    }
    
	public SessionID parseLoginResponse(String responseText)
			throws SerializationException, InvalidCredentialsException,
			LoginException, UserProcessingException, WlServerException {
				// "{\"result\": {\"id\": \"svAsc-rCIKLP1qeU\"}}"
				final JSONObject result = this.parseResultObject(responseText);
				String sessionIdStr = this.json2string(result.get("id"));
				final SessionID sessionId = new SessionID(sessionIdStr);
				return sessionId;
			}

	public String serializeLoginRequest(String username, String password)
			throws SerializationException {
				// {"params": {"username": "student1", "password": "password"}, "method": "login"}
				final JSONObject params = new JSONObject();
				params.put("username", new JSONString(username));
				params.put("password", new JSONString(password));
				return this.serializeRequest("login", params);
			}
	
    public void parseLogoutResponse(String responseText)
	    throws SerializationException, WlServerException {
		this.parseResultObject(responseText);
    }
    
    public String serializeLogoutRequest(SessionID sessionId) throws SerializationException {
		// {"params": {"session_id": {"id": "RqpLBRTlRW8ZVN1d"}}, "method": "logout"}
		final JSONObject params = new JSONObject();
		params.put("session_id", serializeSessionId(sessionId));
		return this.serializeRequest("logout", params);
    }
    
    public User parseGetUserInformationResponse(String responseText)
    	throws SerializationException, SessionNotFoundException, UserProcessingException, WlServerException {
		//"{\"result\": {\"login\": \"student1\", \"email\": \"porduna@tecnologico.deusto.es\", 
		// \"full_name\": \"Name of student 1\", \"role\": {\"name\": \"student\"}}, \"is_exception\": false}"
		final JSONObject result = this.parseResultObject(responseText);
		final String login    = this.json2string(result.get("login"));
		final String email    = this.json2string(result.get("email"));
		final String fullName = this.json2string(result.get("full_name"));
		
	    JSONValue roleValue = result.get("role");
	    if(roleValue == null)
	    	throw new SerializationException("Expected role field in UserInformation");
	    JSONObject jsonRole = roleValue.isObject();
	    if(jsonRole == null)
	    	throw new SerializationException("Expected JSON Object as Role, found: " + roleValue);
	    final String role_name = this.json2string(jsonRole.get("name"));
		
	    final Role role = new Role(role_name);
	    
		return new User(login, fullName, email, role);
	}    

    public String serializeGetUserInformationRequest(SessionID sessionId) throws SerializationException {
		final JSONObject params = new JSONObject();
		params.put("session_id", this.serializeSessionId(sessionId));
		return this.serializeRequest("get_user_information", params);
    }
    
    // General

    protected JSONObject serializeSessionId(SessionID sessionId) {
		final JSONObject session_id = new JSONObject();
		session_id.put("id", new JSONString(sessionId.getRealId()));
		return session_id;
    }
    
	private void throwException(JSONObject responseObject) throws WlServerException {
		// {"message": "No UserAuth found", "code": "JSON:Server.WebLab", "is_exception": true}
		final String faultCode = responseObject.get("code").isString().stringValue();
		final String faultString = responseObject.get("message").isString().stringValue();
		
		throw this.buildException(faultCode, faultString);
	}

	protected WlServerException buildException(final String faultCode, final String faultString) {
		if(faultCode.equals(WlCommonSerializerJSON.ERR_CLIENT_INVALID_CREDENTIALS)){
		    return new InvalidCredentialsException(faultString);
		}else if(faultCode.equals(WlCommonSerializerJSON.ERR_CLIENT_SESSION_NOT_FOUND)){
		    return new SessionNotFoundException(faultString);
		}else if(faultCode.equals(WlCommonSerializerJSON.ERR_LOGIN_GENERAL)){
		    return new LoginException(faultString);
		}else if(faultCode.equals(WlCommonSerializerJSON.ERR_UPS_GENERAL)){
		    return new UserProcessingException(faultString);
		}else if(faultCode.equals(WlCommonSerializerJSON.ERR_WEBLAB_GENERAL)){
		    return new WlServerException(faultString);
		}else if(faultCode.equals(WlCommonSerializerJSON.ERR_VOODOO_GENERAL)){
		    return new WlServerException(faultString);
		}else if(faultCode.equals(WlCommonSerializerJSON.ERR_PYTHON_GENERAL)){
		    return new WlServerException(faultString);
		}else{
		    return new WlServerException(faultString);    
		}
	}

	protected JSONObject parseResultObject(String response)
			throws SerializationException, WlServerException {
				final JSONValue result = parseResult(response);
				final JSONObject resultObject = result.isObject();
				if(resultObject == null)
				    throw new SerializationException("Expecting an object as a result; found: " + result);
				return resultObject;
			}

	protected JSONArray parseResultArray(String response)
			throws SerializationException, WlServerException {
				final JSONValue result = parseResult(response);
				final JSONArray resultArray = result.isArray();
				if(resultArray == null)
				    throw new SerializationException("Expecting an array as a result; found: " + result);
				return resultArray;
			}

	private JSONValue parseResult(String response) throws SerializationException,
			WlServerException {
				final JSONValue value;
				try {
				    value = JSONParser.parse(response);
				} catch (IllegalArgumentException e) {
				    throw new SerializationException("Invalid response: " + e.getMessage());
				} catch (JSONException e){
				    throw new SerializationException("Invalid response: " + e.getMessage());
				}
				final JSONObject responseObject = value.isObject();
				if(responseObject == null)
				    throw new SerializationException("Expecting an object as a response; found: " + response);
				
				final JSONValue isException = responseObject.get("is_exception");
				final JSONBoolean isExceptionB = isException.isBoolean();
				if(isExceptionB.booleanValue())
				    throwException(responseObject);
				
				final JSONValue result = responseObject.get("result");
				if(result == null)
				    throw new SerializationException("Expecting 'result'; not found");
				return result;
			}

	protected String json2string(JSONValue value) throws SerializationException {
		if(value == null)
		    throw new SerializationException("String expected, found null");
		JSONString jsonstring = value.isString();
		if(jsonstring == null)
		    throw new SerializationException("String expected, found: " + value);
		return jsonstring.stringValue();
	}

	protected double json2double(JSONValue value) throws SerializationException {
		if(value == null)
		    throw new SerializationException("Double expected, found null");
		JSONNumber jsonnumber = value.isNumber();
		if(jsonnumber == null)
		    throw new SerializationException("Double expected, found: " + value);
		return jsonnumber.doubleValue();
	}

	protected int json2int(JSONValue value) throws SerializationException {
		if(value == null)
		    throw new SerializationException("Int expected, found null");
		JSONNumber jsonnumber = value.isNumber();
		if(jsonnumber == null)
		    throw new SerializationException("Int expected, found: " + value);
		return (int)jsonnumber.doubleValue();
	}

}
