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

import java.util.Date;
import java.util.HashMap;

import junit.framework.Assert;

import com.google.gwt.http.client.Header;
import com.google.gwt.http.client.RequestException;
import com.google.gwt.http.client.Response;
import com.google.gwt.junit.client.GWTTestCase;
import com.google.gwt.user.client.ui.FileUpload;
import com.google.gwt.user.client.ui.FormPanel;
import com.google.gwt.user.client.ui.FormPanel.SubmitCompleteEvent;

import es.deusto.weblab.client.comm.callbacks.ISessionIdCallback;
import es.deusto.weblab.client.comm.callbacks.IUserInformationCallback;
import es.deusto.weblab.client.comm.callbacks.IVoidCallback;
import es.deusto.weblab.client.comm.exceptions.CommunicationException;
import es.deusto.weblab.client.comm.exceptions.ServerException;
import es.deusto.weblab.client.comm.exceptions.WlCommException;
import es.deusto.weblab.client.configuration.FakeConfiguration;
import es.deusto.weblab.client.dto.SessionID;
import es.deusto.weblab.client.dto.experiments.Category;
import es.deusto.weblab.client.dto.experiments.Command;
import es.deusto.weblab.client.dto.experiments.Experiment;
import es.deusto.weblab.client.dto.experiments.ExperimentAllowed;
import es.deusto.weblab.client.dto.experiments.ExperimentID;
import es.deusto.weblab.client.dto.experiments.ResponseCommand;
import es.deusto.weblab.client.dto.reservations.ConfirmedReservationStatus;
import es.deusto.weblab.client.dto.reservations.ReservationStatus;
import es.deusto.weblab.client.dto.users.Role;
import es.deusto.weblab.client.dto.users.User;
import es.deusto.weblab.client.lab.comm.UploadStructure;
import es.deusto.weblab.client.lab.comm.WlLabCommunication;
import es.deusto.weblab.client.lab.comm.callbacks.IExperimentsAllowedCallback;
import es.deusto.weblab.client.lab.comm.callbacks.IReservationCallback;
import es.deusto.weblab.client.lab.comm.callbacks.IResponseCommandCallback;
import es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.xilinx.commands.SwitchCommand;

public class WebLabCommunicationTest extends GWTTestCase {

	private int stepCounter;
	
	private Response generateBadResponse(){
		return new Response(){
			@Override
			public String getHeader(String header) {
				return null;
			}

			@Override
			public Header[] getHeaders() {
				return null;
			}

			@Override
			public String getHeadersAsString() {
				return null;
			}

			@Override
			public int getStatusCode() {
				return 503;
			}

			@Override
			public String getStatusText() {
				return "fail!";
			}

			@Override
			public String getText() {
				return "whatever";
			}
		};
	}
	
	public void testGetReservationStatus(){
		this.stepCounter = 0;
		
		final FakeWebLabSerializer weblabSerializer = new FakeWebLabSerializer();
		final FakeRequestBuilder requestBuilder = new FakeRequestBuilder();
		final FakeConfiguration configurationManager = new FakeConfiguration(new HashMap<String, String>());
		
		final WrappedWebLabCommunication comms = new WrappedWebLabCommunication(
					weblabSerializer,
					requestBuilder,
					configurationManager
				);
		final SessionID sessionId = new SessionID();
		
		final int TIME = 100;
		final String SERIALIZED_MESSAGE = "serialized get reservation status request";
		final String ERROR_MESSAGE = "whatever the error message";
		
		weblabSerializer.appendReturn(
					FakeWebLabSerializer.PARSE_GET_RESERVATION_STATUS_RESPONSE, 
					new ConfirmedReservationStatus(TIME)
				);
		weblabSerializer.appendReturn(
					FakeWebLabSerializer.SERIALIZE_GET_RESERVATION_STATUS_REQUEST, 
					SERIALIZED_MESSAGE
				);
		
		IReservationCallback rc = new IReservationCallback(){
			public void onSuccess(ReservationStatus reservation) {
				Assert.assertTrue(reservation instanceof ConfirmedReservationStatus);
				Assert.assertEquals(TIME, ((ConfirmedReservationStatus)reservation).getTime());
				WebLabCommunicationTest.this.stepCounter++;
			}

			public void onFailure(WlCommException e) {
				Assert.fail("onFailure not expected");
			}
		};
		
		requestBuilder.setNextReceivedMessage(SERIALIZED_MESSAGE);		
		comms.getReservationStatus(sessionId, rc);
		Assert.assertEquals(1, this.stepCounter);
		
		requestBuilder.setNextToThrow(new RequestException(ERROR_MESSAGE));
		rc = new IReservationCallback(){
			public void onSuccess(ReservationStatus reservation){
				Assert.fail("onSuccess not expected");
			}
			
			public void onFailure(WlCommException e){
				Assert.assertTrue(e instanceof CommunicationException);
				Assert.assertEquals(ERROR_MESSAGE, e.getMessage());
				WebLabCommunicationTest.this.stepCounter++;
			}
		};
		comms.getReservationStatus(sessionId, rc);
		Assert.assertEquals(2, this.stepCounter);
		
		requestBuilder.setNextToError(new Exception(ERROR_MESSAGE));
		rc = new IReservationCallback(){
			public void onSuccess(ReservationStatus reservation){
				Assert.fail("onSuccess not expected");
			}
			
			public void onFailure(WlCommException e){
				Assert.assertTrue(e instanceof CommunicationException);
				Assert.assertEquals(ERROR_MESSAGE, e.getMessage());
				WebLabCommunicationTest.this.stepCounter++;
			}
		};
		comms.getReservationStatus(sessionId, rc);
		Assert.assertEquals(3, this.stepCounter);
		
		requestBuilder.setNextReceivedMessage("");
		requestBuilder.setResponseToSend(this.generateBadResponse());
		rc = new IReservationCallback(){
			public void onSuccess(ReservationStatus reservation){
				Assert.fail("onSuccess not expected");
			}
			
			public void onFailure(WlCommException e){
				Assert.assertTrue(e instanceof ServerException);
				WebLabCommunicationTest.this.stepCounter++;
			}
		};
		comms.getReservationStatus(sessionId, rc);
		Assert.assertEquals(4, this.stepCounter);
	}

	public void testGetUserInformation(){
		this.stepCounter = 0;
		final FakeWebLabSerializer weblabSerializer = new FakeWebLabSerializer();
		final FakeRequestBuilder requestBuilder = new FakeRequestBuilder();
		final FakeConfiguration configurationManager = new FakeConfiguration(new HashMap<String,String>());
				
		final WrappedWebLabCommunication comms = new WrappedWebLabCommunication(
					weblabSerializer,
					requestBuilder,
					configurationManager
				);
		final SessionID sessionId = new SessionID();
		
		final String SERIALIZED_MESSAGE = "serialized get reservation status request";
		final String ERROR_MESSAGE = "whatever the error message";
		final User user = new User();
		user.setEmail("porduna@tecnologico.deusto.es");
		user.setFullName("Pablo Orduña");
		user.setLogin("porduna");
		final Role role = new Role();
		role.setName("student");
		user.setRole(role);
		
		weblabSerializer.appendReturn(
					FakeWebLabSerializer.PARSE_GET_USER_INFORMATION_RESPONSE, 
					user
				);
		weblabSerializer.appendReturn(
					FakeWebLabSerializer.SERIALIZE_GET_USER_INFORMATION_REQUEST, 
					SERIALIZED_MESSAGE
				);
		
		IUserInformationCallback uic = new IUserInformationCallback(){
			public void onSuccess(User userInformation) {
				Assert.assertEquals(user.getEmail(),    userInformation.getEmail());
				Assert.assertEquals(user.getFullName(), userInformation.getFullName());
				Assert.assertEquals(user.getLogin(),    userInformation.getLogin());
				WebLabCommunicationTest.this.stepCounter++;
			}

			public void onFailure(WlCommException e) {
				Assert.fail("onFailure not expected");
			}
		};
		
		requestBuilder.setNextReceivedMessage(SERIALIZED_MESSAGE);		
		comms.getUserInformation(sessionId, uic);
		Assert.assertEquals(1, this.stepCounter);
		
		requestBuilder.setNextToThrow(new RequestException(ERROR_MESSAGE));
		uic = new IUserInformationCallback(){
			public void onSuccess(User userInformation){
				Assert.fail("onSuccess not expected");
			}
			
			public void onFailure(WlCommException e){
				Assert.assertTrue(e instanceof CommunicationException);
				Assert.assertEquals(ERROR_MESSAGE, e.getMessage());
				WebLabCommunicationTest.this.stepCounter++;
			}
		};
		comms.getUserInformation(sessionId, uic);
		Assert.assertEquals(2, this.stepCounter);
		
		requestBuilder.setNextToError(new Exception(ERROR_MESSAGE));
		uic = new IUserInformationCallback(){
			public void onSuccess(User userInformation){
				Assert.fail("onSuccess not expected");
			}
			
			public void onFailure(WlCommException e){
				Assert.assertTrue(e instanceof CommunicationException);
				Assert.assertEquals(ERROR_MESSAGE, e.getMessage());
				WebLabCommunicationTest.this.stepCounter++;
			}
		};
		comms.getUserInformation(sessionId, uic);
		Assert.assertEquals(3, this.stepCounter);
		
		requestBuilder.setNextReceivedMessage("");
		requestBuilder.setResponseToSend(this.generateBadResponse());
		uic = new IUserInformationCallback(){
			public void onSuccess(User userInformation){
				Assert.fail("onSuccess not expected");
			}
			
			public void onFailure(WlCommException e){
				Assert.assertTrue(e instanceof ServerException);
				WebLabCommunicationTest.this.stepCounter++;
			}
		};
		comms.getUserInformation(sessionId, uic);
		Assert.assertEquals(4, this.stepCounter);
	}
	
	public void testListExperiments(){
		this.stepCounter = 0;
		final FakeWebLabSerializer weblabSerializer = new FakeWebLabSerializer();
		final FakeRequestBuilder requestBuilder = new FakeRequestBuilder();
		final FakeConfiguration configurationManager = new FakeConfiguration(new HashMap<String,String>());
				
		final WrappedWebLabCommunication comms = new WrappedWebLabCommunication(
					weblabSerializer,
					requestBuilder,
					configurationManager
				);
		final SessionID sessionId = new SessionID();
		
		final String SERIALIZED_MESSAGE = "serialized get reservation status request";
		final String ERROR_MESSAGE = "whatever the error message";
		final ExperimentAllowed [] experiments = new ExperimentAllowed[1];
		experiments[0] = new ExperimentAllowed(
				new Experiment("Experiment name", new Category("Category name"), new Date(), new Date()), 
				100
			);
		
		weblabSerializer.appendReturn(
					FakeWebLabSerializer.PARSE_LIST_EXPERIMENTS_RESPONSE, 
					experiments
				);
		weblabSerializer.appendReturn(
					FakeWebLabSerializer.SERIALIZE_LIST_EXPERIMENTS_REQUEST, 
					SERIALIZED_MESSAGE
				);
		
		IExperimentsAllowedCallback eac = new IExperimentsAllowedCallback(){
			public void onSuccess(ExperimentAllowed [] experimentsAllowed) {
				Assert.assertEquals(experiments.length, experimentsAllowed.length);
				Assert.assertEquals(experiments[0], experimentsAllowed[0]);
				WebLabCommunicationTest.this.stepCounter++;
			}

			public void onFailure(WlCommException e) {
				Assert.fail("onFailure not expected");
			}
		};
		
		requestBuilder.setNextReceivedMessage(SERIALIZED_MESSAGE);		
		comms.listExperiments(sessionId, eac);
		Assert.assertEquals(1, this.stepCounter);
		
		requestBuilder.setNextToThrow(new RequestException(ERROR_MESSAGE));
		eac = new IExperimentsAllowedCallback(){
			public void onSuccess(ExperimentAllowed [] experimentsAllowed){
				Assert.fail("onSuccess not expected");
			}
			
			public void onFailure(WlCommException e){
				Assert.assertTrue(e instanceof CommunicationException);
				Assert.assertEquals(ERROR_MESSAGE, e.getMessage());
				WebLabCommunicationTest.this.stepCounter++;
			}
		};
		comms.listExperiments(sessionId, eac);
		Assert.assertEquals(2, this.stepCounter);
		
		requestBuilder.setNextToError(new Exception(ERROR_MESSAGE));
		eac = new IExperimentsAllowedCallback(){
			public void onSuccess(ExperimentAllowed [] experimentsAllowed){
				Assert.fail("onSuccess not expected");
			}
			
			public void onFailure(WlCommException e){
				Assert.assertTrue(e instanceof CommunicationException);
				Assert.assertEquals(ERROR_MESSAGE, e.getMessage());
				WebLabCommunicationTest.this.stepCounter++;
			}
		};
		comms.listExperiments(sessionId, eac);
		Assert.assertEquals(3, this.stepCounter);
		
		requestBuilder.setNextReceivedMessage("");
		requestBuilder.setResponseToSend(this.generateBadResponse());
		eac = new IExperimentsAllowedCallback(){
			public void onSuccess(ExperimentAllowed [] experimentsAllowed){
				Assert.fail("onSuccess not expected");
			}
			
			public void onFailure(WlCommException e){
				Assert.assertTrue(e instanceof ServerException);
				WebLabCommunicationTest.this.stepCounter++;
			}
		};
		comms.listExperiments(sessionId, eac);
		Assert.assertEquals(4, this.stepCounter);
	}
	
	public void testLogin(){
		this.stepCounter = 0;
		final FakeWebLabSerializer weblabSerializer = new FakeWebLabSerializer();
		final FakeRequestBuilder requestBuilder = new FakeRequestBuilder();
		final FakeConfiguration configurationManager = new FakeConfiguration(new HashMap<String,String>());
				
		final WrappedWebLabCommunication comms = new WrappedWebLabCommunication(
					weblabSerializer,
					requestBuilder,
					configurationManager
				);
		final SessionID expectedSessionId = new SessionID("realid");
		
		final String SERIALIZED_MESSAGE = "serialized get reservation status request";
		final String ERROR_MESSAGE = "whatever the error message";
		final String USERNAME = "porduna";
		final String PASSWORD = "passwor";
		
		weblabSerializer.appendReturn(
					FakeWebLabSerializer.PARSE_LOGIN_RESPONSE, 
					expectedSessionId
				);
		weblabSerializer.appendReturn(
					FakeWebLabSerializer.SERIALIZE_LOGIN_REQUEST, 
					SERIALIZED_MESSAGE
				);
		
		ISessionIdCallback eac = new ISessionIdCallback(){
			public void onSuccess(SessionID sessionId) {
				Assert.assertEquals(expectedSessionId, sessionId);
				WebLabCommunicationTest.this.stepCounter++;
			}

			public void onFailure(WlCommException e) {
				Assert.fail("onFailure not expected");
			}
		};
		
		requestBuilder.setNextReceivedMessage(SERIALIZED_MESSAGE);		
		comms.login(USERNAME, PASSWORD, eac);
		Assert.assertEquals(1, this.stepCounter);
		
		requestBuilder.setNextToThrow(new RequestException(ERROR_MESSAGE));
		eac = new ISessionIdCallback(){
			public void onSuccess(SessionID sessionId){
				Assert.fail("onSuccess not expected");
			}
			
			public void onFailure(WlCommException e){
				Assert.assertTrue(e instanceof CommunicationException);
				Assert.assertEquals(ERROR_MESSAGE, e.getMessage());
				WebLabCommunicationTest.this.stepCounter++;
			}
		};
		comms.login(USERNAME, PASSWORD, eac);
		Assert.assertEquals(2, this.stepCounter);
		
		requestBuilder.setNextToError(new Exception(ERROR_MESSAGE));
		eac = new ISessionIdCallback(){
			public void onSuccess(SessionID sessionId){
				Assert.fail("onSuccess not expected");
			}
			
			public void onFailure(WlCommException e){
				Assert.assertTrue(e instanceof CommunicationException);
				Assert.assertEquals(ERROR_MESSAGE, e.getMessage());
				WebLabCommunicationTest.this.stepCounter++;
			}
		};
		comms.login(USERNAME, PASSWORD, eac);
		Assert.assertEquals(3, this.stepCounter);
		
		requestBuilder.setNextReceivedMessage("");
		requestBuilder.setResponseToSend(this.generateBadResponse());
		eac = new ISessionIdCallback(){
			public void onSuccess(SessionID sessionId){
				Assert.fail("onSuccess not expected");
			}
			
			public void onFailure(WlCommException e){
				Assert.assertTrue(e instanceof ServerException);
				WebLabCommunicationTest.this.stepCounter++;
			}
		};
		comms.login(USERNAME, PASSWORD, eac);
		Assert.assertEquals(4, this.stepCounter);
	}
	
	public void testLogout(){
		this.stepCounter = 0;
		final FakeWebLabSerializer weblabSerializer = new FakeWebLabSerializer();
		final FakeRequestBuilder requestBuilder = new FakeRequestBuilder();
		final FakeConfiguration configurationManager = new FakeConfiguration(new HashMap<String, String>());
				
		final WrappedWebLabCommunication comms = new WrappedWebLabCommunication(
					weblabSerializer,
					requestBuilder,
					configurationManager
				);
		final SessionID sessionId = new SessionID("whatever the session id");
		
		final String SERIALIZED_MESSAGE = "serialized get reservation status request";
		final String ERROR_MESSAGE = "whatever the error message";
		
		weblabSerializer.appendReturn(
					FakeWebLabSerializer.SERIALIZE_LOGOUT_REQUEST, 
					SERIALIZED_MESSAGE
				);
		
		IVoidCallback eac = new IVoidCallback(){
			public void onSuccess() {
				WebLabCommunicationTest.this.stepCounter++;
			}

			public void onFailure(WlCommException e) {
				Assert.fail("onFailure not expected");
			}
		};
		
		requestBuilder.setNextReceivedMessage(SERIALIZED_MESSAGE);		
		comms.logout(sessionId, eac);
		Assert.assertEquals(1, this.stepCounter);
		
		requestBuilder.setNextToThrow(new RequestException(ERROR_MESSAGE));
		eac = new IVoidCallback(){
			public void onSuccess(){
				Assert.fail("onSuccess not expected");
			}
			
			public void onFailure(WlCommException e){
				Assert.assertTrue(e instanceof CommunicationException);
				Assert.assertEquals(ERROR_MESSAGE, e.getMessage());
				WebLabCommunicationTest.this.stepCounter++;
			}
		};
		comms.logout(sessionId, eac);
		Assert.assertEquals(2, this.stepCounter);
		
		requestBuilder.setNextToError(new Exception(ERROR_MESSAGE));
		eac = new IVoidCallback(){
			public void onSuccess(){
				Assert.fail("onSuccess not expected");
			}
			
			public void onFailure(WlCommException e){
				Assert.assertTrue(e instanceof CommunicationException);
				Assert.assertEquals(ERROR_MESSAGE, e.getMessage());
				WebLabCommunicationTest.this.stepCounter++;
			}
		};
		comms.logout(sessionId, eac);
		Assert.assertEquals(3, this.stepCounter);
		
		requestBuilder.setNextReceivedMessage("");
		requestBuilder.setResponseToSend(this.generateBadResponse());
		eac = new IVoidCallback(){
			public void onSuccess(){
				Assert.fail("onSuccess not expected");
			}
			
			public void onFailure(WlCommException e){
				Assert.assertTrue(e instanceof ServerException);
				WebLabCommunicationTest.this.stepCounter++;
			}
		};
		comms.logout(sessionId, eac);
		Assert.assertEquals(4, this.stepCounter);
	}

	public void testPoll(){
		this.stepCounter = 0;
		final FakeWebLabSerializer weblabSerializer = new FakeWebLabSerializer();
		final FakeRequestBuilder requestBuilder = new FakeRequestBuilder();
		final FakeConfiguration configurationManager = new FakeConfiguration(new HashMap<String, String>());
				
		final WrappedWebLabCommunication comms = new WrappedWebLabCommunication(
					weblabSerializer,
					requestBuilder,
					configurationManager
				);
		final SessionID sessionId = new SessionID("whatever the session id");
		
		final String SERIALIZED_MESSAGE = "serialized get reservation status request";
		final String ERROR_MESSAGE = "whatever the error message";
		
		weblabSerializer.appendReturn(
					FakeWebLabSerializer.SERIALIZE_POLL_REQUEST, 
					SERIALIZED_MESSAGE
				);
		
		IVoidCallback eac = new IVoidCallback(){
			public void onSuccess() {
				WebLabCommunicationTest.this.stepCounter++;
			}

			public void onFailure(WlCommException e) {
				Assert.fail("onFailure not expected");
			}
		};
		
		requestBuilder.setNextReceivedMessage(SERIALIZED_MESSAGE);		
		comms.poll(sessionId, eac);
		Assert.assertEquals(1, this.stepCounter);
		
		requestBuilder.setNextToThrow(new RequestException(ERROR_MESSAGE));
		eac = new IVoidCallback(){
			public void onSuccess(){
				Assert.fail("onSuccess not expected");
			}
			
			public void onFailure(WlCommException e){
				Assert.assertTrue(e instanceof CommunicationException);
				Assert.assertEquals(ERROR_MESSAGE, e.getMessage());
				WebLabCommunicationTest.this.stepCounter++;
			}
		};
		comms.poll(sessionId, eac);
		Assert.assertEquals(2, this.stepCounter);
		
		requestBuilder.setNextToError(new Exception(ERROR_MESSAGE));
		eac = new IVoidCallback(){
			public void onSuccess(){
				Assert.fail("onSuccess not expected");
			}
			
			public void onFailure(WlCommException e){
				Assert.assertTrue(e instanceof CommunicationException);
				Assert.assertEquals(ERROR_MESSAGE, e.getMessage());
				WebLabCommunicationTest.this.stepCounter++;
			}
		};
		comms.poll(sessionId, eac);
		Assert.assertEquals(3, this.stepCounter);
		
		requestBuilder.setNextReceivedMessage("");
		requestBuilder.setResponseToSend(this.generateBadResponse());
		eac = new IVoidCallback(){
			public void onSuccess(){
				Assert.fail("onSuccess not expected");
			}
			
			public void onFailure(WlCommException e){
				Assert.assertTrue(e instanceof ServerException);
				WebLabCommunicationTest.this.stepCounter++;
			}
		};
		comms.poll(sessionId, eac);
		Assert.assertEquals(4, this.stepCounter);
	}

	public void testReserveExperiment(){
		this.stepCounter = 0;
		final FakeWebLabSerializer weblabSerializer = new FakeWebLabSerializer();
		final FakeRequestBuilder requestBuilder = new FakeRequestBuilder();
		final FakeConfiguration configurationManager = new FakeConfiguration(new HashMap<String, String>());
				
		final WrappedWebLabCommunication comms = new WrappedWebLabCommunication(
					weblabSerializer,
					requestBuilder,
					configurationManager
				);
		final SessionID sessionId = new SessionID();
		
		final String SERIALIZED_MESSAGE = "serialized get reservation status request";
		final String ERROR_MESSAGE = "whatever the error message";
		final ExperimentID experimentId = new ExperimentID(new Category("Category name"), "Experiment name");
		final ReservationStatus expectedReservation = new ConfirmedReservationStatus(100);
		
		weblabSerializer.appendReturn(
					FakeWebLabSerializer.PARSE_RESERVE_EXPERIMENT_RESPONSE, 
					expectedReservation
				);
		weblabSerializer.appendReturn(
					FakeWebLabSerializer.SERIALIZE_RESERVE_EXPERIMENT_REQUEST, 
					SERIALIZED_MESSAGE
				);
		
		IReservationCallback eac = new IReservationCallback(){
			public void onSuccess(ReservationStatus reservation) {
				Assert.assertEquals(expectedReservation, reservation);
				WebLabCommunicationTest.this.stepCounter++;
			}

			public void onFailure(WlCommException e) {
				Assert.fail("onFailure not expected");
			}
		};
		
		requestBuilder.setNextReceivedMessage(SERIALIZED_MESSAGE);		
		comms.reserveExperiment(sessionId, experimentId, eac);
		Assert.assertEquals(1, this.stepCounter);
		
		requestBuilder.setNextToThrow(new RequestException(ERROR_MESSAGE));
		eac = new IReservationCallback(){
			public void onSuccess(ReservationStatus reservation) {
				Assert.fail("onSuccess not expected");
			}
			
			public void onFailure(WlCommException e){
				Assert.assertTrue(e instanceof CommunicationException);
				Assert.assertEquals(ERROR_MESSAGE, e.getMessage());
				WebLabCommunicationTest.this.stepCounter++;
			}
		};
		comms.reserveExperiment(sessionId, experimentId, eac);
		Assert.assertEquals(2, this.stepCounter);
		
		requestBuilder.setNextToError(new Exception(ERROR_MESSAGE));
		eac = new IReservationCallback(){
			public void onSuccess(ReservationStatus reservation) {
				Assert.fail("onSuccess not expected");
			}
			
			public void onFailure(WlCommException e){
				Assert.assertTrue(e instanceof CommunicationException);
				Assert.assertEquals(ERROR_MESSAGE, e.getMessage());
				WebLabCommunicationTest.this.stepCounter++;
			}
		};
		comms.reserveExperiment(sessionId, experimentId, eac);
		Assert.assertEquals(3, this.stepCounter);
		
		requestBuilder.setNextReceivedMessage("");
		requestBuilder.setResponseToSend(this.generateBadResponse());
		eac = new IReservationCallback(){
			public void onSuccess(ReservationStatus reservation) {
				Assert.fail("onSuccess not expected");
			}
			
			public void onFailure(WlCommException e){
				Assert.assertTrue(e instanceof ServerException);
				WebLabCommunicationTest.this.stepCounter++;
			}
		};
		comms.reserveExperiment(sessionId, experimentId, eac);
		Assert.assertEquals(4, this.stepCounter);
	}
	
	public void testSendCommand(){
		this.stepCounter = 0;
		final FakeWebLabSerializer weblabSerializer = new FakeWebLabSerializer();
		final FakeRequestBuilder requestBuilder = new FakeRequestBuilder();
		final FakeConfiguration configurationManager = new FakeConfiguration(new HashMap<String, String>());
				
		final WrappedWebLabCommunication comms = new WrappedWebLabCommunication(
					weblabSerializer,
					requestBuilder,
					configurationManager
				);
		final SessionID sessionId = new SessionID("whatever the session id");
		final Command   command   = new SwitchCommand(5, true);
		
		final String SERIALIZED_MESSAGE = "serialized get reservation status request";
		final String ERROR_MESSAGE = "whatever the error message";
		
		weblabSerializer.appendReturn(
				FakeWebLabSerializer.SERIALIZE_SEND_COMMAND_REQUEST, 
				SERIALIZED_MESSAGE
			);
	
		weblabSerializer.appendReturn(
				FakeWebLabSerializer.PARSE_SEND_COMMAND_RESPONSE, 
				new ResponseCommand("whatever") // TODO 
			);
	
		IResponseCommandCallback eac = new IResponseCommandCallback(){
			public void onSuccess(ResponseCommand responseCommand) {
				//TODO
				WebLabCommunicationTest.this.stepCounter++;
			}

			public void onFailure(WlCommException e) {
				Assert.fail("onFailure not expected");
			}
		};
		
		requestBuilder.setNextReceivedMessage(SERIALIZED_MESSAGE);		
		comms.sendCommand(sessionId, command, eac);
		Assert.assertEquals(1, this.stepCounter);
		
		requestBuilder.setNextToThrow(new RequestException(ERROR_MESSAGE));
		eac = new IResponseCommandCallback(){
			public void onSuccess(ResponseCommand responseCommand){
				Assert.fail("onSuccess not expected");
			}
			
			public void onFailure(WlCommException e){
				Assert.assertTrue(e instanceof CommunicationException);
				Assert.assertEquals(ERROR_MESSAGE, e.getMessage());
				WebLabCommunicationTest.this.stepCounter++;
			}
		};
		comms.sendCommand(sessionId, command, eac);
		Assert.assertEquals(2, this.stepCounter);
		
		requestBuilder.setNextToError(new Exception(ERROR_MESSAGE));
		eac = new IResponseCommandCallback(){
			public void onSuccess(ResponseCommand responseCommand){
				Assert.fail("onSuccess not expected");
			}
			
			public void onFailure(WlCommException e){
				Assert.assertTrue(e instanceof CommunicationException);
				Assert.assertEquals(ERROR_MESSAGE, e.getMessage());
				WebLabCommunicationTest.this.stepCounter++;
			}
		};
		comms.sendCommand(sessionId, command, eac);
		Assert.assertEquals(3, this.stepCounter);

		requestBuilder.setNextReceivedMessage("");
		requestBuilder.setResponseToSend(this.generateBadResponse());
		eac = new IResponseCommandCallback(){
			public void onSuccess(ResponseCommand responseCommand){
				Assert.fail("onSuccess not expected");
			}
			
			public void onFailure(WlCommException e){
				Assert.assertTrue(e instanceof ServerException);
				WebLabCommunicationTest.this.stepCounter++;
			}
		};
		comms.sendCommand(sessionId, command, eac);
		Assert.assertEquals(4, this.stepCounter);
	}

	public void testFinishedExperiment(){
		this.stepCounter = 0;
		final FakeWebLabSerializer weblabSerializer = new FakeWebLabSerializer();
		final FakeRequestBuilder requestBuilder = new FakeRequestBuilder();
		final FakeConfiguration configurationManager = new FakeConfiguration(new HashMap<String, String>());
				
		final WrappedWebLabCommunication comms = new WrappedWebLabCommunication(
					weblabSerializer,
					requestBuilder,
					configurationManager
				);
		final SessionID sessionId = new SessionID("whatever the session id");
		
		final String SERIALIZED_MESSAGE = "serialized get reservation status request";
		final String ERROR_MESSAGE = "whatever the error message";
		
		weblabSerializer.appendReturn(
					FakeWebLabSerializer.SERIALIZE_FINISHED_EXPERIMENT_REQUEST, 
					SERIALIZED_MESSAGE
				);
		
		IVoidCallback eac = new IVoidCallback(){
			public void onSuccess() {
				WebLabCommunicationTest.this.stepCounter++;
			}

			public void onFailure(WlCommException e) {
				Assert.fail("onFailure not expected");
			}
		};
		
		requestBuilder.setNextReceivedMessage(SERIALIZED_MESSAGE);		
		comms.finishedExperiment(sessionId, eac);
		Assert.assertEquals(1, this.stepCounter);
		
		requestBuilder.setNextToThrow(new RequestException(ERROR_MESSAGE));
		eac = new IVoidCallback(){
			public void onSuccess(){
				Assert.fail("onSuccess not expected");
			}
			
			public void onFailure(WlCommException e){
				Assert.assertTrue(e instanceof CommunicationException);
				Assert.assertEquals(ERROR_MESSAGE, e.getMessage());
				WebLabCommunicationTest.this.stepCounter++;
			}
		};
		comms.finishedExperiment(sessionId, eac);
		Assert.assertEquals(2, this.stepCounter);
		
		requestBuilder.setNextToError(new Exception(ERROR_MESSAGE));
		eac = new IVoidCallback(){
			public void onSuccess(){
				Assert.fail("onSuccess not expected");
			}
			
			public void onFailure(WlCommException e){
				Assert.assertTrue(e instanceof CommunicationException);
				Assert.assertEquals(ERROR_MESSAGE, e.getMessage());
				WebLabCommunicationTest.this.stepCounter++;
			}
		};
		comms.finishedExperiment(sessionId, eac);
		Assert.assertEquals(3, this.stepCounter);
		
		requestBuilder.setNextReceivedMessage("");
		requestBuilder.setResponseToSend(this.generateBadResponse());
		eac = new IVoidCallback(){
			public void onSuccess(){
				Assert.fail("onSuccess not expected");
			}
			
			public void onFailure(WlCommException e){
				Assert.assertTrue(e instanceof ServerException);
				WebLabCommunicationTest.this.stepCounter++;
			}
		};
		comms.finishedExperiment(sessionId, eac);
		Assert.assertEquals(4, this.stepCounter);
	}
	
	private class FakeFormPanel extends FormPanel{
		
		public FakeFormPanel(){
			
		}
		
		private String currentUrl = null;
		
		@Override
		public void setAction(String url) {
			if(this.currentUrl != null)
				throw new IllegalStateException("FakeFormPanel already had an currentUrl");
			this.currentUrl = url;
		}
		
		@Override
		public String getAction(){
			return this.currentUrl;
		}

		private String currentEncodingType; 
		
		@Override
		public void setEncoding(String encodingType) {
			if(this.currentEncodingType != null)
				throw new IllegalStateException("FakeFormPanel already had an currentEncodingType");
			this.currentEncodingType = encodingType;
		}
		
		@Override
		public String getEncoding(){
			return this.currentEncodingType;
		}

		private String currentMethod;
		
		@Override
		public void setMethod(String method) {
			if(this.currentMethod != null)
				throw new IllegalStateException("FakeFormPanel already had an currentMethod");
			this.currentMethod = method;
		}
		
		@Override
		public String getMethod(){
			return this.currentMethod;
		}
		
		private boolean submitted = false;

		@Override
		public void submit() {
			if(this.submitted)
				throw new IllegalStateException("FakeFormPanel already had an submitted");
			this.submitted = true;
		}
	}
	
	private class FakeFileUpload extends FileUpload{
		private String name;
		@Override
		public void setName(String name) {
			if(this.name != null)
				throw new IllegalStateException("FakeFileUpload already had a name");
			this.name = name;
		}
		@Override
		public String getName(){
			return this.name;
		}
	}
	
	private ResponseCommand sentFileResponse;
	
	public void testSendFile(){
		this.stepCounter = 0;
		final FakeWebLabSerializer weblabSerializer = new FakeWebLabSerializer();
		final FakeRequestBuilder requestBuilder = new FakeRequestBuilder();
		final FakeConfiguration configurationManager = new FakeConfiguration(new HashMap<String, String>());
				
		final WrappedWebLabCommunication comms = new WrappedWebLabCommunication(
					weblabSerializer,
					requestBuilder,
					configurationManager
				);
		final SessionID sessionId = new SessionID("whatever the session id");
		final FakeFormPanel fakeFormPanel = new FakeFormPanel();
		final FakeFileUpload fakeFileUpload = new FakeFileUpload();
		
		final UploadStructure us = new UploadStructure(){
			@Override
			public FormPanel getFormPanel(){
				return fakeFormPanel;
			}
			
			@Override
			public FileUpload getFileUpload(){
				return fakeFileUpload;
			}
		};
		
		final IResponseCommandCallback callback = new IResponseCommandCallback(){
			public void onSuccess(ResponseCommand command){
				WebLabCommunicationTest.this.stepCounter++;
				WebLabCommunicationTest.this.sentFileResponse = command;
			}

			public void onFailure(WlCommException e){
			}
		};
		
		Assert.assertEquals(0, this.stepCounter);
		comms.sendFile(sessionId, us, callback);

		Assert.assertNotNull(fakeFormPanel.getAction());
		Assert.assertEquals(FormPanel.ENCODING_MULTIPART, fakeFormPanel.getEncoding());
		Assert.assertEquals(FormPanel.METHOD_POST,        fakeFormPanel.getMethod());
		Assert.assertEquals(WlLabCommunication.FILE_SENT_ATTR, fakeFileUpload.getName());
		
		Assert.assertEquals(0, this.stepCounter);
		
		final String messageItself = "my message";
		final String sentMessage = "SUCCESS@" + messageItself;
		final String bundledMessage = "<body>" + sentMessage + "</body>"; 
		final SubmitCompleteEvent sce = new FakeSubmitCompleteEvent(bundledMessage);
		weblabSerializer.appendReturn(FakeWebLabSerializer.PARSE_SEND_FILE_RESPONSE, new ResponseCommand(messageItself));
		fakeFormPanel.fireEvent(sce);
		
		Assert.assertEquals(1, this.stepCounter);
		Assert.assertNotNull(this.sentFileResponse);
		Assert.assertEquals(messageItself, this.sentFileResponse.getCommandString());
	}
	
	private static class FakeSubmitCompleteEvent extends SubmitCompleteEvent{
	    public FakeSubmitCompleteEvent(String resultHtml) {
		super(resultHtml);
	    }
	}

	@Override
	public String getModuleName() {
		return "es.deusto.weblab.WebLabClient";
	}
}
