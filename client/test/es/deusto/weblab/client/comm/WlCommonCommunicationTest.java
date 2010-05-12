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
* Author: FILLME
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
import es.deusto.weblab.client.comm.exceptions.CommunicationException;
import es.deusto.weblab.client.comm.exceptions.ServerException;
import es.deusto.weblab.client.comm.exceptions.WlCommException;
import es.deusto.weblab.client.configuration.FakeConfiguration;
import es.deusto.weblab.client.dto.SessionID;

public class WlCommonCommunicationTest extends GWTTestCase {
	
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
		final FakeWlCommonSerializer weblabSerializer = new FakeWlCommonSerializer();
		final FakeRequestBuilder requestBuilder = new FakeRequestBuilder();
		final FakeConfiguration configurationManager = new FakeConfiguration(new HashMap<String,String>());
				
		final WrappedWlCommonCommunication comms = new WrappedWlCommonCommunication(
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
					FakeWlCommonSerializer.PARSE_LOGIN_RESPONSE, 
					expectedSessionId
				);
		weblabSerializer.appendReturn(
				FakeWlCommonSerializer.SERIALIZE_LOGIN_REQUEST, 
					SERIALIZED_MESSAGE
				);
		
		ISessionIdCallback eac = new ISessionIdCallback(){
			public void onSuccess(SessionID sessionId) {
				Assert.assertEquals(expectedSessionId, sessionId);
				WlCommonCommunicationTest.this.stepCounter++;
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
				WlCommonCommunicationTest.this.stepCounter++;
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
				WlCommonCommunicationTest.this.stepCounter++;
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
				WlCommonCommunicationTest.this.stepCounter++;
			}
		};
		comms.login(USERNAME, PASSWORD, eac);
		Assert.assertEquals(4, this.stepCounter);
	}

	@Override
	public String getModuleName() {
		return "es.deusto.weblab.WebLabClient";
	}
	
}
