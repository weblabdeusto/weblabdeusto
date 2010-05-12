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

import com.google.gwt.json.client.JSONObject;

import es.deusto.weblab.client.comm.FakeWlCommonSerializer;
import es.deusto.weblab.client.comm.exceptions.SerializationException;
import es.deusto.weblab.client.comm.exceptions.WlServerException;
import es.deusto.weblab.client.comm.exceptions.core.SessionNotFoundException;
import es.deusto.weblab.client.dto.SessionID;
import es.deusto.weblab.client.dto.experiments.Command;
import es.deusto.weblab.client.dto.experiments.ExperimentAllowed;
import es.deusto.weblab.client.dto.experiments.ExperimentID;
import es.deusto.weblab.client.dto.experiments.ResponseCommand;
import es.deusto.weblab.client.dto.reservations.ReservationStatus;
import es.deusto.weblab.client.dto.users.User;

public class FakeWlLabSerializer extends FakeWlCommonSerializer implements IWlLabSerializer {
	
	public static final String PARSE_GET_RESERVATION_STATUS_RESPONSE    = "FakeWebLabSerializer::parseGetReservationStatus";
	public static final String PARSE_GET_USER_INFORMATION_RESPONSE      = "FakeWebLabSerializer::parseGetUserInformation";
	public static final String PARSE_LIST_EXPERIMENTS_RESPONSE          = "FakeWebLabSerializer::parseListExperimentsResponse";
	public static final String PARSE_POLL_RESPONSE                      = "FakeWebLabSerializer::parsePollResponse";
	public static final String PARSE_RESERVE_EXPERIMENT_RESPONSE        = "FakeWebLabSerializer::parseReserveExperimentResponse";
	public static final String PARSE_SEND_COMMAND_RESPONSE              = "FakeWebLabSerializer::parseSendCommandResponse";
	public static final String PARSE_FINISHED_EXPERIMENT_RESPONSE       = "FakeWebLabSerializer::parseFinishedExperimentResponse";
	public static final String PARSE_SEND_FILE_RESPONSE                 = "FakeWebLabSerializer::parseSendFileResponse";

	public static final String SERIALIZE_GET_RESERVATION_STATUS_REQUEST = "FakeWebLabSerializer::serializeGetReservationStatusRequest";
	public static final String SERIALIZE_GET_USER_INFORMATION_REQUEST   = "FakeWebLabSerializer::serializeGetUserInformationRequest";
	public static final String SERIALIZE_LIST_EXPERIMENTS_REQUEST       = "FakeWebLabSerializer::serializeListExperimentsRequest";
	public static final String SERIALIZE_POLL_REQUEST                   = "FakeWebLabSerializer::serializePollRequest";
	public static final String SERIALIZE_RESERVE_EXPERIMENT_REQUEST     = "FakeWebLabSerializer::serializeReserveExperimentRequest";
	public static final String SERIALIZE_SEND_COMMAND_REQUEST           = "FakeWebLabSerializer::serializeSendCommandRequest";
	public static final String SERIALIZE_FINISHED_EXPERIMENT_REQUEST    = "FakeWebLabSerializer::serializeFinishedExperimentRequest";

	public ReservationStatus parseGetReservationStatusResponse(String responseText) {
		this.append(FakeWlLabSerializer.PARSE_GET_RESERVATION_STATUS_RESPONSE, new Object[]{
				responseText
		});
		return (ReservationStatus)this.retrieveReturn(FakeWlLabSerializer.PARSE_GET_RESERVATION_STATUS_RESPONSE);
	}

	public User parseGetUserInformationResponse(String responseText) {
		this.append(FakeWlLabSerializer.PARSE_GET_USER_INFORMATION_RESPONSE, new Object[]{
				responseText
		});
		return (User)this.retrieveReturn(FakeWlLabSerializer.PARSE_GET_USER_INFORMATION_RESPONSE);
	}
	
	public ExperimentAllowed [] parseListExperimentsResponse(String responseText){
		this.append(FakeWlLabSerializer.PARSE_LIST_EXPERIMENTS_RESPONSE, new Object[]{
				responseText
		});
		return (ExperimentAllowed [])this.retrieveReturn(FakeWlLabSerializer.PARSE_LIST_EXPERIMENTS_RESPONSE);
	}

	public void parseFinishedExperimentResponse(String responseText)
		throws SerializationException {
			this.append(FakeWlLabSerializer.PARSE_FINISHED_EXPERIMENT_RESPONSE, new Object[]{
					responseText
			});
	}
	
	public void parsePollResponse(String responseText)
		throws SerializationException {
		this.append(FakeWlLabSerializer.PARSE_POLL_RESPONSE, new Object[]{
				responseText
		});
	}

	public ResponseCommand parseSendFileResponse(String responseText)
		throws SerializationException, SessionNotFoundException,
			WlServerException 
	{
		this.append(FakeWlLabSerializer.PARSE_SEND_FILE_RESPONSE, new Object[]{
				responseText
		});
		return (ResponseCommand)this.retrieveReturn(FakeWlLabSerializer.PARSE_SEND_FILE_RESPONSE);
	}
	
	public ReservationStatus parseReserveExperimentResponse(String responseText)
		throws SerializationException {
		this.append(FakeWlLabSerializer.PARSE_RESERVE_EXPERIMENT_RESPONSE, new Object[]{
				responseText
		});
		return (ReservationStatus)this.retrieveReturn(FakeWlLabSerializer.PARSE_RESERVE_EXPERIMENT_RESPONSE);
	}
	
	public ResponseCommand parseSendCommandResponse(String responseText)
		throws SerializationException {
		this.append(FakeWlLabSerializer.PARSE_SEND_COMMAND_RESPONSE, new Object[]{
				responseText
		});
		return (ResponseCommand)this.retrieveReturn(FakeWlLabSerializer.PARSE_SEND_COMMAND_RESPONSE);
	}
	
	@SuppressWarnings("unused")
	protected ReservationStatus parseReservationStatus(final JSONObject result) throws SerializationException {
		return null;
	}	
	
	public String serializeGetReservationStatusRequest(SessionID sessionId) {
		this.append(FakeWlLabSerializer.SERIALIZE_GET_RESERVATION_STATUS_REQUEST, new Object[]{
				sessionId
		});
		return (String)this.retrieveReturn(FakeWlLabSerializer.SERIALIZE_GET_RESERVATION_STATUS_REQUEST);
	}

	public String serializeGetUserInformationRequest(SessionID sessionId) {
		this.append(FakeWlLabSerializer.SERIALIZE_GET_USER_INFORMATION_REQUEST, new Object[]{
				sessionId
		});
		return (String)this.retrieveReturn(FakeWlLabSerializer.SERIALIZE_GET_USER_INFORMATION_REQUEST);
	}
	
	public String serializeListExperimentsRequest(SessionID sessionId){
		this.append(FakeWlLabSerializer.SERIALIZE_LIST_EXPERIMENTS_REQUEST, new Object[]{
				sessionId
		});
		return (String)this.retrieveReturn(FakeWlLabSerializer.SERIALIZE_LIST_EXPERIMENTS_REQUEST);
	}

	public String serializeFinishedExperimentRequest(SessionID sessionId)
			throws SerializationException {
		this.append(FakeWlLabSerializer.SERIALIZE_FINISHED_EXPERIMENT_REQUEST, new Object[]{
				sessionId
		});
		return (String)this.retrieveReturn(FakeWlLabSerializer.SERIALIZE_FINISHED_EXPERIMENT_REQUEST);
	}

	public String serializePollRequest(SessionID sessionId)
			throws SerializationException {
		this.append(FakeWlLabSerializer.SERIALIZE_POLL_REQUEST, new Object[]{
				sessionId
		});
		return (String)this.retrieveReturn(FakeWlLabSerializer.SERIALIZE_POLL_REQUEST);
	}

	public String serializeReserveExperimentRequest(SessionID sessionId,
			ExperimentID experimentId) throws SerializationException {
		this.append(FakeWlLabSerializer.SERIALIZE_RESERVE_EXPERIMENT_REQUEST, new Object[]{
				sessionId,
				experimentId
		});
		return (String)this.retrieveReturn(FakeWlLabSerializer.SERIALIZE_RESERVE_EXPERIMENT_REQUEST);
	}

	public String serializeSendCommandRequest(SessionID sessionId,
			Command command) throws SerializationException {
		this.append(FakeWlLabSerializer.SERIALIZE_SEND_COMMAND_REQUEST, new Object[]{
				sessionId,
				command
		});
		return (String)this.retrieveReturn(FakeWlLabSerializer.SERIALIZE_SEND_COMMAND_REQUEST);
	}
}
