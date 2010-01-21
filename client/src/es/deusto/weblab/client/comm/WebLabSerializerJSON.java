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
*
*/

package es.deusto.weblab.client.comm;

import com.google.gwt.core.client.GWT;
import com.google.gwt.i18n.client.DateTimeFormat;
import com.google.gwt.json.client.JSONArray;
import com.google.gwt.json.client.JSONBoolean;
import com.google.gwt.json.client.JSONException;
import com.google.gwt.json.client.JSONNumber;
import com.google.gwt.json.client.JSONObject;
import com.google.gwt.json.client.JSONParser;
import com.google.gwt.json.client.JSONString;
import com.google.gwt.json.client.JSONValue;

import es.deusto.weblab.client.dto.SessionID;
import es.deusto.weblab.client.dto.experiments.Category;
import es.deusto.weblab.client.dto.experiments.Command;
import es.deusto.weblab.client.dto.experiments.EmptyResponseCommand;
import es.deusto.weblab.client.dto.experiments.Experiment;
import es.deusto.weblab.client.dto.experiments.ExperimentAllowed;
import es.deusto.weblab.client.dto.experiments.ExperimentID;
import es.deusto.weblab.client.dto.experiments.ResponseCommand;
import es.deusto.weblab.client.dto.reservations.CancellingReservationStatus;
import es.deusto.weblab.client.dto.reservations.ConfirmedReservationStatus;
import es.deusto.weblab.client.dto.reservations.ReservationStatus;
import es.deusto.weblab.client.dto.reservations.WaitingConfirmationReservationStatus;
import es.deusto.weblab.client.dto.reservations.WaitingInstancesReservationStatus;
import es.deusto.weblab.client.dto.reservations.WaitingReservationStatus;
import es.deusto.weblab.client.dto.users.AdminUser;
import es.deusto.weblab.client.dto.users.ProfessorUser;
import es.deusto.weblab.client.dto.users.StudentUser;
import es.deusto.weblab.client.dto.users.User;
import es.deusto.weblab.client.exceptions.comm.SerializationException;
import es.deusto.weblab.client.exceptions.comm.WlServerException;
import es.deusto.weblab.client.exceptions.comm.login.InvalidCredentialsException;
import es.deusto.weblab.client.exceptions.comm.login.LoginException;
import es.deusto.weblab.client.exceptions.comm.user_processing.NoCurrentReservationException;
import es.deusto.weblab.client.exceptions.comm.user_processing.SessionNotFoundException;
import es.deusto.weblab.client.exceptions.comm.user_processing.UnknownExperimentIdException;
import es.deusto.weblab.client.exceptions.comm.user_processing.UserProcessingException;

public class WebLabSerializerJSON implements IWebLabSerializer {
    
	public static final String ERR_CLIENT_INVALID_CREDENTIALS    = "JSON:Client.InvalidCredentials";
	public static final String ERR_CLIENT_SESSION_NOT_FOUND      = "JSON:Client.SessionNotFound";
	public static final String ERR_CLIENT_NO_CURRENT_RESERVATION = "JSON:Client.NoCurrentReservation";
	public static final String ERR_CLIENT_UNKNOWN_EXPERIMENT_ID  = "JSON:Client.UnknownExperimentId";
	public static final String ERR_LOGIN_GENERAL                 = "JSON:Server.Login";
	public static final String ERR_UPS_GENERAL                   = "JSON:Server.UserProcessing";
	public static final String ERR_WEBLAB_GENERAL                = "JSON:Server.WebLab";
	public static final String ERR_VOODOO_GENERAL                = "JSON:Server.Voodoo";
	public static final String ERR_PYTHON_GENERAL                = "JSON:Server.Python";
	
	public WebLabSerializerJSON(){}
	
    // Parsing

    public void parseFinishedExperimentResponse(String responseText)
    	throws SerializationException, SessionNotFoundException, NoCurrentReservationException, UserProcessingException, WlServerException {
	this.parseResultObject(responseText);
    }

    public ReservationStatus parseGetReservationStatusResponse(String responseText)
    	throws SerializationException, SessionNotFoundException, NoCurrentReservationException, UserProcessingException, WlServerException {
	// "{\"result\": {\"status\": \"Reservation::waiting_confirmation\"}, \"is_exception\": false}"
	final JSONObject result = parseResultObject(responseText);
	return parseReservationStatus(result);
    }

    private ReservationStatus parseReservationStatus(final JSONObject result)
	    throws SerializationException {
	final String status = this.json2string(result.get("status"));
	if(status.equals("Reservation::waiting_confirmation")){
	    return new WaitingConfirmationReservationStatus();
	}else if(status.equals("Reservation::confirmed")){
	    double time = this.json2double(result.get("time"));
	    return new ConfirmedReservationStatus((int)time);
	}else if(status.equals("Reservation::waiting")){
	    int position = this.json2int(result.get("position"));
	    return new WaitingReservationStatus(position);
	}else if(status.equals("Reservation::cancelling")){
	    return new CancellingReservationStatus();
	}else if(status.equals("Reservation::waiting_instances")){
	    int position = this.json2int(result.get("position"));
	    return new WaitingInstancesReservationStatus(position);
	}else
	    throw new SerializationException("Unknown status: " + status);
    }
    
    public User parseGetUserInformationResponse(String responseText)
	    throws SerializationException, SessionNotFoundException, UserProcessingException, WlServerException {
	//"{\"result\": {\"login\": \"student1\", \"email\": \"porduna@tecnologico.deusto.es\", 
	// \"full_name\": \"Name of student 1\", \"user_type\": \"student\"}, \"is_exception\": false}"
	final JSONObject result = this.parseResultObject(responseText);
	final String login    = this.json2string(result.get("login"));
	final String email    = this.json2string(result.get("email"));
	final String fullName = this.json2string(result.get("full_name"));
	final String userType = this.json2string(result.get("user_type"));
	final User user; 
	if(userType.equals("student"))
	    user = new StudentUser();
	else if(userType.equals("administrator"))
	    user = new AdminUser();
	else if(userType.equals("professor"))
	    user = new ProfessorUser();
	else
	    throw new SerializationException("Unrecognized user type: " + userType);
	user.setLogin(login);
	user.setFullName(fullName);
	user.setEmail(email);
	return user;
    }

    public ExperimentAllowed[] parseListExperimentsResponse(String responseText)
    	throws SerializationException, SessionNotFoundException, UserProcessingException, WlServerException {	
//	"{\"result\": [" +
//		"{\"experiment\": {\"category\": {\"name\": \"Dummy experiments\"}, \"owner\": \"porduna@tecnologico.deusto.es\", " +
//			"\"name\": \"ud-dummy\", \"end_date\": \"2008-01-01\", \"start_date\": \"2007-08-17\"}, \"time_allowed\": 30.0}, " +
//		"{\"experiment\": {\"category\": {\"name\": \"FPGA experiments\"}, \"owner\": \"porduna@tecnologico.deusto.es\", " +
//			"\"name\": \"ud-fpga\", \"end_date\": \"2006-01-01\", \"start_date\": \"2005-01-01\"}, \"time_allowed\": 30.0}" +
//	"], \"is_exception\": false}"
	JSONArray result = this.parseResultArray(responseText);
	ExperimentAllowed [] experiments = new ExperimentAllowed[result.size()];
	for(int i = 0; i < result.size(); ++i){
	    JSONValue value = result.get(i);
	    JSONObject jsonExperimentAllowed = value.isObject();
	    if(jsonExperimentAllowed == null)
		throw new SerializationException("Expected JSON Object as ExperimentAllowed, found: " + value);
	    JSONValue jsonExperimentValue = jsonExperimentAllowed.get("experiment");
	    if(jsonExperimentValue == null)
		throw new SerializationException("Expected experiment field in ExperimentAllowed");
	    JSONObject jsonExperiment = jsonExperimentValue.isObject();
	    if(jsonExperiment == null)
		throw new SerializationException("Expected JSON Object as Experiment, found: " + jsonExperimentValue);
	    JSONValue jsonCategoryValue = jsonExperiment.get("category");
	    if(jsonCategoryValue == null)
		throw new SerializationException("Expected category field in Experiment");
	    JSONObject jsonCategory = jsonCategoryValue.isObject();
	    if(jsonCategory == null)
		throw new SerializationException("Expected JSON Object as Category, found: " + jsonCategoryValue);
	    
	    Category category = new Category(this.json2string(jsonCategory.get("name")));
	    
	    Experiment experiment = new Experiment();
	    experiment.setCategory(category);
	    experiment.setName(this.json2string(jsonExperiment.get("name")));
	    experiment.setOwner(this.json2string(jsonExperiment.get("owner")));
	    
	    String startDateString = this.json2string(jsonExperiment.get("start_date"));
	    String endDateString   = this.json2string(jsonExperiment.get("end_date"));
	    
	    DateTimeFormat formatter1 = DateTimeFormat.getFormat("yyyy-MM-dd");
	    DateTimeFormat formatter2 = DateTimeFormat.getFormat("yyyy-MM-dd HH:mm:ss");
	    
	    try{
		experiment.setStartDate(formatter1.parse(startDateString));
		experiment.setEndDate(formatter1.parse(endDateString));
	    }catch(IllegalArgumentException iae){
		try{
		    experiment.setStartDate(formatter2.parse(startDateString));
		    experiment.setEndDate(formatter2.parse(endDateString));
		}catch(IllegalArgumentException iae2){
		    throw new SerializationException("Couldn't parse date: " + startDateString + "; or: " + endDateString);
		}
	    }
	    
	    ExperimentAllowed experimentAllowed = new ExperimentAllowed();
	    experimentAllowed.setTimeAllowed(this.json2int(jsonExperimentAllowed.get("time_allowed")));
	    experimentAllowed.setExperiment(experiment);
	    
	    experiments[i] = experimentAllowed;
	}
	return experiments;
    }

    public SessionID parseLoginResponse(String responseText)
    	throws SerializationException, InvalidCredentialsException, LoginException, UserProcessingException, WlServerException {
	// "{\"result\": {\"id\": \"svAsc-rCIKLP1qeU\"}}"
	final JSONObject result = this.parseResultObject(responseText);
	String sessionIdStr = this.json2string(result.get("id"));
	final SessionID sessionId = new SessionID(sessionIdStr);
	return sessionId;
    }

    public void parseLogoutResponse(String responseText)
	    throws SerializationException, WlServerException {
	this.parseResultObject(responseText);
    }

    public void parsePollResponse(String responseText)
	    throws SerializationException, SessionNotFoundException, NoCurrentReservationException, UserProcessingException, WlServerException {
	this.parseResultObject(responseText);
    }

    public ReservationStatus parseReserveExperimentResponse(String responseText)
    	throws SerializationException, SessionNotFoundException, UnknownExperimentIdException, UserProcessingException, WlServerException {
	final JSONObject result = this.parseResultObject(responseText);
	return this.parseReservationStatus(result);
    }

    public ResponseCommand parseSendCommandResponse(String responseText)
	    throws SerializationException, SessionNotFoundException, NoCurrentReservationException, UserProcessingException, WlServerException {
	// "{\"result\": {\"commandstring\": null}, \"is_exception\": false}"
	final JSONObject result = this.parseResultObject(responseText);
	JSONValue value = result.get("commandstring");
	if(value.isNull() != null)
	    return new EmptyResponseCommand();
	String commandString = this.json2string(value);
	return new ResponseCommand(commandString);
    }

    public ResponseCommand parseSendFileResponse(String responseText)
	    throws SerializationException, SessionNotFoundException, NoCurrentReservationException, UserProcessingException, WlServerException {
	if(!GWT.isScript() && responseText == null)
		return new EmptyResponseCommand();
	
	final String startMessage = "<body>";
	final String endMessage = "</body>";
	
	final int startPoint = responseText.trim().toLowerCase().indexOf(startMessage) + startMessage.length();
	final int endPoint = responseText.trim().toLowerCase().lastIndexOf(endMessage);
	
	// Sometimes the browsers provide us directly the body of the message, sometimes it provides the full HTML message
	final String parsedResponse;
	if(startPoint < 0 || endPoint < 0 || startPoint > endPoint)
	    parsedResponse = responseText;
	else
	    parsedResponse = responseText.trim().substring(startPoint, endPoint);
	
	final int firstAT = parsedResponse.indexOf("@");
	if(firstAT < 0)
	    throw new SerializationException("Sending file failed: response should have at least one '@' symbol");
	final String firstWord = parsedResponse.substring(0, firstAT);
	final String restOfText = parsedResponse.substring(firstAT + 1);
	
	if(firstWord.toLowerCase().equals("success")){
	    return new ResponseCommand(restOfText);
	}else if(firstWord.toLowerCase().equals("error")){
	    final int secondAT = restOfText.indexOf("@");
	    final String faultCode = restOfText.substring(0, secondAT);
	    final String faultString = restOfText.substring(secondAT + 1);
	    final String jsonizedFaultCode = "JSON" + faultCode.substring(faultCode.indexOf(":"));
	    throw this.buildException(jsonizedFaultCode, faultString);
	}else
	    throw new SerializationException("Sending file failed: first element must be 'success' or 'error'");
    }

    public String serializeFinishedExperimentRequest(SessionID sessionId)
	    throws SerializationException {
	// "{\"params\":{\"session_id\":{\"id\":\"" + MESSAGE + "\"}}, \"method\":\"finished_experiment\"}",
	final JSONObject params = new JSONObject();
	params.put("session_id", this.serializeSessionId(sessionId));
	return this.serializeRequest("finished_experiment", params);
    }

    public String serializeGetReservationStatusRequest(SessionID sessionId)
	    throws SerializationException {
	final JSONObject params = new JSONObject();
	params.put("session_id", this.serializeSessionId(sessionId));
	return this.serializeRequest("get_reservation_status", params);
    }

    public String serializeGetUserInformationRequest(SessionID sessionId)
	    throws SerializationException {
	final JSONObject params = new JSONObject();
	params.put("session_id", this.serializeSessionId(sessionId));
	return this.serializeRequest("get_user_information", params);
    }

    public String serializeListExperimentsRequest(SessionID sessionId)
	    throws SerializationException {
	final JSONObject params = new JSONObject();
	params.put("session_id", this.serializeSessionId(sessionId));
	return this.serializeRequest("list_experiments", params);
    }
    
    public String serializeLoginRequest(String username, String password)
	    throws SerializationException {
	// {"params": {"username": "student1", "password": "password"}, "method": "login"}
	final JSONObject params = new JSONObject();
	params.put("username", new JSONString(username));
	params.put("password", new JSONString(password));
	return this.serializeRequest("login", params);
    }

    public String serializeLogoutRequest(SessionID sessionId)
	    throws SerializationException {
	// {"params": {"session_id": {"id": "RqpLBRTlRW8ZVN1d"}}, "method": "logout"}
	final JSONObject params = new JSONObject();
	params.put("session_id", serializeSessionId(sessionId));
	return this.serializeRequest("logout", params);
    }

    public String serializePollRequest(SessionID sessionId)
	    throws SerializationException {
	final JSONObject params = new JSONObject();
	params.put("session_id", serializeSessionId(sessionId));
	return this.serializeRequest("poll", params);
    }

    public String serializeReserveExperimentRequest(SessionID sessionId,
	    ExperimentID experimentId) throws SerializationException {
	//{"params": {"session_id": {"id": "svAsc-rCIKLP1qeU"}, 
	//  "experiment_id": {"exp_name": "ud-dummy", "cat_name": "Dummy experiments"}}, 
	// "method": "reserve_experiment"}
	final JSONObject params = new JSONObject();
	params.put("session_id", this.serializeSessionId(sessionId));
	final JSONObject jsonExperimentId = new JSONObject();
	jsonExperimentId.put("exp_name", new JSONString(experimentId.getExperimentName()));
	jsonExperimentId.put("cat_name", new JSONString(experimentId.getCategory().getCategory()));
	params.put("experiment_id", jsonExperimentId);
	return this.serializeRequest("reserve_experiment", params);
    }

    public String serializeSendCommandRequest(SessionID sessionId,
	    Command command) throws SerializationException {
	final JSONObject params = new JSONObject();
	params.put("session_id", this.serializeSessionId(sessionId));
	final JSONObject commandjson = new JSONObject();
	commandjson.put("commandstring", new JSONString(command.getCommandString()));
	params.put("command", commandjson);
	return this.serializeRequest("send_command", params);
    }

    // General
    
    private String serializeRequest(String method, JSONObject params){
	final JSONObject request = new JSONObject();
	request.put("params", params);
	request.put("method", new JSONString(method));
	return request.toString();
    }
    
    private JSONObject serializeSessionId(SessionID sessionId) {
	final JSONObject session_id = new JSONObject();
	session_id.put("id", new JSONString(sessionId.getRealId()));
	return session_id;
    }
    
    private void throwException(JSONObject responseObject) throws WlServerException{
	// {"message": "No UserAuth found", "code": "JSON:Server.WebLab", "is_exception": true}
	final String faultCode = responseObject.get("code").isString().stringValue();
	final String faultString = responseObject.get("message").isString().stringValue();
	
	throw this.buildException(faultCode, faultString);
    }

    private WlServerException buildException(final String faultCode, final String faultString) {
		if(faultCode.equals(WebLabSerializerJSON.ERR_CLIENT_INVALID_CREDENTIALS)){
		    return new InvalidCredentialsException(faultString);
		}else if(faultCode.equals(WebLabSerializerJSON.ERR_CLIENT_SESSION_NOT_FOUND)){
		    return new SessionNotFoundException(faultString);
		}else if(faultCode.equals(WebLabSerializerJSON.ERR_CLIENT_NO_CURRENT_RESERVATION)){
		    return new NoCurrentReservationException(faultString);
		}else if(faultCode.equals(WebLabSerializerJSON.ERR_CLIENT_UNKNOWN_EXPERIMENT_ID)){
		    return new UnknownExperimentIdException(faultString);
		}else if(faultCode.equals(WebLabSerializerJSON.ERR_LOGIN_GENERAL)){
		    return new LoginException(faultString);
		}else if(faultCode.equals(WebLabSerializerJSON.ERR_UPS_GENERAL)){
		    return new UserProcessingException(faultString);
		}else if(faultCode.equals(WebLabSerializerJSON.ERR_WEBLAB_GENERAL)){
		    return new WlServerException(faultString);
		}else if(faultCode.equals(WebLabSerializerJSON.ERR_VOODOO_GENERAL)){
		    return new WlServerException(faultString);
		}else if(faultCode.equals(WebLabSerializerJSON.ERR_PYTHON_GENERAL)){
		    return new WlServerException(faultString);
		}else{
		    return new WlServerException(faultString);    
		}
    }
    
    private JSONObject parseResultObject(String response) throws SerializationException, WlServerException{
	final JSONValue result = parseResult(response);
	final JSONObject resultObject = result.isObject();
	if(resultObject == null)
	    throw new SerializationException("Expecting an object as a result; found: " + result);
	return resultObject;
    }

    private JSONArray parseResultArray(String response) throws SerializationException, WlServerException{
	final JSONValue result = parseResult(response);
	final JSONArray resultArray = result.isArray();
	if(resultArray == null)
	    throw new SerializationException("Expecting an array as a result; found: " + result);
	return resultArray;
    }

    private JSONValue parseResult(String response)
	    throws SerializationException, WlServerException {
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
    
    

    private String json2string(JSONValue value) throws SerializationException{
	if(value == null)
	    throw new SerializationException("String expected, found null");
	JSONString jsonstring = value.isString();
	if(jsonstring == null)
	    throw new SerializationException("String expected, found: " + value);
	return jsonstring.stringValue();
    }
    
    private double json2double(JSONValue value) throws SerializationException{
	if(value == null)
	    throw new SerializationException("Double expected, found null");
	JSONNumber jsonnumber = value.isNumber();
	if(jsonnumber == null)
	    throw new SerializationException("Double expected, found: " + value);
	return jsonnumber.doubleValue();
    }

    private int json2int(JSONValue value) throws SerializationException{
	if(value == null)
	    throw new SerializationException("Int expected, found null");
	JSONNumber jsonnumber = value.isNumber();
	if(jsonnumber == null)
	    throw new SerializationException("Int expected, found: " + value);
	return (int)jsonnumber.doubleValue();
    }
}
