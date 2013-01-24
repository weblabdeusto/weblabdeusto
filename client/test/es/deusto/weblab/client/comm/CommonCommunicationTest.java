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
*         Jaime Irurzun <jaime.irurzun@gmail.com>
*
*/

package es.deusto.weblab.client.comm;

import java.util.HashMap;

import junit.framework.Assert;

import com.google.gwt.http.client.Header;
import com.google.gwt.http.client.RequestException;
import com.google.gwt.http.client.Response;
import com.google.gwt.junit.client.GWTTestCase;

import es.deusto.weblab.client.comm.callbacks.ISessionIdCallback;
import es.deusto.weblab.client.comm.callbacks.IUserInformationCallback;
import es.deusto.weblab.client.comm.callbacks.IVoidCallback;
import es.deusto.weblab.client.comm.exceptions.CommunicationException;
import es.deusto.weblab.client.comm.exceptions.ServerException;
import es.deusto.weblab.client.comm.exceptions.CommException;
import es.deusto.weblab.client.configuration.FakeConfiguration;
import es.deusto.weblab.client.dto.SessionID;
import es.deusto.weblab.client.dto.users.Role;
import es.deusto.weblab.client.dto.users.User;

public class CommonCommunicationTest extends GWTTestCase {
	
	protected int stepCounter;
	
	protected Response generateBadResponse(){
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

	public void testLogin(){
		this.stepCounter = 0;
		final FakeCommonSerializer weblabSerializer = new FakeCommonSerializer();
		final FakeWebLabRequestBuilder requestBuilder = new FakeWebLabRequestBuilder();
		final FakeConfiguration configurationManager = new FakeConfiguration(new HashMap<String,String>());
				
		final WrappedCommonCommunication comms = new WrappedCommonCommunication(
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
					FakeCommonSerializer.PARSE_LOGIN_RESPONSE, 
					expectedSessionId
				);
		weblabSerializer.appendReturn(
				FakeCommonSerializer.SERIALIZE_LOGIN_REQUEST, 
					SERIALIZED_MESSAGE
				);
		
		ISessionIdCallback eac = new ISessionIdCallback(){
			@Override
			public void onSuccess(SessionID sessionId) {
				Assert.assertEquals(expectedSessionId, sessionId);
				CommonCommunicationTest.this.stepCounter++;
			}

			@Override
			public void onFailure(CommException e) {
				Assert.fail("onFailure not expected");
			}
		};
		
		requestBuilder.setNextReceivedMessage(SERIALIZED_MESSAGE);		
		comms.login(USERNAME, PASSWORD, eac);
		Assert.assertEquals(1, this.stepCounter);
		
		requestBuilder.setNextToThrow(new RequestException(ERROR_MESSAGE));
		eac = new ISessionIdCallback(){
			@Override
			public void onSuccess(SessionID sessionId){
				Assert.fail("onSuccess not expected");
			}
			
			@Override
			public void onFailure(CommException e){
				Assert.assertTrue(e instanceof CommunicationException);
				Assert.assertEquals(ERROR_MESSAGE, e.getMessage());
				CommonCommunicationTest.this.stepCounter++;
			}
		};
		comms.login(USERNAME, PASSWORD, eac);
		Assert.assertEquals(2, this.stepCounter);
		
		requestBuilder.setNextToError(new Exception(ERROR_MESSAGE));
		eac = new ISessionIdCallback(){
			@Override
			public void onSuccess(SessionID sessionId){
				Assert.fail("onSuccess not expected");
			}
			
			@Override
			public void onFailure(CommException e){
				Assert.assertTrue(e instanceof CommunicationException);
				Assert.assertEquals(ERROR_MESSAGE, e.getMessage());
				CommonCommunicationTest.this.stepCounter++;
			}
		};
		comms.login(USERNAME, PASSWORD, eac);
		Assert.assertEquals(3, this.stepCounter);
		
		requestBuilder.setNextReceivedMessage("");
		requestBuilder.setResponseToSend(this.generateBadResponse());
		eac = new ISessionIdCallback(){
			@Override
			public void onSuccess(SessionID sessionId){
				Assert.fail("onSuccess not expected");
			}
			
			@Override
			public void onFailure(CommException e){
				Assert.assertTrue(e instanceof ServerException);
				CommonCommunicationTest.this.stepCounter++;
			}
		};
		comms.login(USERNAME, PASSWORD, eac);
		Assert.assertEquals(4, this.stepCounter);
	}
		
	public void testLogout(){
		this.stepCounter = 0;
		final FakeCommonSerializer weblabSerializer = new FakeCommonSerializer();
		final FakeWebLabRequestBuilder requestBuilder = new FakeWebLabRequestBuilder();
		final FakeConfiguration configurationManager = new FakeConfiguration(new HashMap<String, String>());
				
		final WrappedCommonCommunication comms = new WrappedCommonCommunication(
					weblabSerializer,
					requestBuilder,
					configurationManager
				);
		final SessionID sessionId = new SessionID("whatever the session id");
		
		final String SERIALIZED_MESSAGE = "serialized get reservation status request";
		final String ERROR_MESSAGE = "whatever the error message";
		
		weblabSerializer.appendReturn(
					FakeCommonSerializer.SERIALIZE_LOGOUT_REQUEST, 
					SERIALIZED_MESSAGE
				);
		
		IVoidCallback eac = new IVoidCallback(){
			@Override
			public void onSuccess() {
				CommonCommunicationTest.this.stepCounter++;
			}

			@Override
			public void onFailure(CommException e) {
				Assert.fail("onFailure not expected");
			}
		};
		
		requestBuilder.setNextReceivedMessage(SERIALIZED_MESSAGE);		
		comms.logout(sessionId, eac);
		Assert.assertEquals(1, this.stepCounter);
		
		requestBuilder.setNextToThrow(new RequestException(ERROR_MESSAGE));
		eac = new IVoidCallback(){
			@Override
			public void onSuccess(){
				Assert.fail("onSuccess not expected");
			}
			
			@Override
			public void onFailure(CommException e){
				Assert.assertTrue(e instanceof CommunicationException);
				Assert.assertEquals(ERROR_MESSAGE, e.getMessage());
				CommonCommunicationTest.this.stepCounter++;
			}
		};
		comms.logout(sessionId, eac);
		Assert.assertEquals(2, this.stepCounter);
		
		requestBuilder.setNextToError(new Exception(ERROR_MESSAGE));
		eac = new IVoidCallback(){
			@Override
			public void onSuccess(){
				Assert.fail("onSuccess not expected");
			}
			
			@Override
			public void onFailure(CommException e){
				Assert.assertTrue(e instanceof CommunicationException);
				Assert.assertEquals(ERROR_MESSAGE, e.getMessage());
				CommonCommunicationTest.this.stepCounter++;
			}
		};
		comms.logout(sessionId, eac);
		Assert.assertEquals(3, this.stepCounter);
		
		requestBuilder.setNextReceivedMessage("");
		requestBuilder.setResponseToSend(this.generateBadResponse());
		eac = new IVoidCallback(){
			@Override
			public void onSuccess(){
				Assert.fail("onSuccess not expected");
			}
			
			@Override
			public void onFailure(CommException e){
				Assert.assertTrue(e instanceof ServerException);
				CommonCommunicationTest.this.stepCounter++;
			}
		};
		comms.logout(sessionId, eac);
		Assert.assertEquals(4, this.stepCounter);
	}	

	@Override
	public String getModuleName() {
		return "es.deusto.weblab.WebLabClient";
	}

	public void testGetUserInformation(){
		this.stepCounter = 0;
		final FakeCommonSerializer weblabSerializer = new FakeCommonSerializer();
		final FakeWebLabRequestBuilder requestBuilder = new FakeWebLabRequestBuilder();
		final FakeConfiguration configurationManager = new FakeConfiguration(new HashMap<String,String>());
				
		final WrappedCommonCommunication comms = new WrappedCommonCommunication(
					weblabSerializer,
					requestBuilder,
					configurationManager
				);
		final SessionID sessionId = new SessionID("my_session_id");
		
		final String SERIALIZED_MESSAGE = "serialized get reservation status request";
		final String ERROR_MESSAGE = "whatever the error message";
		final User user = new User("porduna", "Pablo Orduña", "porduna@tecnologico.deusto.es", new Role("student"), "");
		
		weblabSerializer.appendReturn(
					FakeCommonSerializer.PARSE_GET_USER_INFORMATION_RESPONSE, 
					user
				);
		weblabSerializer.appendReturn(
				FakeCommonSerializer.SERIALIZE_GET_USER_INFORMATION_REQUEST, 
					SERIALIZED_MESSAGE
				);
		
		IUserInformationCallback uic = new IUserInformationCallback(){
			@Override
			public void onSuccess(User userInformation) {
				Assert.assertEquals(user.getEmail(),    userInformation.getEmail());
				Assert.assertEquals(user.getFullName(), userInformation.getFullName());
				Assert.assertEquals(user.getLogin(),    userInformation.getLogin());
				CommonCommunicationTest.this.stepCounter++;
			}

			@Override
			public void onFailure(CommException e) {
				Assert.fail("onFailure not expected");
			}
		};
		
		requestBuilder.setNextReceivedMessage(SERIALIZED_MESSAGE);		
		comms.getUserInformation(sessionId, uic);
		Assert.assertEquals(1, this.stepCounter);
		
		requestBuilder.setNextToThrow(new RequestException(ERROR_MESSAGE));
		uic = new IUserInformationCallback(){
			@Override
			public void onSuccess(User userInformation){
				Assert.fail("onSuccess not expected");
			}
			
			@Override
			public void onFailure(CommException e){
				Assert.assertTrue(e instanceof CommunicationException);
				Assert.assertEquals(ERROR_MESSAGE, e.getMessage());
				CommonCommunicationTest.this.stepCounter++;
			}
		};
		comms.getUserInformation(sessionId, uic);
		Assert.assertEquals(2, this.stepCounter);
		
		requestBuilder.setNextToError(new Exception(ERROR_MESSAGE));
		uic = new IUserInformationCallback(){
			@Override
			public void onSuccess(User userInformation){
				Assert.fail("onSuccess not expected");
			}
			
			@Override
			public void onFailure(CommException e){
				Assert.assertTrue(e instanceof CommunicationException);
				Assert.assertEquals(ERROR_MESSAGE, e.getMessage());
				CommonCommunicationTest.this.stepCounter++;
			}
		};
		comms.getUserInformation(sessionId, uic);
		Assert.assertEquals(3, this.stepCounter);
		
		requestBuilder.setNextReceivedMessage("");
		requestBuilder.setResponseToSend(this.generateBadResponse());
		uic = new IUserInformationCallback(){
			@Override
			public void onSuccess(User userInformation){
				Assert.fail("onSuccess not expected");
			}
			
			@Override
			public void onFailure(CommException e){
				Assert.assertTrue(e instanceof ServerException);
				CommonCommunicationTest.this.stepCounter++;
			}
		};
		comms.getUserInformation(sessionId, uic);
		Assert.assertEquals(4, this.stepCounter);
	}
	
}
