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

import es.deusto.weblab.client.comm.exceptions.SerializationException;
import es.deusto.weblab.client.comm.exceptions.WlServerException;
import es.deusto.weblab.client.comm.exceptions.user_processing.SessionNotFoundException;
import es.deusto.weblab.client.dto.SessionID;
import es.deusto.weblab.client.dto.experiments.Command;
import es.deusto.weblab.client.dto.experiments.ExperimentAllowed;
import es.deusto.weblab.client.dto.experiments.ExperimentID;
import es.deusto.weblab.client.dto.experiments.ResponseCommand;
import es.deusto.weblab.client.dto.reservations.ReservationStatus;
import es.deusto.weblab.client.dto.users.User;
import es.deusto.weblab.client.testing.util.WlFake;

public class FakeWebLabSerializer extends WlFake implements IWebLabSerializer {
	
	public static final String PARSE_GET_RESERVATION_STATUS_RESPONSE    = "FakeWebLabSerializer::parseGetReservationStatus";
	public static final String PARSE_GET_USER_INFORMATION_RESPONSE      = "FakeWebLabSerializer::parseGetUserInformation";
	public static final String PARSE_LIST_EXPERIMENTS_RESPONSE          = "FakeWebLabSerializer::parseListExperimentsResponse";
	public static final String PARSE_LOGIN_RESPONSE                     = "FakeWebLabSerializer::parseLoginResponse";
	public static final String PARSE_LOGOUT_RESPONSE                    = "FakeWebLabSerializer::parseLogoutResponse";
	public static final String PARSE_POLL_RESPONSE                      = "FakeWebLabSerializer::parsePollResponse";
	public static final String PARSE_RESERVE_EXPERIMENT_RESPONSE        = "FakeWebLabSerializer::parseReserveExperimentResponse";
	public static final String PARSE_SEND_COMMAND_RESPONSE              = "FakeWebLabSerializer::parseSendCommandResponse";
	public static final String PARSE_FINISHED_EXPERIMENT_RESPONSE       = "FakeWebLabSerializer::parseFinishedExperimentResponse";
	public static final String PARSE_SEND_FILE_RESPONSE                 = "FakeWebLabSerializer::parseSendFileResponse";

	public static final String SERIALIZE_GET_RESERVATION_STATUS_REQUEST = "FakeWebLabSerializer::serializeGetReservationStatusRequest";
	public static final String SERIALIZE_GET_USER_INFORMATION_REQUEST   = "FakeWebLabSerializer::serializeGetUserInformationRequest";
	public static final String SERIALIZE_LIST_EXPERIMENTS_REQUEST       = "FakeWebLabSerializer::serializeListExperimentsRequest";
	public static final String SERIALIZE_LOGIN_REQUEST                  = "FakeWebLabSerializer::serializeLoginRequest";
	public static final String SERIALIZE_LOGOUT_REQUEST                 = "FakeWebLabSerializer::serializeLogoutRequest";
	public static final String SERIALIZE_POLL_REQUEST                   = "FakeWebLabSerializer::serializePollRequest";
	public static final String SERIALIZE_RESERVE_EXPERIMENT_REQUEST     = "FakeWebLabSerializer::serializeReserveExperimentRequest";
	public static final String SERIALIZE_SEND_COMMAND_REQUEST           = "FakeWebLabSerializer::serializeSendCommandRequest";
	public static final String SERIALIZE_FINISHED_EXPERIMENT_REQUEST    = "FakeWebLabSerializer::serializeFinishedExperimentRequest";

	public ReservationStatus parseGetReservationStatusResponse(String responseText) {
		this.append(FakeWebLabSerializer.PARSE_GET_RESERVATION_STATUS_RESPONSE, new Object[]{
				responseText
		});
		return (ReservationStatus)this.retrieveReturn(FakeWebLabSerializer.PARSE_GET_RESERVATION_STATUS_RESPONSE);
	}

	public User parseGetUserInformationResponse(String responseText) {
		this.append(FakeWebLabSerializer.PARSE_GET_USER_INFORMATION_RESPONSE, new Object[]{
				responseText
		});
		return (User)this.retrieveReturn(FakeWebLabSerializer.PARSE_GET_USER_INFORMATION_RESPONSE);
	}
	
	public ExperimentAllowed [] parseListExperimentsResponse(String responseText){
		this.append(FakeWebLabSerializer.PARSE_LIST_EXPERIMENTS_RESPONSE, new Object[]{
				responseText
		});
		return (ExperimentAllowed [])this.retrieveReturn(FakeWebLabSerializer.PARSE_LIST_EXPERIMENTS_RESPONSE);
	}

	public SessionID parseLoginResponse(String responseText)
		throws SerializationException {
		this.append(FakeWebLabSerializer.PARSE_LOGIN_RESPONSE, new Object[]{
				responseText
		});
		return (SessionID)this.retrieveReturn(FakeWebLabSerializer.PARSE_LOGIN_RESPONSE);
	}

	public void parseFinishedExperimentResponse(String responseText)
		throws SerializationException {
			this.append(FakeWebLabSerializer.PARSE_FINISHED_EXPERIMENT_RESPONSE, new Object[]{
					responseText
			});
	}
	
	public void parseLogoutResponse(String responseText)
		throws SerializationException {
		this.append(FakeWebLabSerializer.PARSE_LOGOUT_RESPONSE, new Object[]{
				responseText
		});
	}
	
	public void parsePollResponse(String responseText)
		throws SerializationException {
		this.append(FakeWebLabSerializer.PARSE_POLL_RESPONSE, new Object[]{
				responseText
		});
	}

	public ResponseCommand parseSendFileResponse(String responseText)
		throws SerializationException, SessionNotFoundException,
			WlServerException 
	{
		this.append(FakeWebLabSerializer.PARSE_SEND_FILE_RESPONSE, new Object[]{
				responseText
		});
		return (ResponseCommand)this.retrieveReturn(FakeWebLabSerializer.PARSE_SEND_FILE_RESPONSE);
	}
	
	public ReservationStatus parseReserveExperimentResponse(String responseText)
		throws SerializationException {
		this.append(FakeWebLabSerializer.PARSE_RESERVE_EXPERIMENT_RESPONSE, new Object[]{
				responseText
		});
		return (ReservationStatus)this.retrieveReturn(FakeWebLabSerializer.PARSE_RESERVE_EXPERIMENT_RESPONSE);
	}
	
	public ResponseCommand parseSendCommandResponse(String responseText)
		throws SerializationException {
		this.append(FakeWebLabSerializer.PARSE_SEND_COMMAND_RESPONSE, new Object[]{
				responseText
		});
		return (ResponseCommand)this.retrieveReturn(FakeWebLabSerializer.PARSE_SEND_COMMAND_RESPONSE);
	}
	
	public String serializeGetReservationStatusRequest(SessionID sessionId) {
		this.append(FakeWebLabSerializer.SERIALIZE_GET_RESERVATION_STATUS_REQUEST, new Object[]{
				sessionId
		});
		return (String)this.retrieveReturn(FakeWebLabSerializer.SERIALIZE_GET_RESERVATION_STATUS_REQUEST);
	}

	public String serializeGetUserInformationRequest(SessionID sessionId) {
		this.append(FakeWebLabSerializer.SERIALIZE_GET_USER_INFORMATION_REQUEST, new Object[]{
				sessionId
		});
		return (String)this.retrieveReturn(FakeWebLabSerializer.SERIALIZE_GET_USER_INFORMATION_REQUEST);
	}
	
	public String serializeListExperimentsRequest(SessionID sessionId){
		this.append(FakeWebLabSerializer.SERIALIZE_LIST_EXPERIMENTS_REQUEST, new Object[]{
				sessionId
		});
		return (String)this.retrieveReturn(FakeWebLabSerializer.SERIALIZE_LIST_EXPERIMENTS_REQUEST);
	}

	public String serializeLoginRequest(String username, String password)
			throws SerializationException {
		this.append(FakeWebLabSerializer.SERIALIZE_LOGIN_REQUEST, new Object[]{
				username,
				password
		});
		return (String)this.retrieveReturn(FakeWebLabSerializer.SERIALIZE_LOGIN_REQUEST);
	}

	public String serializeFinishedExperimentRequest(SessionID sessionId)
			throws SerializationException {
		this.append(FakeWebLabSerializer.SERIALIZE_FINISHED_EXPERIMENT_REQUEST, new Object[]{
				sessionId
		});
		return (String)this.retrieveReturn(FakeWebLabSerializer.SERIALIZE_FINISHED_EXPERIMENT_REQUEST);
	}

	public String serializeLogoutRequest(SessionID sessionId)
			throws SerializationException {
		this.append(FakeWebLabSerializer.SERIALIZE_LOGOUT_REQUEST, new Object[]{
				sessionId
		});
		return (String)this.retrieveReturn(FakeWebLabSerializer.SERIALIZE_LOGOUT_REQUEST);
	}

	public String serializePollRequest(SessionID sessionId)
			throws SerializationException {
		this.append(FakeWebLabSerializer.SERIALIZE_POLL_REQUEST, new Object[]{
				sessionId
		});
		return (String)this.retrieveReturn(FakeWebLabSerializer.SERIALIZE_POLL_REQUEST);
	}

	public String serializeReserveExperimentRequest(SessionID sessionId,
			ExperimentID experimentId) throws SerializationException {
		this.append(FakeWebLabSerializer.SERIALIZE_RESERVE_EXPERIMENT_REQUEST, new Object[]{
				sessionId,
				experimentId
		});
		return (String)this.retrieveReturn(FakeWebLabSerializer.SERIALIZE_RESERVE_EXPERIMENT_REQUEST);
	}

	public String serializeSendCommandRequest(SessionID sessionId,
			Command command) throws SerializationException {
		this.append(FakeWebLabSerializer.SERIALIZE_SEND_COMMAND_REQUEST, new Object[]{
				sessionId,
				command
		});
		return (String)this.retrieveReturn(FakeWebLabSerializer.SERIALIZE_SEND_COMMAND_REQUEST);
	}
}
