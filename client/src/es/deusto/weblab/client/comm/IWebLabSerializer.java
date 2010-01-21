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

import es.deusto.weblab.client.dto.SessionID;
import es.deusto.weblab.client.dto.experiments.Command;
import es.deusto.weblab.client.dto.experiments.ExperimentAllowed;
import es.deusto.weblab.client.dto.experiments.ExperimentID;
import es.deusto.weblab.client.dto.experiments.ResponseCommand;
import es.deusto.weblab.client.dto.reservations.ReservationStatus;
import es.deusto.weblab.client.dto.users.User;
import es.deusto.weblab.client.exceptions.comm.SerializationException;
import es.deusto.weblab.client.exceptions.comm.WlServerException;
import es.deusto.weblab.client.exceptions.comm.login.InvalidCredentialsException;
import es.deusto.weblab.client.exceptions.comm.login.LoginException;
import es.deusto.weblab.client.exceptions.comm.user_processing.NoCurrentReservationException;
import es.deusto.weblab.client.exceptions.comm.user_processing.SessionNotFoundException;
import es.deusto.weblab.client.exceptions.comm.user_processing.UnknownExperimentIdException;
import es.deusto.weblab.client.exceptions.comm.user_processing.UserProcessingException;

public interface IWebLabSerializer {

	SessionID parseLoginResponse(String responseText) 
		throws SerializationException, InvalidCredentialsException, LoginException, UserProcessingException, WlServerException;
	
	void parseLogoutResponse(String responseText) 
		throws SerializationException, SessionNotFoundException, UserProcessingException, WlServerException;
	
	ExperimentAllowed [] parseListExperimentsResponse(String responseText) 
		throws SerializationException, SessionNotFoundException, UserProcessingException, WlServerException;
	
	ReservationStatus parseReserveExperimentResponse(String responseText) 
		throws SerializationException, SessionNotFoundException, UnknownExperimentIdException, UserProcessingException, WlServerException;
	
	void parseFinishedExperimentResponse(String responseText) 
		throws SerializationException, SessionNotFoundException, NoCurrentReservationException, UserProcessingException, WlServerException;

	ReservationStatus parseGetReservationStatusResponse(String responseText) 
		throws SerializationException, SessionNotFoundException, NoCurrentReservationException, UserProcessingException, WlServerException;
	
	ResponseCommand parseSendCommandResponse(String responseText) 
		throws SerializationException, SessionNotFoundException, NoCurrentReservationException, UserProcessingException, WlServerException;
	
	void parsePollResponse(String responseText) 
		throws SerializationException, SessionNotFoundException, NoCurrentReservationException, UserProcessingException, WlServerException;

	User parseGetUserInformationResponse(String responseText) 
		throws SerializationException, SessionNotFoundException, UserProcessingException, WlServerException;
	
	ResponseCommand parseSendFileResponse(String responseText)
		throws SerializationException, SessionNotFoundException, NoCurrentReservationException, UserProcessingException, WlServerException;
	
	String serializeGetReservationStatusRequest(SessionID sessionId) throws SerializationException;
	String serializeGetUserInformationRequest(SessionID sessionId) throws SerializationException;
	String serializeListExperimentsRequest(SessionID sessionId) throws SerializationException;
	String serializeLoginRequest(String username, String password) throws SerializationException;
	String serializeLogoutRequest(SessionID sessionId) throws SerializationException;
	String serializePollRequest(SessionID sessionId) throws SerializationException;
	String serializeReserveExperimentRequest(SessionID sessionId, ExperimentID experimentId) throws SerializationException;
	String serializeSendCommandRequest(SessionID sessionId, Command command) throws SerializationException;
	String serializeFinishedExperimentRequest(SessionID sessionId) throws SerializationException;
}
