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
