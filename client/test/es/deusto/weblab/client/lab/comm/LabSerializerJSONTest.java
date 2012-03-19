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

import junit.framework.Assert;

import com.google.gwt.i18n.client.DateTimeFormat;
import com.google.gwt.json.client.JSONObject;
import com.google.gwt.junit.client.GWTTestCase;

import es.deusto.weblab.client.comm.exceptions.SerializationException;
import es.deusto.weblab.client.comm.exceptions.WebLabServerException;
import es.deusto.weblab.client.comm.exceptions.core.SessionNotFoundException;
import es.deusto.weblab.client.comm.exceptions.core.UserProcessingException;
import es.deusto.weblab.client.dto.SessionID;
import es.deusto.weblab.client.dto.experiments.AsyncRequestStatus;
import es.deusto.weblab.client.dto.experiments.Category;
import es.deusto.weblab.client.dto.experiments.Command;
import es.deusto.weblab.client.dto.experiments.EmptyResponseCommand;
import es.deusto.weblab.client.dto.experiments.ExperimentAllowed;
import es.deusto.weblab.client.dto.experiments.ExperimentID;
import es.deusto.weblab.client.dto.experiments.ResponseCommand;
import es.deusto.weblab.client.dto.reservations.ConfirmedReservationStatus;
import es.deusto.weblab.client.dto.reservations.PostReservationReservationStatus;
import es.deusto.weblab.client.dto.reservations.ReservationStatus;
import es.deusto.weblab.client.dto.reservations.WaitingConfirmationReservationStatus;
import es.deusto.weblab.client.dto.reservations.WaitingInstancesReservationStatus;
import es.deusto.weblab.client.dto.reservations.WaitingReservationStatus;
import es.deusto.weblab.client.experiments.xilinx.commands.PulseCommand;
import es.deusto.weblab.client.lab.comm.exceptions.NoCurrentReservationException;
import es.deusto.weblab.client.lab.comm.exceptions.UnknownExperimentIdException;

public class LabSerializerJSONTest extends GWTTestCase{
    
	public void testParseGetReservationStatusResponse_Waiting() throws Exception{
		final ILabSerializer weblabSerializer = new LabSerializerJSON();
		final ReservationStatus reservation = weblabSerializer.parseGetReservationStatusResponse(
			"{\"result\": {\"reservation_id\" : {\"id\" : \"my_reservation_id\"}, \"status\": \"Reservation::waiting\", \"position\": 5}, \"is_exception\": false}"
		);
		Assert.assertEquals("my_reservation_id", reservation.getReservationId());
		Assert.assertTrue(reservation instanceof WaitingReservationStatus);
		Assert.assertEquals(5, ((WaitingReservationStatus)reservation).getPosition());
	}

	public void testParseGetReservationStatusResponse_WaitingConfirmation()  throws Exception{
		final ILabSerializer weblabSerializer = new LabSerializerJSON();
		final ReservationStatus reservation = weblabSerializer.parseGetReservationStatusResponse(
			"{\"result\": {\"reservation_id\" : {\"id\" : \"my_reservation_id\"}, \"status\": \"Reservation::waiting_confirmation\"}, \"is_exception\": false}"
		);
		Assert.assertEquals("my_reservation_id", reservation.getReservationId());
		Assert.assertTrue(reservation instanceof WaitingConfirmationReservationStatus);
	}

	public void testParseGetReservationStatusResponse_WaitingInstances()  throws Exception{
		final ILabSerializer weblabSerializer = new LabSerializerJSON();
		final ReservationStatus reservation = weblabSerializer.parseGetReservationStatusResponse(
			"{\"result\": {\"reservation_id\" : {\"id\" : \"my_reservation_id\"}, \"status\": \"Reservation::waiting_instances\", \"position\" : 5}, \"is_exception\": false}"
		);
		Assert.assertEquals("my_reservation_id", reservation.getReservationId());
		Assert.assertTrue(reservation instanceof WaitingInstancesReservationStatus);
		Assert.assertEquals(5, ((WaitingInstancesReservationStatus)reservation).getPosition());
	}

	public void testParseGetReservationStatusResponse_PostReservation()  throws Exception{
		final ILabSerializer weblabSerializer = new LabSerializerJSON();
		final ReservationStatus reservation = weblabSerializer.parseGetReservationStatusResponse(
			"{\"result\": {\"reservation_id\" : {\"id\" : \"my_reservation_id\"}, \"status\": \"Reservation::post_reservation\", \"finished\" : true, \"initial_data\" : \"\\\"foo\\\"\", \"end_data\" : \"\\\"bar\\\"\"}, \"is_exception\": false}"
		);
		Assert.assertEquals("my_reservation_id", reservation.getReservationId());
		Assert.assertTrue(reservation instanceof PostReservationReservationStatus);
		PostReservationReservationStatus status = (PostReservationReservationStatus)reservation;
		Assert.assertEquals(true, status.isFinished());
		Assert.assertEquals("foo", status.getInitialData());
		Assert.assertEquals("bar", status.getEndData());
	}

	public void testParseGetReservationStatusResponse_Confirmed() throws Exception{
		final ILabSerializer weblabSerializer = new LabSerializerJSON();
		final ReservationStatus reservation = weblabSerializer.parseGetReservationStatusResponse(
			"{\"result\": {\"reservation_id\" : {\"id\" : \"my_reservation_id\"}, \"status\": \"Reservation::confirmed\", \"time\": 28.771512031555176, \"initial_configuration\" : \"foo\", \"url\" : \"http://...\", \"remote_reservation_id\" : { \"id\": \"\"} }, \"is_exception\": false}"
		);
		Assert.assertEquals("my_reservation_id", reservation.getReservationId());
		Assert.assertTrue(reservation instanceof ConfirmedReservationStatus);
		Assert.assertEquals(28, ((ConfirmedReservationStatus)reservation).getTime());
		Assert.assertEquals("foo", ((ConfirmedReservationStatus)reservation).getInitialConfiguration());
		Assert.assertEquals("http://...", ((ConfirmedReservationStatus)reservation).getUrl());
		Assert.assertEquals("", ((ConfirmedReservationStatus)reservation).getRemoteReservationId());
		Assert.assertFalse(((ConfirmedReservationStatus)reservation).isRemote());
	}
	
	public void testParseGetReservationStatusResponse_Exceptions() throws Exception{
		final ILabSerializer weblabSerializer = new LabSerializerJSON();
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
	
	public void testParsePollResponse() throws Exception{
		final ILabSerializer weblabSerializer = new LabSerializerJSON();
		weblabSerializer.parsePollResponse(
				"{\"result\": {}, \"is_exception\": false}"
			);
	}

	public void testParsePollResponse_Faults() throws Exception{
		final ILabSerializer weblabSerializer = new LabSerializerJSON();
		
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
		} catch (final WebLabServerException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
		try {
			weblabSerializer.parsePollResponse(
				whole_message.replaceFirst("THE_FAULT_CODE", "JSON:Server.Voodoo")
			);
			Assert.fail("Exception expected");
		} catch (final WebLabServerException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
		try {
			weblabSerializer.parsePollResponse(
				whole_message.replaceFirst("THE_FAULT_CODE", "JSON:Server.Python")
			);
			Assert.fail("Exception expected");
		} catch (final WebLabServerException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
	}

	public void testParsePollResponse_Exceptions() throws Exception{
		final ILabSerializer weblabSerializer = new LabSerializerJSON();
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
	
	
	public void testParseCheckAsyncCommandStatusResponse() throws Exception {
		final ILabSerializer weblabSerializer = new LabSerializerJSON();
		final String json = "{ \"result\" : { \"AAAA\": [\"running\", \"\"], \"BBBB\" : [\"ok\", \"Success\"], \"CCCC\" : [\"error\", \"Error\"] }, \"is_exception\" : false }";
		final AsyncRequestStatus [] requests = weblabSerializer.parseCheckAsyncCommandStatusResponse(json);
	
		Assert.assertEquals(3, requests.length);
		
		AsyncRequestStatus first = requests[0];
		Assert.assertEquals("AAAA", first.getRequestID());
		Assert.assertTrue(first.isRunning());
		Assert.assertFalse(first.isSuccessfullyFinished());
		Assert.assertFalse(first.isError());
		
		AsyncRequestStatus second = requests[1];
		Assert.assertEquals("BBBB", second.getRequestID());
		Assert.assertTrue(second.isSuccessfullyFinished());
		Assert.assertFalse(second.isRunning());
		Assert.assertFalse(second.isError());
		Assert.assertEquals("Success", second.getResponse());
		
		AsyncRequestStatus third = requests[2];
		Assert.assertEquals("CCCC", third.getRequestID());
		Assert.assertFalse(third.isSuccessfullyFinished());
		Assert.assertFalse(third.isRunning());
		Assert.assertTrue(third.isError());
		Assert.assertEquals("Error", third.getResponse());
	}
	
	public void testParseSendAsyncCommandResponse() throws Exception{
		final ILabSerializer weblabSerializer = new LabSerializerJSON();
		final ResponseCommand command = weblabSerializer.parseSendAsyncCommandResponse(
			"{\"result\": \"ABCDEFGH\", \"is_exception\": false}"
		);
		Assert.assertEquals("ABCDEFGH", command.getCommandString());
	}

	public void testParseSendCommandResponse() throws Exception{
		final ILabSerializer weblabSerializer = new LabSerializerJSON();
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
		final ILabSerializer weblabSerializer = new LabSerializerJSON();
		
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
		} catch (final WebLabServerException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
		try {
			weblabSerializer.parseSendCommandResponse(
				whole_message.replaceFirst("THE_FAULT_CODE", "JSON:Server.Voodoo")
			);
			Assert.fail("Exception expected");
		} catch (final WebLabServerException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
		try {
			weblabSerializer.parseSendCommandResponse(
				whole_message.replaceFirst("THE_FAULT_CODE", "JSON:Server.Python")
			);
			Assert.fail("Exception expected");
		} catch (final WebLabServerException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
	}

	public void testParseSendCommandResponse_Exceptions() throws Exception{
		final ILabSerializer weblabSerializer = new LabSerializerJSON();
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
		final ILabSerializer weblabSerializer = new LabSerializerJSON();
		final String realResponse = "the_real_response";
		final ResponseCommand command2 = weblabSerializer.parseSendFileResponse(
			"<body>SUCCESS@" + realResponse + "</body>"
		);
		Assert.assertEquals(realResponse, command2.getCommandString());
	}

	public void testParseSendFileResponse_Faults() throws Exception{
		final ILabSerializer weblabSerializer = new LabSerializerJSON();
		
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
		} catch (final WebLabServerException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
		try {
			weblabSerializer.parseSendFileResponse(
				whole_message.replaceFirst("THE_FAULT_CODE", "XMLRPC:Server.Voodoo")
			);
			Assert.fail("Exception expected");
		} catch (final WebLabServerException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
		try {
			weblabSerializer.parseSendFileResponse(
				whole_message.replaceFirst("THE_FAULT_CODE", "XMLRPC:Server.Python")
			);
			Assert.fail("Exception expected");
		} catch (final WebLabServerException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
	}

	public void testParseSendFileResponse_Exceptions() throws Exception{
		final ILabSerializer weblabSerializer = new LabSerializerJSON();
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
		final ILabSerializer weblabSerializer = new LabSerializerJSON();
		weblabSerializer.parseFinishedExperimentResponse(
			"{\"result\": {}, \"is_exception\": false}"
		);
	}

	public void testParseFinishedExperimentResponse_Faults() throws Exception{
		final ILabSerializer weblabSerializer = new LabSerializerJSON();
		
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
		} catch (final WebLabServerException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
		try {
			weblabSerializer.parseFinishedExperimentResponse(
				whole_message.replaceFirst("THE_FAULT_CODE", "JSON:Server.Voodoo")
			);
			Assert.fail("Exception expected");
		} catch (final WebLabServerException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
		try {
			weblabSerializer.parseFinishedExperimentResponse(
				whole_message.replaceFirst("THE_FAULT_CODE", "JSON:Server.Python")
			);
			Assert.fail("Exception expected");
		} catch (final WebLabServerException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
	}

	public void testParseFinishedExperimentResponse_Exceptions() throws Exception{
		final ILabSerializer weblabSerializer = new LabSerializerJSON();
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
		final ILabSerializer weblabSerializer = new LabSerializerJSON();
		final ReservationStatus reservation = weblabSerializer.parseReserveExperimentResponse(
			"{\"result\": {\"reservation_id\" : {\"id\" : \"my_reservation_id\"}, \"status\": \"Reservation::waiting\", \"position\": 5}, \"is_exception\": false}"
		);
		Assert.assertEquals("my_reservation_id", reservation.getReservationId());
		Assert.assertTrue(reservation instanceof WaitingReservationStatus);
		Assert.assertEquals(5, ((WaitingReservationStatus)reservation).getPosition());
	}

	public void testParseReserveExperimentResponse_Faults() throws Exception{
		final ILabSerializer weblabSerializer = new LabSerializerJSON();
		
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
		} catch (final WebLabServerException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
		try {
			weblabSerializer.parseReserveExperimentResponse(
				whole_message.replaceFirst("THE_FAULT_CODE", "JSON:Server.Voodoo")
			);
			Assert.fail("Exception expected");
		} catch (final WebLabServerException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
		try {
			weblabSerializer.parseReserveExperimentResponse(
				whole_message.replaceFirst("THE_FAULT_CODE", "JSON:Server.Python")
			);
			Assert.fail("Exception expected");
		} catch (final WebLabServerException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
	}

	public void testParseReserveExperimentResponse_WaitingConfirmation()  throws Exception{
		final ILabSerializer weblabSerializer = new LabSerializerJSON();
		final ReservationStatus reservation = weblabSerializer.parseReserveExperimentResponse(
			"{\"result\": {\"reservation_id\" : {\"id\" : \"my_reservation_id\"}, \"status\": \"Reservation::waiting_confirmation\"}, \"is_exception\": false}"
		);
		Assert.assertEquals("my_reservation_id", reservation.getReservationId());
		Assert.assertTrue(reservation instanceof WaitingConfirmationReservationStatus);
	}

	public void testParseReserveExperimentResponse_WaitingInstances()  throws Exception{
		final ILabSerializer weblabSerializer = new LabSerializerJSON();
		final ReservationStatus reservation = weblabSerializer.parseReserveExperimentResponse(
			"{\"result\": {\"reservation_id\" : {\"id\" : \"my_reservation_id\"}, \"status\": \"Reservation::waiting_instances\", \"position\": 5}, \"is_exception\": false}"
		);
		Assert.assertEquals("my_reservation_id", reservation.getReservationId());
		Assert.assertTrue(reservation instanceof WaitingInstancesReservationStatus);
		Assert.assertEquals(5, ((WaitingInstancesReservationStatus)reservation).getPosition());
	}

	public void testParseReserveExperimentResponse_PostReservation()  throws Exception{
		final ILabSerializer weblabSerializer = new LabSerializerJSON();
		final ReservationStatus reservation = weblabSerializer.parseReserveExperimentResponse(
			"{\"result\": {\"reservation_id\" : {\"id\" : \"my_reservation_id\"}, \"status\": \"Reservation::post_reservation\", \"finished\" : true, \"initial_data\" : \"\\\"foo\\\"\", \"end_data\" : \"\\\"bar\\\"\" }, \"is_exception\": false}"
		);
		Assert.assertEquals("my_reservation_id", reservation.getReservationId());
		Assert.assertTrue(reservation instanceof PostReservationReservationStatus);
		final PostReservationReservationStatus status = (PostReservationReservationStatus)reservation;
		Assert.assertTrue(status.isFinished());
		Assert.assertEquals("foo", status.getInitialData());
		Assert.assertEquals("bar", status.getEndData());
	}

	public void testParseReserveExperimentResponse_Confirmed() throws Exception{
		final ILabSerializer weblabSerializer = new LabSerializerJSON();
		final ReservationStatus reservation = weblabSerializer.parseReserveExperimentResponse(
			"{\"result\": {\"reservation_id\" : {\"id\" : \"my_reservation_id\"}, \"status\": \"Reservation::confirmed\", \"time\": 28.771512031555176, \"initial_configuration\" : \"foo\", \"url\" : \"http://...\", \"remote_reservation_id\" : { \"id\" : \"\" } }, \"is_exception\": false}"
		);
		Assert.assertEquals("my_reservation_id", reservation.getReservationId());
		Assert.assertTrue(reservation instanceof ConfirmedReservationStatus);
		Assert.assertEquals(28, ((ConfirmedReservationStatus)reservation).getTime());
		Assert.assertEquals("foo", ((ConfirmedReservationStatus)reservation).getInitialConfiguration());
		Assert.assertEquals("http://...", ((ConfirmedReservationStatus)reservation).getUrl());
		Assert.assertEquals("", ((ConfirmedReservationStatus)reservation).getRemoteReservationId());
		Assert.assertFalse(((ConfirmedReservationStatus)reservation).isRemote());
	}
	
	public void testParseReserveExperimentResponse_ConfirmedRemote() throws Exception{
		final ILabSerializer weblabSerializer = new LabSerializerJSON();
		final ReservationStatus reservation = weblabSerializer.parseReserveExperimentResponse(
			"{\"result\": {\"reservation_id\" : {\"id\" : \"my_reservation_id\"}, \"status\": \"Reservation::confirmed\", \"time\": 28.771512031555176, \"initial_configuration\" : \"foo\", \"url\" : \"http://...\", \"remote_reservation_id\" : { \"id\" : \"foobar\" }}, \"is_exception\": false}"
		);
		Assert.assertEquals("my_reservation_id", reservation.getReservationId());
		Assert.assertTrue(reservation instanceof ConfirmedReservationStatus);
		Assert.assertEquals(28, ((ConfirmedReservationStatus)reservation).getTime());
		Assert.assertEquals("foo", ((ConfirmedReservationStatus)reservation).getInitialConfiguration());
		Assert.assertEquals("http://...", ((ConfirmedReservationStatus)reservation).getUrl());
		Assert.assertEquals("foobar", ((ConfirmedReservationStatus)reservation).getRemoteReservationId());
		Assert.assertTrue(((ConfirmedReservationStatus)reservation).isRemote());
	}
	
	public void testParseReserveExperimentResponse_Exceptions() throws Exception{
		final ILabSerializer weblabSerializer = new LabSerializerJSON();
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
		final ILabSerializer weblabSerializer = new LabSerializerJSON();
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
		
		final long timezoneOffset = DateTimeFormat.getFormat("yyyy-MM-dd").parse("1970-01-01").getTime();
		
		
		// 2007-01-01 00:00:00
		Assert.assertEquals(1167609600000L + timezoneOffset, experiments[0].getExperiment().getStartDate().getTime());
		// 2008-01-01 00:00:00
		Assert.assertEquals(1199145600000L + timezoneOffset, experiments[0].getExperiment().getEndDate().getTime());
		
		// 1
		Assert.assertEquals(30,                              experiments[1].getTimeAllowed());
		Assert.assertEquals("ud-fpga",                       experiments[1].getExperiment().getName());
		Assert.assertEquals("FPGA experiments",              experiments[1].getExperiment().getCategory().getCategory());
		
		// 2005-01-01 00:00:00
		Assert.assertEquals(1104537600000L + timezoneOffset, experiments[1].getExperiment().getStartDate().getTime());
		// 2006-01-01 00:00:00
		Assert.assertEquals(1136073600000L + timezoneOffset, experiments[1].getExperiment().getEndDate().getTime());		
	}

	public void testParseListExperimentsResponseWithOtherDateFormat() throws Exception{
		final ILabSerializer weblabSerializer = new LabSerializerJSON();
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
		
		final long timezoneOffset = DateTimeFormat.getFormat("yyyy-MM-dd").parse("1970-01-01").getTime();
		
		// 2007-01-01 00:00:00
		Assert.assertEquals(1167609600000L + timezoneOffset, experiments[0].getExperiment().getStartDate().getTime());
		// 2008-01-01 00:00:00
		Assert.assertEquals(1199145600000L + timezoneOffset, experiments[0].getExperiment().getEndDate().getTime());
		
		// 1
		Assert.assertEquals(30,                              experiments[1].getTimeAllowed());
		Assert.assertEquals("ud-fpga",                       experiments[1].getExperiment().getName());
		Assert.assertEquals("FPGA experiments",              experiments[1].getExperiment().getCategory().getCategory());
		
		// 2005-01-01 00:00:00
		Assert.assertEquals(1104537600000L + timezoneOffset, experiments[1].getExperiment().getStartDate().getTime());
		// 2006-01-01 00:00:00
		Assert.assertEquals(1136073600000L + timezoneOffset, experiments[1].getExperiment().getEndDate().getTime());		
	}
	
	public void testParseListExperimentsResponseWithYetAnotherOtherDateFormat() throws Exception{
		final ILabSerializer weblabSerializer = new LabSerializerJSON();
		final ExperimentAllowed [] experiments = weblabSerializer.parseListExperimentsResponse(
			"{\"result\": [" +
				"{\"experiment\": {\"category\": {\"name\": \"Dummy experiments\"}, \"owner\": \"porduna@tecnologico.deusto.es\", " +
					"\"name\": \"ud-dummy\", \"end_date\": \"2008-01-01T00:00:00.330016\", \"start_date\": \"2007-01-01T00:00:00.330016\"}, \"time_allowed\": 30.0}, " +
				"{\"experiment\": {\"category\": {\"name\": \"FPGA experiments\"}, \"owner\": \"porduna@tecnologico.deusto.es\", " +
					"\"name\": \"ud-fpga\", \"end_date\": \"2006-01-01T00:00:00.330016\", \"start_date\": \"2005-01-01T00:00:00.330016\"}, \"time_allowed\": 30.0}" +
			"], \"is_exception\": false}"
		);
		
		Assert.assertEquals(2, experiments.length);
		
		// 0
		Assert.assertEquals(30,                              experiments[0].getTimeAllowed());
		Assert.assertEquals("ud-dummy",                      experiments[0].getExperiment().getName());
		Assert.assertEquals("Dummy experiments",             experiments[0].getExperiment().getCategory().getCategory());
		
		final long timezoneOffset = DateTimeFormat.getFormat("yyyy-MM-dd").parse("1970-01-01").getTime();
		
		// 2007-01-01 00:00:00
		Assert.assertEquals(1167609600330L + timezoneOffset, experiments[0].getExperiment().getStartDate().getTime());
		// 2008-01-01 00:00:00
		Assert.assertEquals(1199145600330L + timezoneOffset, experiments[0].getExperiment().getEndDate().getTime());
		
		// 1
		Assert.assertEquals(30,                              experiments[1].getTimeAllowed());
		Assert.assertEquals("ud-fpga",                       experiments[1].getExperiment().getName());
		Assert.assertEquals("FPGA experiments",              experiments[1].getExperiment().getCategory().getCategory());
		
		// 2005-01-01 00:00:00
		Assert.assertEquals(1104537600330L + timezoneOffset, experiments[1].getExperiment().getStartDate().getTime());
		// 2006-01-01 00:00:00
		Assert.assertEquals(1136073600330L + timezoneOffset, experiments[1].getExperiment().getEndDate().getTime());		
	}

	public void testParseListExperimentsResponse_Faults() throws Exception{
		final ILabSerializer weblabSerializer = new LabSerializerJSON();
		
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
		} catch (final WebLabServerException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
		try {
			weblabSerializer.parseListExperimentsResponse(
				whole_message.replaceFirst("THE_FAULT_CODE", "JSON:Server.Voodoo")
			);
			Assert.fail("Exception expected");
		} catch (final WebLabServerException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
		try {
			weblabSerializer.parseListExperimentsResponse(
				whole_message.replaceFirst("THE_FAULT_CODE", "JSON:Server.Python")
			);
			Assert.fail("Exception expected");
		} catch (final WebLabServerException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
	}

	public void testSerializeGetReservationStatusRequest() throws Exception{
		final ILabSerializer weblabSerializer = new LabSerializerJSON();
		final String MESSAGE = "whatever the session id real id";
		
		final SessionID sessionId = new SessionID(MESSAGE);
		final String serializedMessage = weblabSerializer.serializeGetReservationStatusRequest(sessionId);
		
		Assert.assertEquals(
				"{\"params\":{\"reservation_id\":{\"id\":\"" + MESSAGE + "\"}}, \"method\":\"get_reservation_status\"}",
				serializedMessage
			);
	}
	
	public void testSerializeListExperimentsRequest() throws Exception{
		final ILabSerializer weblabSerializer = new LabSerializerJSON();
		final String MESSAGE = "whatever the session id real id";
		
		final SessionID sessionId = new SessionID(MESSAGE);
		final String serializedMessage = weblabSerializer.serializeListExperimentsRequest(sessionId);
		
		Assert.assertEquals(
				"{\"params\":{\"session_id\":{\"id\":\"" + MESSAGE + "\"}}, \"method\":\"list_experiments\"}",
				serializedMessage
			);
	}
	
	public void testSerializePollRequest() throws Exception{
		final ILabSerializer weblabSerializer = new LabSerializerJSON();
		final String MESSAGE = "whatever the session id real id";
		
		final SessionID sessionId = new SessionID(MESSAGE);
		final String serializedMessage = weblabSerializer.serializePollRequest(sessionId);
		
		Assert.assertEquals(
				"{\"params\":{\"reservation_id\":{\"id\":\"" + MESSAGE + "\"}}, \"method\":\"poll\"}",
				serializedMessage
			);
	}
	
	public void testSerializeFinishedExperimentRequest() throws Exception{
		final ILabSerializer weblabSerializer = new LabSerializerJSON();
		final String MESSAGE = "whatever the session id real id";
		
		final SessionID sessionId = new SessionID(MESSAGE);
		final String serializedMessage = weblabSerializer.serializeFinishedExperimentRequest(sessionId);
		
		Assert.assertEquals(
				"{\"params\":{\"reservation_id\":{\"id\":\"" + MESSAGE + "\"}}, \"method\":\"finished_experiment\"}",
				serializedMessage
			);
	}
	
	public void testSerializeReserveExperimentRequest() throws Exception{
		final ILabSerializer weblabSerializer = new LabSerializerJSON();
		
		final String MESSAGE = "whatever the session id real id";
		
		final SessionID sessionId = new SessionID(MESSAGE);
		final ExperimentID experiment = new ExperimentID(
				new Category("WebLab-PLD experiments"),
				"weblab-pld"
			);
		
		final String serializedMessage = weblabSerializer.serializeReserveExperimentRequest(sessionId, experiment, new JSONObject());
		Assert.assertEquals(
				"{\"params\":{\"session_id\":{\"id\":\"" + MESSAGE + "\"}," +
						" \"experiment_id\":{\"exp_name\":\"weblab-pld\", \"cat_name\":\"WebLab-PLD experiments\"}, \"client_initial_data\":\"{}\", \"consumer_data\":\"{}\"}, " +
						"\"method\":\"reserve_experiment\"}",
				serializedMessage
			);
	}
	
	
	public void testSerializeAsyncCommandRequest() throws Exception {
		final ILabSerializer weblabSerializer = new LabSerializerJSON();
		
		final String MESSAGE = "whatever the session id real id";
		
		final SessionID sessionId = new SessionID(MESSAGE);
		final Command command = new PulseCommand(5, true);
		
		final String serializedMessage = weblabSerializer.serializeSendAsyncCommandRequest(
				sessionId, command);
		
		Assert.assertEquals(
				"{\"params\":{\"reservation_id\":{\"id\":\"" + MESSAGE + "\"}, \"command\":{\"commandstring\":\"" + command.getCommandString() + "\"}}, \"method\":\"send_async_command\"}",
				serializedMessage
			);
	}
	
	
	public void testSerializeCommandRequest() throws Exception{
		final ILabSerializer weblabSerializer = new LabSerializerJSON();
		
		final String MESSAGE = "whatever the session id real id";
		
		final SessionID sessionId = new SessionID(MESSAGE);
		final Command command = new PulseCommand(5,true); 
		
		final String serializedMessage = weblabSerializer.serializeSendCommandRequest(sessionId, command);
		
		Assert.assertEquals(
				"{\"params\":{\"reservation_id\":{\"id\":\"" + MESSAGE + "\"}, \"command\":{\"commandstring\":\"" + command.getCommandString() + "\"}}, \"method\":\"send_command\"}",
				serializedMessage
			);
	}    	
    
	@Override
	public String getModuleName() {
		return "es.deusto.weblab.WebLabClient";
	}
}
