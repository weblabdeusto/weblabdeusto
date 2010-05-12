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

import junit.framework.Assert;

import com.google.gwt.junit.client.GWTTestCase;

import es.deusto.weblab.client.comm.exceptions.SerializationException;
import es.deusto.weblab.client.comm.exceptions.WlServerException;
import es.deusto.weblab.client.comm.exceptions.core.SessionNotFoundException;
import es.deusto.weblab.client.comm.exceptions.core.UserProcessingException;
import es.deusto.weblab.client.comm.exceptions.login.InvalidCredentialsException;
import es.deusto.weblab.client.comm.exceptions.login.LoginException;
import es.deusto.weblab.client.dto.SessionID;
import es.deusto.weblab.client.dto.experiments.Category;
import es.deusto.weblab.client.dto.experiments.Command;
import es.deusto.weblab.client.dto.experiments.EmptyResponseCommand;
import es.deusto.weblab.client.dto.experiments.ExperimentAllowed;
import es.deusto.weblab.client.dto.experiments.ExperimentID;
import es.deusto.weblab.client.dto.experiments.ResponseCommand;
import es.deusto.weblab.client.dto.reservations.CancellingReservationStatus;
import es.deusto.weblab.client.dto.reservations.ConfirmedReservationStatus;
import es.deusto.weblab.client.dto.reservations.ReservationStatus;
import es.deusto.weblab.client.dto.reservations.WaitingConfirmationReservationStatus;
import es.deusto.weblab.client.dto.reservations.WaitingInstancesReservationStatus;
import es.deusto.weblab.client.dto.reservations.WaitingReservationStatus;
import es.deusto.weblab.client.dto.users.User;
import es.deusto.weblab.client.lab.comm.IWlLabSerializer;
import es.deusto.weblab.client.lab.comm.WlLabSerializerJSON;
import es.deusto.weblab.client.lab.comm.exceptions.NoCurrentReservationException;
import es.deusto.weblab.client.lab.comm.exceptions.UnknownExperimentIdException;
import es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.xilinx.commands.PulseCommand;

public class WlLabSerializerJSONTest extends GWTTestCase{
    
	public void testParseGetReservationStatusResponse_Waiting() throws Exception{
		final IWlLabSerializer weblabSerializer = new WlLabSerializerJSON();
		final ReservationStatus reservation = weblabSerializer.parseGetReservationStatusResponse(
			"{\"result\": {\"status\": \"Reservation::waiting\", \"position\": 5}, \"is_exception\": false}"
		);
		Assert.assertTrue(reservation instanceof WaitingReservationStatus);
		Assert.assertEquals(5, ((WaitingReservationStatus)reservation).getPosition());
	}

	public void testParseGetReservationStatusResponse_WaitingConfirmation()  throws Exception{
		final IWlLabSerializer weblabSerializer = new WlLabSerializerJSON();
		final ReservationStatus reservation = weblabSerializer.parseGetReservationStatusResponse(
			"{\"result\": {\"status\": \"Reservation::waiting_confirmation\"}, \"is_exception\": false}"
		);
		Assert.assertTrue(reservation instanceof WaitingConfirmationReservationStatus);
	}

	public void testParseGetReservationStatusResponse_WaitingInstances()  throws Exception{
		final IWlLabSerializer weblabSerializer = new WlLabSerializerJSON();
		final ReservationStatus reservation = weblabSerializer.parseGetReservationStatusResponse(
			"{\"result\": {\"status\": \"Reservation::waiting_instances\", \"position\" : 5}, \"is_exception\": false}"
		);
		Assert.assertTrue(reservation instanceof WaitingInstancesReservationStatus);
		Assert.assertEquals(5, ((WaitingInstancesReservationStatus)reservation).getPosition());
	}

	public void testParseGetReservationStatusResponse_Cancelling()  throws Exception{
		final IWlLabSerializer weblabSerializer = new WlLabSerializerJSON();
		final ReservationStatus reservation = weblabSerializer.parseGetReservationStatusResponse(
			"{\"result\": {\"status\": \"Reservation::cancelling\"}, \"is_exception\": false}"
		);
		Assert.assertTrue(reservation instanceof CancellingReservationStatus);
	}

	public void testParseGetReservationStatusResponse_Confirmed() throws Exception{
		final IWlLabSerializer weblabSerializer = new WlLabSerializerJSON();
		final ReservationStatus reservation = weblabSerializer.parseGetReservationStatusResponse(
			"{\"result\": {\"status\": \"Reservation::confirmed\", \"time\": 28.771512031555176}, \"is_exception\": false}"
		);
		Assert.assertTrue(reservation instanceof ConfirmedReservationStatus);
		Assert.assertEquals(28, ((ConfirmedReservationStatus)reservation).getTime());
	}
	
	public void testParseGetReservationStatusResponse_Exceptions() throws Exception{
		final IWlLabSerializer weblabSerializer = new WlLabSerializerJSON();
		try{
			weblabSerializer.parseGetReservationStatusResponse(
				"");
			Assert.fail("exception expected");
		}catch(final SerializationException e){
			//Ok
		}
		
		try{
			weblabSerializer.parseGetReservationStatusResponse(
				"not a xml file");
			Assert.fail("exception expected");
		}catch(final SerializationException e){
			//Ok
		}
	}
	
	public void testParseGetUserInformationResponse() throws Exception{
		final IWlLabSerializer weblabSerializer = new WlLabSerializerJSON();
		final User user = weblabSerializer.parseGetUserInformationResponse(
				"{\"result\": {\"login\": \"porduna\", \"email\": \"porduna@tecnologico.deusto.es\", \"full_name\": \"Pablo Orduna\", \"role\": {\"name\": \"student\"}}, \"is_exception\": false}"
		);
		Assert.assertEquals("porduna", user.getLogin());
		Assert.assertEquals("Pablo Orduna", user.getFullName());
		Assert.assertEquals("porduna@tecnologico.deusto.es", user.getEmail());
		Assert.assertEquals("student", user.getRole().getName());
	}

	public void testParseGetUserInformationResponse_Exceptions() throws Exception{
		final IWlLabSerializer weblabSerializer = new WlLabSerializerJSON();
		try{
			weblabSerializer.parseGetUserInformationResponse(
					""
			);
			Assert.fail("expected exception");
		}catch(final SerializationException e){
			// Ok
		}
		try{
			weblabSerializer.parseGetUserInformationResponse(
					"this is not a json response :-D"
			);
			Assert.fail("expected exception");
		}catch(final SerializationException e){
			// Ok
		}
	}
	
	public void testParseLoginResponse() throws Exception{
		final IWlLabSerializer weblabSerializer = new WlLabSerializerJSON();
		final SessionID sessionId = weblabSerializer.parseLoginResponse(
				"{\"result\": {\"id\": \"whatever\"}, \"is_exception\":false}"
			);
		Assert.assertEquals("whatever",sessionId.getRealId());
	}

	public void testParseLoginResponse_Faults() throws Exception{
		final IWlLabSerializer weblabSerializer = new WlLabSerializerJSON();
		
		final String MESSAGE = "my message";
		final String whole_message = "{\"message\": \"" + MESSAGE + "\", \"code\": \"THE_FAULT_CODE\", \"is_exception\": true}";
		
		try {
			weblabSerializer.parseLoginResponse(
				whole_message.replaceFirst("THE_FAULT_CODE", "JSON:Client.InvalidCredentials")
			);
			Assert.fail("Exception expected");
		} catch (final InvalidCredentialsException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
		try {
			weblabSerializer.parseLoginResponse(
				whole_message.replaceFirst("THE_FAULT_CODE", "JSON:Server.Login")
			);
			Assert.fail("Exception expected");
		} catch (final LoginException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
		try {
			weblabSerializer.parseLoginResponse(
				whole_message.replaceFirst("THE_FAULT_CODE", "JSON:Server.WebLab")
			);
			Assert.fail("Exception expected");
		} catch (final WlServerException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
		try {
			weblabSerializer.parseLoginResponse(
				whole_message.replaceFirst("THE_FAULT_CODE", "JSON:Server.Voodoo")
			);
			Assert.fail("Exception expected");
		} catch (final WlServerException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
		try {
			weblabSerializer.parseLoginResponse(
				whole_message.replaceFirst("THE_FAULT_CODE", "JSON:Server.Python")
			);
			Assert.fail("Exception expected");
		} catch (final WlServerException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
	}

	public void testParseLoginResponse_Exceptions() throws Exception{
		final IWlLabSerializer weblabSerializer = new WlLabSerializerJSON();
		try{
			weblabSerializer.parseLoginResponse(
				""
			);
			Assert.fail("exception expected");
		}catch(final SerializationException se){
			//Ok
		}
		
		try{
			weblabSerializer.parseLoginResponse(
				"not a json response"
			);
			Assert.fail("exception expected");
		}catch(final SerializationException se){
			//Ok
		}
	}
	
	public void testParseLogoutResponse() throws Exception{
		final IWlLabSerializer weblabSerializer = new WlLabSerializerJSON();
		weblabSerializer.parseLogoutResponse(
				"{\"result\": {}, \"is_exception\": false}"
			);
	}

	public void testParseLogoutResponse_Faults() throws Exception{
		final IWlLabSerializer weblabSerializer = new WlLabSerializerJSON();
		
		final String MESSAGE = "my message";
		final String whole_message = "{\"message\": \"" + MESSAGE + "\", \"code\": \"THE_FAULT_CODE\", \"is_exception\": true}";
		
		try {
			weblabSerializer.parseLogoutResponse(
				whole_message.replaceFirst("THE_FAULT_CODE", "JSON:Client.SessionNotFound")
			);
			Assert.fail("Exception expected");
		} catch (final SessionNotFoundException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
		try {
			weblabSerializer.parseLogoutResponse(
				whole_message.replaceFirst("THE_FAULT_CODE", "JSON:Server.UserProcessing")
			);
			Assert.fail("Exception expected");
		} catch (final UserProcessingException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
		try {
			weblabSerializer.parseLogoutResponse(
				whole_message.replaceFirst("THE_FAULT_CODE", "JSON:Server.WebLab")
			);
			Assert.fail("Exception expected");
		} catch (final WlServerException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
		try {
			weblabSerializer.parseLogoutResponse(
				whole_message.replaceFirst("THE_FAULT_CODE", "JSON:Server.Voodoo")
			);
			Assert.fail("Exception expected");
		} catch (final WlServerException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
		try {
			weblabSerializer.parseLogoutResponse(
				whole_message.replaceFirst("THE_FAULT_CODE", "JSON:Server.Python")
			);
			Assert.fail("Exception expected");
		} catch (final WlServerException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
	}

	public void testParseLogoutResponse_Exceptions() throws Exception{
		final IWlLabSerializer weblabSerializer = new WlLabSerializerJSON();
		try{
			weblabSerializer.parseLogoutResponse(
					""
			);
			Assert.fail("exception expected");
		}catch(final SerializationException se){
			//Ok
		}
		
		try{
			weblabSerializer.parseLogoutResponse(
				"not a json response"
			);
			Assert.fail("exception expected");
		}catch(final SerializationException se){
			//Ok
		}
	}

	public void testParsePollResponse() throws Exception{
		final IWlLabSerializer weblabSerializer = new WlLabSerializerJSON();
		weblabSerializer.parsePollResponse(
				"{\"result\": {}, \"is_exception\": false}"
			);
	}

	public void testParsePollResponse_Faults() throws Exception{
		final IWlLabSerializer weblabSerializer = new WlLabSerializerJSON();
		
		final String MESSAGE = "my message";
		final String whole_message = "{\"message\": \"" + MESSAGE + "\", \"code\": \"THE_FAULT_CODE\", \"is_exception\": true}";
		
		try {
			weblabSerializer.parsePollResponse(
				whole_message.replaceFirst("THE_FAULT_CODE", "JSON:Client.SessionNotFound")
			);
			Assert.fail("Exception expected");
		} catch (final SessionNotFoundException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
		try {
			weblabSerializer.parsePollResponse(
				whole_message.replaceFirst("THE_FAULT_CODE", "JSON:Client.NoCurrentReservation")
			);
			Assert.fail("Exception expected");
		} catch (final NoCurrentReservationException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
		try {
			weblabSerializer.parsePollResponse(
				whole_message.replaceFirst("THE_FAULT_CODE", "JSON:Server.UserProcessing")
			);
			Assert.fail("Exception expected");
		} catch (final UserProcessingException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
		try {
			weblabSerializer.parsePollResponse(
				whole_message.replaceFirst("THE_FAULT_CODE", "JSON:Server.WebLab")
			);
			Assert.fail("Exception expected");
		} catch (final WlServerException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
		try {
			weblabSerializer.parsePollResponse(
				whole_message.replaceFirst("THE_FAULT_CODE", "JSON:Server.Voodoo")
			);
			Assert.fail("Exception expected");
		} catch (final WlServerException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
		try {
			weblabSerializer.parsePollResponse(
				whole_message.replaceFirst("THE_FAULT_CODE", "JSON:Server.Python")
			);
			Assert.fail("Exception expected");
		} catch (final WlServerException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
	}

	public void testParsePollResponse_Exceptions() throws Exception{
		final IWlLabSerializer weblabSerializer = new WlLabSerializerJSON();
		try{
			weblabSerializer.parsePollResponse(
					""
			);
			Assert.fail("exception expected");
		}catch(final SerializationException se){
			//Ok
		}
		
		try{
			weblabSerializer.parsePollResponse(
				"not a json response"
			);
			Assert.fail("exception expected");
		}catch(final SerializationException se){
			//Ok
		}
	}

	public void testParseSendCommandResponse() throws Exception{
		final IWlLabSerializer weblabSerializer = new WlLabSerializerJSON();
		final ResponseCommand command = weblabSerializer.parseSendCommandResponse(
			"{\"result\": {\"commandstring\": null}, \"is_exception\": false}"
		);
		Assert.assertEquals(new EmptyResponseCommand(), command);
		
		final String realResponse = "the_real_response";
		final ResponseCommand command2 = weblabSerializer.parseSendCommandResponse(
			"{\"result\": {\"commandstring\": \"" + realResponse + "\"}, \"is_exception\": false}"
		);
		Assert.assertEquals(realResponse, command2.getCommandString());
	}

	public void testParseSendCommandResponse_Faults() throws Exception{
		final IWlLabSerializer weblabSerializer = new WlLabSerializerJSON();
		
		final String MESSAGE = "my message";
		final String whole_message = "{\"message\": \"" + MESSAGE + "\", \"code\": \"THE_FAULT_CODE\", \"is_exception\": true}";
		
		try {
			weblabSerializer.parseSendCommandResponse(
				whole_message.replaceFirst("THE_FAULT_CODE", "JSON:Client.SessionNotFound")
			);
			Assert.fail("Exception expected");
		} catch (final SessionNotFoundException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
		try {
			weblabSerializer.parseSendCommandResponse(
				whole_message.replaceFirst("THE_FAULT_CODE", "JSON:Client.NoCurrentReservation")
			);
			Assert.fail("Exception expected");
		} catch (final NoCurrentReservationException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
		try {
			weblabSerializer.parseSendCommandResponse(
				whole_message.replaceFirst("THE_FAULT_CODE", "JSON:Server.UserProcessing")
			);
			Assert.fail("Exception expected");
		} catch (final UserProcessingException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
		try {
			weblabSerializer.parseSendCommandResponse(
				whole_message.replaceFirst("THE_FAULT_CODE", "JSON:Server.WebLab")
			);
			Assert.fail("Exception expected");
		} catch (final WlServerException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
		try {
			weblabSerializer.parseSendCommandResponse(
				whole_message.replaceFirst("THE_FAULT_CODE", "JSON:Server.Voodoo")
			);
			Assert.fail("Exception expected");
		} catch (final WlServerException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
		try {
			weblabSerializer.parseSendCommandResponse(
				whole_message.replaceFirst("THE_FAULT_CODE", "JSON:Server.Python")
			);
			Assert.fail("Exception expected");
		} catch (final WlServerException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
	}

	public void testParseSendCommandResponse_Exceptions() throws Exception{
		final IWlLabSerializer weblabSerializer = new WlLabSerializerJSON();
		try{
			weblabSerializer.parseSendCommandResponse(
					""
			);
			Assert.fail("exception expected");
		}catch(final SerializationException se){
			//Ok
		}
		
		try{
			weblabSerializer.parseSendCommandResponse(
				"not a json response"
			);
			Assert.fail("exception expected");
		}catch(final SerializationException se){
			//Ok
		}
	}

	public void testParseSendFileResponse() throws Exception{
		final IWlLabSerializer weblabSerializer = new WlLabSerializerJSON();
		final String realResponse = "the_real_response";
		final ResponseCommand command2 = weblabSerializer.parseSendFileResponse(
			"<body>SUCCESS@" + realResponse + "</body>"
		);
		Assert.assertEquals(realResponse, command2.getCommandString());
	}

	public void testParseSendFileResponse_Faults() throws Exception{
		final IWlLabSerializer weblabSerializer = new WlLabSerializerJSON();
		
		final String MESSAGE = "my message";
		final String whole_message = "<body>ERROR@THE_FAULT_CODE@" + MESSAGE + "</body>";
		
		try {
			weblabSerializer.parseSendFileResponse(
				whole_message.replaceFirst("THE_FAULT_CODE", "XMLRPC:Client.SessionNotFound")
			);
			Assert.fail("Exception expected");
		} catch (final SessionNotFoundException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
		try {
			weblabSerializer.parseSendFileResponse(
				whole_message.replaceFirst("THE_FAULT_CODE", "XMLRPC:Client.NoCurrentReservation")
			);
			Assert.fail("Exception expected");
		} catch (final NoCurrentReservationException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
		try {
			weblabSerializer.parseSendFileResponse(
				whole_message.replaceFirst("THE_FAULT_CODE", "XMLRPC:Server.UserProcessing")
			);
			Assert.fail("Exception expected");
		} catch (final UserProcessingException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
		try {
			weblabSerializer.parseSendFileResponse(
				whole_message.replaceFirst("THE_FAULT_CODE", "XMLRPC:Server.WebLab")
			);
			Assert.fail("Exception expected");
		} catch (final WlServerException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
		try {
			weblabSerializer.parseSendFileResponse(
				whole_message.replaceFirst("THE_FAULT_CODE", "XMLRPC:Server.Voodoo")
			);
			Assert.fail("Exception expected");
		} catch (final WlServerException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
		try {
			weblabSerializer.parseSendFileResponse(
				whole_message.replaceFirst("THE_FAULT_CODE", "XMLRPC:Server.Python")
			);
			Assert.fail("Exception expected");
		} catch (final WlServerException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
	}

	public void testParseSendFileResponse_Exceptions() throws Exception{
		final IWlLabSerializer weblabSerializer = new WlLabSerializerJSON();
		try{
			weblabSerializer.parseSendFileResponse(
					""
			);
			Assert.fail("exception expected");
		}catch(final SerializationException se){
			//Ok
		}
		
		try{
			weblabSerializer.parseSendFileResponse(
				"not an proper response"
			);
			Assert.fail("exception expected");
		}catch(final SerializationException se){
			//Ok
		}
	}
	
	
	public void testParseFinishedExperimentResponse() throws Exception{
		final IWlLabSerializer weblabSerializer = new WlLabSerializerJSON();
		weblabSerializer.parseFinishedExperimentResponse(
			"{\"result\": {}, \"is_exception\": false}"
		);
	}

	public void testParseFinishedExperimentResponse_Faults() throws Exception{
		final IWlLabSerializer weblabSerializer = new WlLabSerializerJSON();
		
		final String MESSAGE = "my message";
		final String whole_message = "{\"message\": \"" + MESSAGE + "\", \"code\": \"THE_FAULT_CODE\", \"is_exception\": true}";
		
		try {
			weblabSerializer.parseFinishedExperimentResponse(
				whole_message.replaceFirst("THE_FAULT_CODE", "JSON:Client.SessionNotFound")
			);
			Assert.fail("Exception expected");
		} catch (final SessionNotFoundException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
		try {
			weblabSerializer.parseFinishedExperimentResponse(
				whole_message.replaceFirst("THE_FAULT_CODE", "JSON:Client.NoCurrentReservation")
			);
			Assert.fail("Exception expected");
		} catch (final NoCurrentReservationException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
		try {
			weblabSerializer.parseFinishedExperimentResponse(
				whole_message.replaceFirst("THE_FAULT_CODE", "JSON:Server.UserProcessing")
			);
			Assert.fail("Exception expected");
		} catch (final UserProcessingException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
		try {
			weblabSerializer.parseFinishedExperimentResponse(
				whole_message.replaceFirst("THE_FAULT_CODE", "JSON:Server.WebLab")
			);
			Assert.fail("Exception expected");
		} catch (final WlServerException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
		try {
			weblabSerializer.parseFinishedExperimentResponse(
				whole_message.replaceFirst("THE_FAULT_CODE", "JSON:Server.Voodoo")
			);
			Assert.fail("Exception expected");
		} catch (final WlServerException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
		try {
			weblabSerializer.parseFinishedExperimentResponse(
				whole_message.replaceFirst("THE_FAULT_CODE", "JSON:Server.Python")
			);
			Assert.fail("Exception expected");
		} catch (final WlServerException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
	}

	public void testParseFinishedExperimentResponse_Exceptions() throws Exception{
		final IWlLabSerializer weblabSerializer = new WlLabSerializerJSON();
		try{
			weblabSerializer.parseFinishedExperimentResponse(
					""
			);
			Assert.fail("exception expected");
		}catch(final SerializationException se){
			//Ok
		}
		
		try{
			weblabSerializer.parseFinishedExperimentResponse(
				"not a json response"
			);
			Assert.fail("exception expected");
		}catch(final SerializationException se){
			//Ok
		}
	}

	public void testParseReserveExperimentResponse_Waiting() throws Exception{
		final IWlLabSerializer weblabSerializer = new WlLabSerializerJSON();
		final ReservationStatus reservation = weblabSerializer.parseReserveExperimentResponse(
			"{\"result\": {\"status\": \"Reservation::waiting\", \"position\": 5}, \"is_exception\": false}"
		);
		Assert.assertTrue(reservation instanceof WaitingReservationStatus);
		Assert.assertEquals(5, ((WaitingReservationStatus)reservation).getPosition());
	}

	public void testParseReserveExperimentResponse_Faults() throws Exception{
		final IWlLabSerializer weblabSerializer = new WlLabSerializerJSON();
		
		final String MESSAGE = "my message";
		final String whole_message = "{\"message\": \"" + MESSAGE + "\", \"code\": \"THE_FAULT_CODE\", \"is_exception\": true}";
		
		try {
			weblabSerializer.parseReserveExperimentResponse(
				whole_message.replaceFirst("THE_FAULT_CODE", "JSON:Client.SessionNotFound")
			);
			Assert.fail("Exception expected");
		} catch (final SessionNotFoundException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
		try {
			weblabSerializer.parseReserveExperimentResponse(
				whole_message.replaceFirst("THE_FAULT_CODE", "JSON:Client.UnknownExperimentId")
			);
			Assert.fail("Exception expected");
		} catch (final UnknownExperimentIdException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
		try {
			weblabSerializer.parseReserveExperimentResponse(
				whole_message.replaceFirst("THE_FAULT_CODE", "JSON:Server.UserProcessing")
			);
			Assert.fail("Exception expected");
		} catch (final UserProcessingException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
		try {
			weblabSerializer.parseReserveExperimentResponse(
				whole_message.replaceFirst("THE_FAULT_CODE", "JSON:Server.WebLab")
			);
			Assert.fail("Exception expected");
		} catch (final WlServerException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
		try {
			weblabSerializer.parseReserveExperimentResponse(
				whole_message.replaceFirst("THE_FAULT_CODE", "JSON:Server.Voodoo")
			);
			Assert.fail("Exception expected");
		} catch (final WlServerException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
		try {
			weblabSerializer.parseReserveExperimentResponse(
				whole_message.replaceFirst("THE_FAULT_CODE", "JSON:Server.Python")
			);
			Assert.fail("Exception expected");
		} catch (final WlServerException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
	}

	public void testParseReserveExperimentResponse_WaitingConfirmation()  throws Exception{
		final IWlLabSerializer weblabSerializer = new WlLabSerializerJSON();
		final ReservationStatus reservation = weblabSerializer.parseReserveExperimentResponse(
			"{\"result\": {\"status\": \"Reservation::waiting_confirmation\"}, \"is_exception\": false}"
		);
		Assert.assertTrue(reservation instanceof WaitingConfirmationReservationStatus);
	}

	public void testParseReserveExperimentResponse_WaitingInstances()  throws Exception{
		final IWlLabSerializer weblabSerializer = new WlLabSerializerJSON();
		final ReservationStatus reservation = weblabSerializer.parseReserveExperimentResponse(
			"{\"result\": {\"status\": \"Reservation::waiting_instances\", \"position\": 5}, \"is_exception\": false}"
		);
		Assert.assertTrue(reservation instanceof WaitingInstancesReservationStatus);
		Assert.assertEquals(5, ((WaitingInstancesReservationStatus)reservation).getPosition());
	}

	public void testParseReserveExperimentResponse_Cancelling()  throws Exception{
		final IWlLabSerializer weblabSerializer = new WlLabSerializerJSON();
		final ReservationStatus reservation = weblabSerializer.parseReserveExperimentResponse(
			"{\"result\": {\"status\": \"Reservation::cancelling\"}, \"is_exception\": false}"
		);
		Assert.assertTrue(reservation instanceof CancellingReservationStatus);
	}

	public void testParseReserveExperimentResponse_Confirmed() throws Exception{
		final IWlLabSerializer weblabSerializer = new WlLabSerializerJSON();
		final ReservationStatus reservation = weblabSerializer.parseReserveExperimentResponse(
			"{\"result\": {\"status\": \"Reservation::confirmed\", \"time\": 28.771512031555176}, \"is_exception\": false}"
		);
		Assert.assertTrue(reservation instanceof ConfirmedReservationStatus);
		Assert.assertEquals(28, ((ConfirmedReservationStatus)reservation).getTime());
	}
	
	public void testParseReserveExperimentResponse_Exceptions() throws Exception{
		final IWlLabSerializer weblabSerializer = new WlLabSerializerJSON();
		try{
			weblabSerializer.parseReserveExperimentResponse(
				"");
			Assert.fail("exception expected");
		}catch(final SerializationException e){
			//Ok
		}
		
		try{
			weblabSerializer.parseReserveExperimentResponse(
				"not a xml file");
			Assert.fail("exception expected");
		}catch(final SerializationException e){
			//Ok
		}
	}

	public void testParseListExperimentsResponse() throws Exception{
		final IWlLabSerializer weblabSerializer = new WlLabSerializerJSON();
		final ExperimentAllowed [] experiments = weblabSerializer.parseListExperimentsResponse(
			"{\"result\": [" +
				"{\"experiment\": {\"category\": {\"name\": \"Dummy experiments\"}, \"owner\": \"porduna@tecnologico.deusto.es\", " +
					"\"name\": \"ud-dummy\", \"end_date\": \"2008-01-01\", \"start_date\": \"2007-01-01\"}, \"time_allowed\": 30.0}, " +
				"{\"experiment\": {\"category\": {\"name\": \"FPGA experiments\"}, \"owner\": \"porduna@tecnologico.deusto.es\", " +
					"\"name\": \"ud-fpga\", \"end_date\": \"2006-01-01\", \"start_date\": \"2005-01-01\"}, \"time_allowed\": 30.0}" +
			"], \"is_exception\": false}"
		);
		
		Assert.assertEquals(2, experiments.length);
		
		// 0
		Assert.assertEquals(30,                              experiments[0].getTimeAllowed());
		Assert.assertEquals("ud-dummy",                      experiments[0].getExperiment().getName());
		Assert.assertEquals("Dummy experiments",             experiments[0].getExperiment().getCategory().getCategory());
		
		// 2007-01-01 00:00:00
		Assert.assertEquals(1167606000000l,                  experiments[0].getExperiment().getStartDate().getTime());
		// 2008-01-01 00:00:00
		Assert.assertEquals(1199142000000l,                  experiments[0].getExperiment().getEndDate().getTime());
		
		// 1
		Assert.assertEquals(30,                              experiments[1].getTimeAllowed());
		Assert.assertEquals("ud-fpga",                       experiments[1].getExperiment().getName());
		Assert.assertEquals("FPGA experiments",              experiments[1].getExperiment().getCategory().getCategory());
		
		// 2005-01-01 00:00:00
		Assert.assertEquals(1104534000000l,                  experiments[1].getExperiment().getStartDate().getTime());
		// 2006-01-01 00:00:00
		Assert.assertEquals(1136070000000l,                  experiments[1].getExperiment().getEndDate().getTime());		
	}

	public void testParseListExperimentsResponseWithOtherDateFormat() throws Exception{
		final IWlLabSerializer weblabSerializer = new WlLabSerializerJSON();
		final ExperimentAllowed [] experiments = weblabSerializer.parseListExperimentsResponse(
			"{\"result\": [" +
				"{\"experiment\": {\"category\": {\"name\": \"Dummy experiments\"}, \"owner\": \"porduna@tecnologico.deusto.es\", " +
					"\"name\": \"ud-dummy\", \"end_date\": \"2008-01-01 00:00:00\", \"start_date\": \"2007-01-01 00:00:00\"}, \"time_allowed\": 30.0}, " +
				"{\"experiment\": {\"category\": {\"name\": \"FPGA experiments\"}, \"owner\": \"porduna@tecnologico.deusto.es\", " +
					"\"name\": \"ud-fpga\", \"end_date\": \"2006-01-01 00:00:00\", \"start_date\": \"2005-01-01 00:00:00\"}, \"time_allowed\": 30.0}" +
			"], \"is_exception\": false}"
		);
		
		Assert.assertEquals(2, experiments.length);
		
		// 0
		Assert.assertEquals(30,                              experiments[0].getTimeAllowed());
		Assert.assertEquals("ud-dummy",                      experiments[0].getExperiment().getName());
		Assert.assertEquals("Dummy experiments",             experiments[0].getExperiment().getCategory().getCategory());
		
		// 2007-01-01 00:00:00
		Assert.assertEquals(1167606000000l,                  experiments[0].getExperiment().getStartDate().getTime());
		// 2008-01-01 00:00:00
		Assert.assertEquals(1199142000000l,                  experiments[0].getExperiment().getEndDate().getTime());
		
		// 1
		Assert.assertEquals(30,                              experiments[1].getTimeAllowed());
		Assert.assertEquals("ud-fpga",                       experiments[1].getExperiment().getName());
		Assert.assertEquals("FPGA experiments",              experiments[1].getExperiment().getCategory().getCategory());
		
		// 2005-01-01 00:00:00
		Assert.assertEquals(1104534000000l,                  experiments[1].getExperiment().getStartDate().getTime());
		// 2006-01-01 00:00:00
		Assert.assertEquals(1136070000000l,                  experiments[1].getExperiment().getEndDate().getTime());		
	}

	public void testParseListExperimentsResponse_Faults() throws Exception{
		final IWlLabSerializer weblabSerializer = new WlLabSerializerJSON();
		
		final String MESSAGE = "my message";
		final String whole_message = "{\"message\": \"" + MESSAGE + "\", \"code\": \"THE_FAULT_CODE\", \"is_exception\": true}";
		
		try {
			weblabSerializer.parseListExperimentsResponse(
				whole_message.replaceFirst("THE_FAULT_CODE", "JSON:Client.SessionNotFound")
			);
			Assert.fail("Exception expected");
		} catch (final SessionNotFoundException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
		try {
			weblabSerializer.parseListExperimentsResponse(
				whole_message.replaceFirst("THE_FAULT_CODE", "JSON:Server.UserProcessing")
			);
			Assert.fail("Exception expected");
		} catch (final UserProcessingException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
		try {
			weblabSerializer.parseListExperimentsResponse(
				whole_message.replaceFirst("THE_FAULT_CODE", "JSON:Server.WebLab")
			);
			Assert.fail("Exception expected");
		} catch (final WlServerException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
		try {
			weblabSerializer.parseListExperimentsResponse(
				whole_message.replaceFirst("THE_FAULT_CODE", "JSON:Server.Voodoo")
			);
			Assert.fail("Exception expected");
		} catch (final WlServerException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
		try {
			weblabSerializer.parseListExperimentsResponse(
				whole_message.replaceFirst("THE_FAULT_CODE", "JSON:Server.Python")
			);
			Assert.fail("Exception expected");
		} catch (final WlServerException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
	}

	public void testSerializeGetReservationStatusRequest() throws Exception{
		final IWlLabSerializer weblabSerializer = new WlLabSerializerJSON();
		final String MESSAGE = "whatever the session id real id";
		
		final SessionID sessionId = new SessionID(MESSAGE);
		final String serializedMessage = weblabSerializer.serializeGetReservationStatusRequest(sessionId);
		
		Assert.assertEquals(
				"{\"params\":{\"session_id\":{\"id\":\"" + MESSAGE + "\"}}, \"method\":\"get_reservation_status\"}",
				serializedMessage
			);
	}
	
	public void testSerializeGetUserInformationRequest() throws Exception{
		final IWlLabSerializer weblabSerializer = new WlLabSerializerJSON();
		final String MESSAGE = "whatever the session id real id";
		
		final SessionID sessionId = new SessionID(MESSAGE);
		final String serializedMessage = weblabSerializer.serializeGetUserInformationRequest(sessionId);
		
		Assert.assertEquals(
				"{\"params\":{\"session_id\":{\"id\":\"" + MESSAGE + "\"}}, \"method\":\"get_user_information\"}",
				serializedMessage
			);
	}
	
	public void testSerializeListExperimentsRequest() throws Exception{
		final IWlLabSerializer weblabSerializer = new WlLabSerializerJSON();
		final String MESSAGE = "whatever the session id real id";
		
		final SessionID sessionId = new SessionID(MESSAGE);
		final String serializedMessage = weblabSerializer.serializeListExperimentsRequest(sessionId);
		
		Assert.assertEquals(
				"{\"params\":{\"session_id\":{\"id\":\"" + MESSAGE + "\"}}, \"method\":\"list_experiments\"}",
				serializedMessage
			);
	}
	
	public void testSerializeLogoutRequest() throws Exception{
		final IWlLabSerializer weblabSerializer = new WlLabSerializerJSON();
		final String MESSAGE = "whatever the session id real id";
		
		final SessionID sessionId = new SessionID(MESSAGE);
		final String serializedMessage = weblabSerializer.serializeLogoutRequest(sessionId);
		
		Assert.assertEquals(
				"{\"params\":{\"session_id\":{\"id\":\"" + MESSAGE + "\"}}, \"method\":\"logout\"}",
				serializedMessage
			);
	}
	
	public void testSerializePollRequest() throws Exception{
		final IWlLabSerializer weblabSerializer = new WlLabSerializerJSON();
		final String MESSAGE = "whatever the session id real id";
		
		final SessionID sessionId = new SessionID(MESSAGE);
		final String serializedMessage = weblabSerializer.serializePollRequest(sessionId);
		
		Assert.assertEquals(
				"{\"params\":{\"session_id\":{\"id\":\"" + MESSAGE + "\"}}, \"method\":\"poll\"}",
				serializedMessage
			);
	}
	
	public void testSerializeFinishedExperimentRequest() throws Exception{
		final IWlLabSerializer weblabSerializer = new WlLabSerializerJSON();
		final String MESSAGE = "whatever the session id real id";
		
		final SessionID sessionId = new SessionID(MESSAGE);
		final String serializedMessage = weblabSerializer.serializeFinishedExperimentRequest(sessionId);
		
		Assert.assertEquals(
				"{\"params\":{\"session_id\":{\"id\":\"" + MESSAGE + "\"}}, \"method\":\"finished_experiment\"}",
				serializedMessage
			);
	}
	
	public void testSerializeLoginRequest() throws Exception{
		final IWlLabSerializer weblabSerializer = new WlLabSerializerJSON();
		
		final String USERNAME = "my username";
		final String PASSWORD = "my password";
		
		final String serializedMessage = weblabSerializer.serializeLoginRequest(USERNAME, PASSWORD);
		
		Assert.assertEquals(
				"{\"params\":{\"username\":\"" + USERNAME + "\", \"password\":\"" + PASSWORD + "\"}, \"method\":\"login\"}",
				serializedMessage
			);
	}
	
	public void testSerializeReserveExperimentRequest() throws Exception{
		final IWlLabSerializer weblabSerializer = new WlLabSerializerJSON();
		
		final String MESSAGE = "whatever the session id real id";
		
		final SessionID sessionId = new SessionID(MESSAGE);
		final ExperimentID experiment = new ExperimentID(
				new Category("WebLab-PLD experiments"),
				"weblab-pld"
			);
		
		final String serializedMessage = weblabSerializer.serializeReserveExperimentRequest(sessionId, experiment);
		Assert.assertEquals(
				"{\"params\":{\"session_id\":{\"id\":\"" + MESSAGE + "\"}," +
						" \"experiment_id\":{\"exp_name\":\"weblab-pld\", \"cat_name\":\"WebLab-PLD experiments\"}}, " +
						"\"method\":\"reserve_experiment\"}",
				serializedMessage
			);
	}
	
	public void testSerializeCommandRequest() throws Exception{
		final IWlLabSerializer weblabSerializer = new WlLabSerializerJSON();
		
		final String MESSAGE = "whatever the session id real id";
		
		final SessionID sessionId = new SessionID(MESSAGE);
		final Command command = new PulseCommand(5,true); 
		
		final String serializedMessage = weblabSerializer.serializeSendCommandRequest(sessionId, command);
		
		Assert.assertEquals(
				"{\"params\":{\"session_id\":{\"id\":\"" + MESSAGE + "\"}, \"command\":{\"commandstring\":\"" + command.getCommandString() + "\"}}, \"method\":\"send_command\"}",
				serializedMessage
			);
	}    	
    
	@Override
	public String getModuleName() {
		return "es.deusto.weblab.WebLabClient";
	}
}
