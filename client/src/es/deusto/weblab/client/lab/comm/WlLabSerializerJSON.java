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

package es.deusto.weblab.client.lab.comm;

import com.google.gwt.core.client.GWT;
import com.google.gwt.i18n.client.DateTimeFormat;
import com.google.gwt.json.client.JSONArray;
import com.google.gwt.json.client.JSONObject;
import com.google.gwt.json.client.JSONString;
import com.google.gwt.json.client.JSONValue;

import es.deusto.weblab.client.comm.WebLabSerializerJSON;
import es.deusto.weblab.client.comm.exceptions.SerializationException;
import es.deusto.weblab.client.comm.exceptions.WlServerException;
import es.deusto.weblab.client.comm.exceptions.core.SessionNotFoundException;
import es.deusto.weblab.client.comm.exceptions.core.UserProcessingException;
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
import es.deusto.weblab.client.dto.users.Role;
import es.deusto.weblab.client.dto.users.User;
import es.deusto.weblab.client.lab.comm.exceptions.NoCurrentReservationException;
import es.deusto.weblab.client.lab.comm.exceptions.UnknownExperimentIdException;

public class WlLabSerializerJSON extends WebLabSerializerJSON implements IWlLabSerializer {
    
	public WlLabSerializerJSON(){}
	
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
		
	    final Role role = new Role();
	    role.setName(role_name);
	    
		final User user = new User();
		user.setLogin(login);
		user.setFullName(fullName);
		user.setEmail(email);
		user.setRole(role);
		return user;
    }

    public ExperimentAllowed[] parseListExperimentsResponse(String responseText)
    	throws SerializationException, SessionNotFoundException, UserProcessingException, WlServerException {	
	//	"{\"result\": [" +
	//		"{\"experiment\": {\"category\": {\"name\": \"Dummy experiments\"}, " +
	//			"\"name\": \"ud-dummy\", \"end_date\": \"2008-01-01\", \"start_date\": \"2007-08-17\"}, \"time_allowed\": 30.0}, " +
	//		"{\"experiment\": {\"category\": {\"name\": \"FPGA experiments\"}, " +
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
		    
		    String startDateString = this.json2string(jsonExperiment.get("start_date"));
		    String endDateString   = this.json2string(jsonExperiment.get("end_date"));
		    
		    DateTimeFormat formatter1 = DateTimeFormat.getFormat("yyyy-MM-dd");
		    DateTimeFormat formatter2 = DateTimeFormat.getFormat("yyyy-MM-dd HH:mm:ss");
		    DateTimeFormat formatter3 = DateTimeFormat.getFormat("yyyy-MM-ddTHH:mm:ss");
		    
		    try{
			experiment.setStartDate(formatter1.parse(startDateString));
			experiment.setEndDate(formatter1.parse(endDateString));
		    }catch(IllegalArgumentException iae){
				try{
				    experiment.setStartDate(formatter2.parse(startDateString));
				    experiment.setEndDate(formatter2.parse(endDateString));
				}catch(IllegalArgumentException iae2){
					try{
					    experiment.setStartDate(formatter3.parse(startDateString));
					    experiment.setEndDate(formatter3.parse(endDateString));
					}catch(IllegalArgumentException iae3){
					    throw new SerializationException("Couldn't parse date: " + startDateString + "; or: " + endDateString);
					}
				}
		    }
		    
		    ExperimentAllowed experimentAllowed = new ExperimentAllowed();
		    experimentAllowed.setTimeAllowed(this.json2int(jsonExperimentAllowed.get("time_allowed")));
		    experimentAllowed.setExperiment(experiment);
		    
		    experiments[i] = experimentAllowed;
		}
		return experiments;
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
    
    private JSONObject serializeSessionId(SessionID sessionId) {
		final JSONObject session_id = new JSONObject();
		session_id.put("id", new JSONString(sessionId.getRealId()));
		return session_id;
    }
}
