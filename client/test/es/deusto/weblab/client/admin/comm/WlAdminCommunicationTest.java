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

package es.deusto.weblab.client.admin.comm;

import java.util.ArrayList;
import java.util.Date;
import java.util.HashMap;

import junit.framework.Assert;

import com.google.gwt.http.client.RequestException;

import es.deusto.weblab.client.admin.comm.callbacks.IExperimentsCallback;
import es.deusto.weblab.client.admin.comm.callbacks.IGroupsCallback;
import es.deusto.weblab.client.comm.FakeRequestBuilder;
import es.deusto.weblab.client.comm.WlCommonCommunicationTest;
import es.deusto.weblab.client.comm.exceptions.CommunicationException;
import es.deusto.weblab.client.comm.exceptions.ServerException;
import es.deusto.weblab.client.comm.exceptions.WlCommException;
import es.deusto.weblab.client.configuration.FakeConfiguration;
import es.deusto.weblab.client.dto.SessionID;
import es.deusto.weblab.client.dto.experiments.Category;
import es.deusto.weblab.client.dto.experiments.Experiment;
import es.deusto.weblab.client.dto.users.Group;


public class WlAdminCommunicationTest extends WlCommonCommunicationTest {

	public void testGetGroups(){
		
		this.stepCounter = 0;
		final FakeWlAdminSerializer weblabSerializer = new FakeWlAdminSerializer();
		final FakeRequestBuilder requestBuilder = new FakeRequestBuilder();
		final FakeConfiguration configurationManager = new FakeConfiguration(new HashMap<String,String>());
				
		final WrappedWlAdminCommunication comms = new WrappedWlAdminCommunication(
					weblabSerializer,
					requestBuilder,
					configurationManager
				);
		final SessionID sessionId = new SessionID();
		
		final String SERIALIZED_MESSAGE = "serialized get reservation status request";
		final String ERROR_MESSAGE = "whatever the error message";
		
		final ArrayList<Group> expectedGroups = new ArrayList<Group>();
		expectedGroups.add(new Group("group"));
		
		weblabSerializer.appendReturn(
					FakeWlAdminSerializer.PARSE_GET_GROUPS_RESPONSE, 
					expectedGroups
				);
		weblabSerializer.appendReturn(
				FakeWlAdminSerializer.SERIALIZE_GET_GROUPS_REQUEST, 
					SERIALIZED_MESSAGE
				);
		
		IGroupsCallback callback = new IGroupsCallback(){
			@Override
			public void onSuccess(ArrayList<Group> groups) {
				Assert.assertEquals(expectedGroups.size(), groups.size());
				Assert.assertEquals(expectedGroups.get(0), groups.get(0));
				WlAdminCommunicationTest.this.stepCounter++;
			}

			@Override
			public void onFailure(WlCommException e) {
				Assert.fail("onFailure not expected");
			}
		};
		
		requestBuilder.setNextReceivedMessage(SERIALIZED_MESSAGE);		
		comms.getGroups(sessionId, callback);
		Assert.assertEquals(1, this.stepCounter);
		
		requestBuilder.setNextToThrow(new RequestException(ERROR_MESSAGE));
		callback = new IGroupsCallback(){
			@Override
			public void onSuccess(ArrayList<Group> groups) {
				Assert.fail("onSuccess not expected");
			}

			@Override
			public void onFailure(WlCommException e){
				Assert.assertTrue(e instanceof CommunicationException);
				Assert.assertEquals(ERROR_MESSAGE, e.getMessage());
				WlAdminCommunicationTest.this.stepCounter++;
			}
		};
		comms.getGroups(sessionId, callback);
		Assert.assertEquals(2, this.stepCounter);
		
		requestBuilder.setNextToError(new Exception(ERROR_MESSAGE));
		callback = new IGroupsCallback(){
			@Override
			public void onSuccess(ArrayList<Group> groups) {
				Assert.fail("onSuccess not expected");
			}

			@Override
			public void onFailure(WlCommException e){
				Assert.assertTrue(e instanceof CommunicationException);
				Assert.assertEquals(ERROR_MESSAGE, e.getMessage());
				WlAdminCommunicationTest.this.stepCounter++;
			}
		};
		comms.getGroups(sessionId, callback);
		Assert.assertEquals(3, this.stepCounter);
		
		requestBuilder.setNextReceivedMessage("");
		requestBuilder.setResponseToSend(this.generateBadResponse());
		callback = new IGroupsCallback(){
			@Override
			public void onSuccess(ArrayList<Group> groups) {
				Assert.fail("onSuccess not expected");
			}

			@Override
			public void onFailure(WlCommException e){
				Assert.assertTrue(e instanceof ServerException);
				WlAdminCommunicationTest.this.stepCounter++;
			}
		};
		comms.getGroups(sessionId, callback);
		Assert.assertEquals(4, this.stepCounter);
	}	

	public void testGetExperiments() {
		
		this.stepCounter = 0;
		final FakeWlAdminSerializer weblabSerializer = new FakeWlAdminSerializer();
		final FakeRequestBuilder requestBuilder = new FakeRequestBuilder();
		final FakeConfiguration configurationManager = new FakeConfiguration(new HashMap<String,String>());
				
		final WrappedWlAdminCommunication comms = new WrappedWlAdminCommunication(
					weblabSerializer,
					requestBuilder,
					configurationManager
				);
		final SessionID sessionId = new SessionID();
		
		final String SERIALIZED_MESSAGE = "serialized get reservation status request";
		final String ERROR_MESSAGE = "whatever the error message";
		
		final ArrayList<Experiment> expectedExperiments = new ArrayList<Experiment>();
		expectedExperiments.add(new Experiment("ud-fpga", new Category("FPGA experiments"), new Date(), new Date()));
		
		weblabSerializer.appendReturn(
					FakeWlAdminSerializer.PARSE_GET_EXPERIMENTS_RESPONSE, 
					expectedExperiments
				);
		weblabSerializer.appendReturn(
					FakeWlAdminSerializer.SERIALIZE_GET_EXPERIMENTS_REQUEST, 
					SERIALIZED_MESSAGE
				);
		
		IExperimentsCallback callback = new IExperimentsCallback(){
			@Override
			public void onSuccess(ArrayList<Experiment> experiments) {
				Assert.assertEquals(expectedExperiments.size(), experiments.size());
				Assert.assertEquals(expectedExperiments.get(0), experiments.get(0));
				WlAdminCommunicationTest.this.stepCounter++;
			}

			@Override
			public void onFailure(WlCommException e) {
				Assert.fail("onFailure not expected");
			}
		};
		
		requestBuilder.setNextReceivedMessage(SERIALIZED_MESSAGE);		
		comms.getExperiments(sessionId, callback);
		Assert.assertEquals(1, this.stepCounter);
		
		requestBuilder.setNextToThrow(new RequestException(ERROR_MESSAGE));
		callback = new IExperimentsCallback(){
			@Override
			public void onSuccess(ArrayList<Experiment> experiments) {
				Assert.fail("onSuccess not expected");
			}

			@Override
			public void onFailure(WlCommException e){
				Assert.assertTrue(e instanceof CommunicationException);
				Assert.assertEquals(ERROR_MESSAGE, e.getMessage());
				WlAdminCommunicationTest.this.stepCounter++;
			}
		};
		comms.getExperiments(sessionId, callback);
		Assert.assertEquals(2, this.stepCounter);
		
		requestBuilder.setNextToError(new Exception(ERROR_MESSAGE));
		callback = new IExperimentsCallback(){
			@Override
			public void onSuccess(ArrayList<Experiment> experiments) {
				Assert.fail("onSuccess not expected");
			}

			@Override
			public void onFailure(WlCommException e){
				Assert.assertTrue(e instanceof CommunicationException);
				Assert.assertEquals(ERROR_MESSAGE, e.getMessage());
				WlAdminCommunicationTest.this.stepCounter++;
			}
		};
		comms.getExperiments(sessionId, callback);
		Assert.assertEquals(3, this.stepCounter);
		
		requestBuilder.setNextReceivedMessage("");
		requestBuilder.setResponseToSend(this.generateBadResponse());
		callback = new IExperimentsCallback(){
			@Override
			public void onSuccess(ArrayList<Experiment> experiments) {
				Assert.fail("onSuccess not expected");
			}

			@Override
			public void onFailure(WlCommException e){
				Assert.assertTrue(e instanceof ServerException);
				WlAdminCommunicationTest.this.stepCounter++;
			}
		};
		comms.getExperiments(sessionId, callback);
		Assert.assertEquals(4, this.stepCounter);
	}	
	
	@Override
	public String getModuleName() {
		return "es.deusto.weblab.WebLabClient";
	}

}
