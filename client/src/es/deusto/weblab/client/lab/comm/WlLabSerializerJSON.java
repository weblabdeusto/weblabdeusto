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

import es.deusto.weblab.client.comm.WlCommonSerializerJSON;
import es.deusto.weblab.client.comm.exceptions.SerializationException;
import es.deusto.weblab.client.comm.exceptions.WlServerException;
import es.deusto.weblab.client.comm.exceptions.core.SessionNotFoundException;
import es.deusto.weblab.client.comm.exceptions.core.UserProcessingException;
import es.deusto.weblab.client.dto.SessionID;
import es.deusto.weblab.client.dto.experiments.AsyncRequestStatus;
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
import es.deusto.weblab.client.lab.comm.exceptions.NoCurrentReservationException;
import es.deusto.weblab.client.lab.comm.exceptions.UnknownExperimentIdException;

public class WlLabSerializerJSON extends WlCommonSerializerJSON implements IWlLabSerializer {
	
	public static final String ERR_CLIENT_NO_CURRENT_RESERVATION = "JSON:Client.NoCurrentReservation";
	public static final String ERR_CLIENT_UNKNOWN_EXPERIMENT_ID = "JSON:Client.UnknownExperimentId";
    
	public WlLabSerializerJSON(){}
	
    // Parsing

    @Override
	public void parseFinishedExperimentResponse(String responseText)
    	throws SerializationException, SessionNotFoundException, NoCurrentReservationException, UserProcessingException, WlServerException {
    	this.parseResultObject(responseText);
    }

    @Override
	public ReservationStatus parseGetReservationStatusResponse(String responseText)
    	throws SerializationException, SessionNotFoundException, NoCurrentReservationException, UserProcessingException, WlServerException {
		// "{\"result\": {\"status\": \"Reservation::waiting_confirmation\"}, \"is_exception\": false}"
		final JSONObject result = this.parseResultObject(responseText);
		return this.parseReservationStatus(result);
    }
    
    @Override
	public AsyncRequestStatus [] parseCheckAsyncCommandStatusResponse(String responseText) 
		throws SerializationException {
    	
    	// TODO: Implement this.
    	
    	return null;
	}

    private ReservationStatus parseReservationStatus(final JSONObject result)
	    throws SerializationException {
		final String status = this.json2string(result.get("status"));
		if(status.equals("Reservation::waiting_confirmation")){
		    return new WaitingConfirmationReservationStatus();
		}else if(status.equals("Reservation::confirmed")){
		    final double time = this.json2double(result.get("time"));
		    return new ConfirmedReservationStatus((int)time);
		}else if(status.equals("Reservation::waiting")){
		    final int position = this.json2int(result.get("position"));
		    return new WaitingReservationStatus(position);
		}else if(status.equals("Reservation::cancelling")){
		    return new CancellingReservationStatus();
		}else if(status.equals("Reservation::waiting_instances")){
		    final int position = this.json2int(result.get("position"));
		    return new WaitingInstancesReservationStatus(position);
		}else
		    throw new SerializationException("Unknown status: " + status);
    }
    
    @Override
	public ExperimentAllowed[] parseListExperimentsResponse(String responseText)
    	throws SerializationException, SessionNotFoundException, UserProcessingException, WlServerException {	
	//	"{\"result\": [" +
	//		"{\"experiment\": {\"category\": {\"name\": \"Dummy experiments\"}, " +
	//			"\"name\": \"ud-dummy\", \"end_date\": \"2008-01-01\", \"start_date\": \"2007-08-17\"}, \"time_allowed\": 30.0}, " +
	//		"{\"experiment\": {\"category\": {\"name\": \"FPGA experiments\"}, " +
	//			"\"name\": \"ud-fpga\", \"end_date\": \"2006-01-01\", \"start_date\": \"2005-01-01\"}, \"time_allowed\": 30.0}" +
	//	"], \"is_exception\": false}"
		final JSONArray result = this.parseResultArray(responseText);
		final ExperimentAllowed [] experiments = new ExperimentAllowed[result.size()];
		for(int i = 0; i < result.size(); ++i){
		    final JSONValue value = result.get(i);
		    final JSONObject jsonExperimentAllowed = value.isObject();
		    if(jsonExperimentAllowed == null)
			throw new SerializationException("Expected JSON Object as ExperimentAllowed, found: " + value);
		    final JSONValue jsonExperimentValue = jsonExperimentAllowed.get("experiment");
		    if(jsonExperimentValue == null)
			throw new SerializationException("Expected experiment field in ExperimentAllowed");
		    final JSONObject jsonExperiment = jsonExperimentValue.isObject();
		    if(jsonExperiment == null)
			throw new SerializationException("Expected JSON Object as Experiment, found: " + jsonExperimentValue);
		    final JSONValue jsonCategoryValue = jsonExperiment.get("category");
		    if(jsonCategoryValue == null)
			throw new SerializationException("Expected category field in Experiment");
		    final JSONObject jsonCategory = jsonCategoryValue.isObject();
		    if(jsonCategory == null)
			throw new SerializationException("Expected JSON Object as Category, found: " + jsonCategoryValue);
		    
		    final Category category = new Category(this.json2string(jsonCategory.get("name")));
		    
		    final Experiment experiment = new Experiment();
		    experiment.setCategory(category);
		    experiment.setName(this.json2string(jsonExperiment.get("name")));
		    
		    final String startDateString = this.json2string(jsonExperiment.get("start_date"));
		    final String endDateString   = this.json2string(jsonExperiment.get("end_date"));
		    
		    final DateTimeFormat formatter1 = DateTimeFormat.getFormat("yyyy-MM-dd");
		    final DateTimeFormat formatter2 = DateTimeFormat.getFormat("yyyy-MM-dd HH:mm:ss");
		    final DateTimeFormat formatter3 = DateTimeFormat.getFormat("yyyy-MM-ddTHH:mm:ss");
		    
		    try{
			experiment.setStartDate(formatter1.parse(startDateString));
			experiment.setEndDate(formatter1.parse(endDateString));
		    }catch(final IllegalArgumentException iae){
				try{
				    experiment.setStartDate(formatter2.parse(startDateString));
				    experiment.setEndDate(formatter2.parse(endDateString));
				}catch(final IllegalArgumentException iae2){
					try{
					    experiment.setStartDate(formatter3.parse(startDateString));
					    experiment.setEndDate(formatter3.parse(endDateString));
					}catch(final IllegalArgumentException iae3){
					    throw new SerializationException("Couldn't parse date: " + startDateString + "; or: " + endDateString);
					}
				}
		    }
		    
		    final ExperimentAllowed experimentAllowed = new ExperimentAllowed();
		    experimentAllowed.setTimeAllowed(this.json2int(jsonExperimentAllowed.get("time_allowed")));
		    experimentAllowed.setExperiment(experiment);
		    
		    experiments[i] = experimentAllowed;
		}
		return experiments;
    }

    @Override
	public void parsePollResponse(String responseText)
	    throws SerializationException, SessionNotFoundException, NoCurrentReservationException, UserProcessingException, WlServerException {
    	this.parseResultObject(responseText);
    }

    @Override
	public ReservationStatus parseReserveExperimentResponse(String responseText)
    	throws SerializationException, SessionNotFoundException, UnknownExperimentIdException, UserProcessingException, WlServerException {
		final JSONObject result = this.parseResultObject(responseText);
		return this.parseReservationStatus(result);
    }

    @Override
	public ResponseCommand parseSendCommandResponse(String responseText)
	    throws SerializationException, SessionNotFoundException, NoCurrentReservationException, UserProcessingException, WlServerException {
		// "{\"result\": {\"commandstring\": null}, \"is_exception\": false}"
		final JSONObject result = this.parseResultObject(responseText);
		final JSONValue value = result.get("commandstring");
		if(value.isNull() != null)
		    return new EmptyResponseCommand();
		final String commandString = this.json2string(value);
		return new ResponseCommand(commandString);
    }

    @Override
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
    
    /**
     * TODO: This method will probably need some work.
     */
    @Override
	public String serializeCheckAsyncCommandStatusRequest(SessionID sessionId, String [] requestIdentifiers) 
		throws SerializationException {
    	
    	final JSONArray requestIds = new JSONArray();
    	for(int i = 0; i < requestIdentifiers.length; ++i)
    		requestIds.set(i, new JSONString(requestIdentifiers[i]));
  
		final JSONObject params = new JSONObject();
		params.put("session_id", this.serializeSessionId(sessionId));
		params.put("request_identifiers", requestIds);
		
		return this.serializeRequest("check_async_command_status", params);
	}

    @Override
	public String serializeFinishedExperimentRequest(SessionID sessionId)
	    throws SerializationException {
		// "{\"params\":{\"session_id\":{\"id\":\"" + MESSAGE + "\"}}, \"method\":\"finished_experiment\"}",
		final JSONObject params = new JSONObject();
		params.put("session_id", this.serializeSessionId(sessionId));
		return this.serializeRequest("finished_experiment", params);
    }

    @Override
	public String serializeGetReservationStatusRequest(SessionID sessionId) throws SerializationException {
		final JSONObject params = new JSONObject();
		params.put("session_id", this.serializeSessionId(sessionId));
		return this.serializeRequest("get_reservation_status", params);
    }

    @Override
	public String serializeListExperimentsRequest(SessionID sessionId)
	    throws SerializationException {
		final JSONObject params = new JSONObject();
		params.put("session_id", this.serializeSessionId(sessionId));
		return this.serializeRequest("list_experiments", params);
    }

    @Override
	public String serializePollRequest(SessionID sessionId)
	    throws SerializationException {
		final JSONObject params = new JSONObject();
		params.put("session_id", this.serializeSessionId(sessionId));
		return this.serializeRequest("poll", params);
    }

    @Override
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

    @Override
	public String serializeSendCommandRequest(SessionID sessionId,
	    Command command) throws SerializationException {
		final JSONObject params = new JSONObject();
		params.put("session_id", this.serializeSessionId(sessionId));
		final JSONObject commandjson = new JSONObject();
		commandjson.put("commandstring", new JSONString(command.getCommandString()));
		params.put("command", commandjson);
		return this.serializeRequest("send_command", params);
    }
    
    @Override
    public String serializeSendAsyncCommandRequest(SessionID sessionId,
    		Command command) throws SerializationException {
    	final JSONObject params = new JSONObject();
    	params.put("session_id", this.serializeSessionId(sessionId));
    	final JSONObject commandjson = new JSONObject();
    	commandjson.put("commandstring", new JSONString(command.getCommandString()));
    	params.put("command", commandjson);
    	return this.serializeRequest("send_async_command", params);
    }

    // General
    
    @Override
	protected WlServerException buildException(final String faultCode, final String faultString) {
		if(faultCode.equals(WlLabSerializerJSON.ERR_CLIENT_NO_CURRENT_RESERVATION)){
		    return new NoCurrentReservationException(faultString);
		}else if(faultCode.equals(WlLabSerializerJSON.ERR_CLIENT_UNKNOWN_EXPERIMENT_ID)){
		    return new UnknownExperimentIdException(faultString);
		} else {
			return super.buildException(faultCode, faultString);
		}
	}    
}
