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
*
*/ 
package es.deusto.weblab.client.lab.comm;

import com.google.gwt.json.client.JSONObject;
import com.google.gwt.json.client.JSONValue;

import es.deusto.weblab.client.comm.FakeCommonSerializer;
import es.deusto.weblab.client.comm.exceptions.SerializationException;
import es.deusto.weblab.client.comm.exceptions.WebLabServerException;
import es.deusto.weblab.client.comm.exceptions.core.SessionNotFoundException;
import es.deusto.weblab.client.comm.exceptions.core.UserProcessingException;
import es.deusto.weblab.client.dto.SessionID;
import es.deusto.weblab.client.dto.experiments.AsyncRequestStatus;
import es.deusto.weblab.client.dto.experiments.Command;
import es.deusto.weblab.client.dto.experiments.ExperimentAllowed;
import es.deusto.weblab.client.dto.experiments.ExperimentID;
import es.deusto.weblab.client.dto.experiments.ResponseCommand;
import es.deusto.weblab.client.dto.reservations.ReservationStatus;
import es.deusto.weblab.client.lab.comm.exceptions.NoCurrentReservationException;

public class FakeLabSerializer extends FakeCommonSerializer implements ILabSerializer {
	
	public static final String PARSE_GET_RESERVATION_STATUS_RESPONSE    	= "FakeWebLabSerializer::parseGetReservationStatus";
	public static final String PARSE_LIST_EXPERIMENTS_RESPONSE          	= "FakeWebLabSerializer::parseListExperimentsResponse";
	public static final String PARSE_POLL_RESPONSE                      	= "FakeWebLabSerializer::parsePollResponse";
	public static final String PARSE_RESERVE_EXPERIMENT_RESPONSE        	= "FakeWebLabSerializer::parseReserveExperimentResponse";
	public static final String PARSE_SEND_COMMAND_RESPONSE              	= "FakeWebLabSerializer::parseSendCommandResponse";
	public static final String PARSE_CHECK_ASYNC_COMMAND_STATUS_RESPONSE 	= "FakeWebLabSerializer::parseCheckAsyncCommandStatusResponse";
	public static final String PARSE_FINISHED_EXPERIMENT_RESPONSE       	= "FakeWebLabSerializer::parseFinishedExperimentResponse";
	public static final String PARSE_SEND_FILE_RESPONSE                 	= "FakeWebLabSerializer::parseSendFileResponse";
	public static final String PARSE_SEND_ASYNC_COMMAND_RESPONSE			= "FakeWebLabSerializer::parseSendAsyncCommandResponse";

	public static final String SERIALIZE_GET_RESERVATION_STATUS_REQUEST 	= "FakeWebLabSerializer::serializeGetReservationStatusRequest";
	public static final String SERIALIZE_LIST_EXPERIMENTS_REQUEST       	= "FakeWebLabSerializer::serializeListExperimentsRequest";
	public static final String SERIALIZE_POLL_REQUEST                   	= "FakeWebLabSerializer::serializePollRequest";
	public static final String SERIALIZE_RESERVE_EXPERIMENT_REQUEST     	= "FakeWebLabSerializer::serializeReserveExperimentRequest";
	public static final String SERIALIZE_SEND_COMMAND_REQUEST          		= "FakeWebLabSerializer::serializeSendCommandRequest";
	public static final String SERIALIZE_SEND_ASYNC_COMMAND_REQUEST     	= "FakeWebLabSerializer::serializeAsyncSendCommandRequest";
	public static final String SERIALIZE_CHECK_ASYNC_COMMAND_STATUS_REQUEST = "FakeWebLabSerializer::serializeCheckAsyncCommandStatus";
	public static final String SERIALIZE_FINISHED_EXPERIMENT_REQUEST    	= "FakeWebLabSerializer::serializeFinishedExperimentRequest";

	@Override
	public ReservationStatus parseGetReservationStatusResponse(String responseText) {
		this.append(FakeLabSerializer.PARSE_GET_RESERVATION_STATUS_RESPONSE, new Object[]{
				responseText
		});
		return (ReservationStatus)this.retrieveReturn(FakeLabSerializer.PARSE_GET_RESERVATION_STATUS_RESPONSE);
	}
	
	

	@Override
	public ExperimentAllowed [] parseListExperimentsResponse(String responseText){
		this.append(FakeLabSerializer.PARSE_LIST_EXPERIMENTS_RESPONSE, new Object[]{
				responseText
		});
		return (ExperimentAllowed [])this.retrieveReturn(FakeLabSerializer.PARSE_LIST_EXPERIMENTS_RESPONSE);
	}

	@Override
	public void parseFinishedExperimentResponse(String responseText)
		throws SerializationException {
			this.append(FakeLabSerializer.PARSE_FINISHED_EXPERIMENT_RESPONSE, new Object[]{
					responseText
			});
	}
	
	@Override
	public void parsePollResponse(String responseText)
		throws SerializationException {
		this.append(FakeLabSerializer.PARSE_POLL_RESPONSE, new Object[]{
				responseText
		});
	}

	@Override
	public ResponseCommand parseSendFileResponse(String responseText)
		throws SerializationException, SessionNotFoundException,
			WebLabServerException 
	{
		this.append(FakeLabSerializer.PARSE_SEND_FILE_RESPONSE, new Object[]{
				responseText
		});
		return (ResponseCommand)this.retrieveReturn(FakeLabSerializer.PARSE_SEND_FILE_RESPONSE);
	}
	
	@Override
	public ReservationStatus parseReserveExperimentResponse(String responseText)
		throws SerializationException {
		this.append(FakeLabSerializer.PARSE_RESERVE_EXPERIMENT_RESPONSE, new Object[]{
				responseText
		});
		return (ReservationStatus)this.retrieveReturn(FakeLabSerializer.PARSE_RESERVE_EXPERIMENT_RESPONSE);
	}
	
	@Override
	public ResponseCommand parseSendCommandResponse(String responseText)
		throws SerializationException {
		this.append(FakeLabSerializer.PARSE_SEND_COMMAND_RESPONSE, new Object[]{
				responseText
		});
		return (ResponseCommand)this.retrieveReturn(FakeLabSerializer.PARSE_SEND_COMMAND_RESPONSE);
	}
	
	@Override
	public ResponseCommand parseSendAsyncCommandResponse(String responseText)
			throws SerializationException, SessionNotFoundException,
			NoCurrentReservationException, UserProcessingException,
			WebLabServerException {
		this.append(FakeLabSerializer.PARSE_SEND_ASYNC_COMMAND_RESPONSE, new Object[]{
				responseText
		});
		return (ResponseCommand)this.retrieveReturn(FakeLabSerializer.PARSE_SEND_ASYNC_COMMAND_RESPONSE);
	}
	
	@Override
	public AsyncRequestStatus[] parseCheckAsyncCommandStatusResponse(String responseText)
			throws SerializationException {
		this.append(FakeLabSerializer.PARSE_CHECK_ASYNC_COMMAND_STATUS_RESPONSE, new Object[]{
				responseText
		});
		return null;
	}

	
	@SuppressWarnings("unused")
	protected ReservationStatus parseReservationStatus(final JSONObject result) throws SerializationException {
		return null;
	}	
	
	@Override
	public String serializeGetReservationStatusRequest(SessionID sessionId) {
		this.append(FakeLabSerializer.SERIALIZE_GET_RESERVATION_STATUS_REQUEST, new Object[]{
				sessionId
		});
		return (String)this.retrieveReturn(FakeLabSerializer.SERIALIZE_GET_RESERVATION_STATUS_REQUEST);
	}

	@Override
	public String serializeListExperimentsRequest(SessionID sessionId){
		this.append(FakeLabSerializer.SERIALIZE_LIST_EXPERIMENTS_REQUEST, new Object[]{
				sessionId
		});
		return (String)this.retrieveReturn(FakeLabSerializer.SERIALIZE_LIST_EXPERIMENTS_REQUEST);
	}

	@Override
	public String serializeFinishedExperimentRequest(SessionID sessionId)
			throws SerializationException {
		this.append(FakeLabSerializer.SERIALIZE_FINISHED_EXPERIMENT_REQUEST, new Object[]{
				sessionId
		});
		return (String)this.retrieveReturn(FakeLabSerializer.SERIALIZE_FINISHED_EXPERIMENT_REQUEST);
	}

	@Override
	public String serializePollRequest(SessionID sessionId)
			throws SerializationException {
		this.append(FakeLabSerializer.SERIALIZE_POLL_REQUEST, new Object[]{
				sessionId
		});
		return (String)this.retrieveReturn(FakeLabSerializer.SERIALIZE_POLL_REQUEST);
	}

	@Override
	public String serializeReserveExperimentRequest(SessionID sessionId, ExperimentID experimentId, JSONValue clientInitialData) throws SerializationException {
		this.append(FakeLabSerializer.SERIALIZE_RESERVE_EXPERIMENT_REQUEST, new Object[]{
				sessionId,
				experimentId,
				clientInitialData
		});
		return (String)this.retrieveReturn(FakeLabSerializer.SERIALIZE_RESERVE_EXPERIMENT_REQUEST);
	}

	@Override
	public String serializeSendCommandRequest(SessionID sessionId,
			Command command) throws SerializationException {
		this.append(FakeLabSerializer.SERIALIZE_SEND_COMMAND_REQUEST, new Object[]{
				sessionId,
				command
		});
		return (String)this.retrieveReturn(FakeLabSerializer.SERIALIZE_SEND_COMMAND_REQUEST);
	}

	@Override
	public String serializeSendAsyncCommandRequest(SessionID sessionId,
			Command command) throws SerializationException {
		this.append(FakeLabSerializer.SERIALIZE_SEND_ASYNC_COMMAND_REQUEST, new Object[]{
			sessionId,
			command
		});
		return null;
	}


	@Override
	public String serializeCheckAsyncCommandStatusRequest(SessionID sessionId,
			String[] requestIdentifiers) throws SerializationException {
		this.append(FakeLabSerializer.SERIALIZE_CHECK_ASYNC_COMMAND_STATUS_REQUEST);
		return null;
	}


}
