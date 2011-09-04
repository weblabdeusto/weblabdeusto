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
* Author: Jaime Irurzun <jaime.irurzun@gmail.com>
*
*/

package es.deusto.weblab.client.admin.comm;

import java.util.HashMap;

import junit.framework.Assert;

import com.google.gwt.http.client.RequestException;

import es.deusto.weblab.client.admin.comm.callbacks.IPermissionsCallback;
import es.deusto.weblab.client.comm.FakeWebLabRequestBuilder;
import es.deusto.weblab.client.comm.CommonCommunicationTest;
import es.deusto.weblab.client.comm.exceptions.CommunicationException;
import es.deusto.weblab.client.comm.exceptions.ServerException;
import es.deusto.weblab.client.comm.exceptions.CommException;
import es.deusto.weblab.client.configuration.FakeConfiguration;
import es.deusto.weblab.client.dto.SessionID;
import es.deusto.weblab.client.dto.users.Permission;
import es.deusto.weblab.client.dto.users.PermissionParameter;

public class AdminCommunicationTest extends CommonCommunicationTest {
	   
	public void testGetUserPermissions(){
		this.stepCounter = 0;
		final FakeAdminSerializer weblabSerializer = new FakeAdminSerializer();
		final FakeWebLabRequestBuilder requestBuilder = new FakeWebLabRequestBuilder();
		final FakeConfiguration configurationManager = new FakeConfiguration(new HashMap<String,String>());
				
		final WrappedAdminCommunication comms = new WrappedAdminCommunication(
					weblabSerializer,
					requestBuilder,
					configurationManager
				);
		final SessionID sessionId = new SessionID();
		
		final String SERIALIZED_MESSAGE = "serialized get_user_information request";
		final String ERROR_MESSAGE = "whatever the error message";
		final Permission [] expected_permissions = new Permission[1];
		final PermissionParameter[] expected_parameters = new PermissionParameter[1];
		expected_parameters[0] = new PermissionParameter("full_privileges", "bool", "1");
		expected_permissions[0] = new Permission("admin_panel_access", expected_parameters);
		
		weblabSerializer.appendReturn(
					FakeAdminSerializer.PARSE_GET_USER_PERMISSIONS_RESPONSE, 
					expected_permissions
				);
		weblabSerializer.appendReturn(
				FakeAdminSerializer.SERIALIZE_GET_USER_PERMISSIONS_REQUEST, 
					SERIALIZED_MESSAGE
				);
		
		IPermissionsCallback pc = new IPermissionsCallback(){
			@Override
			public void onSuccess(Permission [] permissions) {
				Assert.assertEquals(expected_permissions.length, permissions.length);
				Assert.assertEquals(expected_permissions[0], permissions[0]);
				AdminCommunicationTest.this.stepCounter++;
			}

			@Override
			public void onFailure(CommException e) {
				Assert.fail("onFailure not expected");
			}
		};
		
		requestBuilder.setNextReceivedMessage(SERIALIZED_MESSAGE);		
		comms.getUserPermissions(sessionId, pc);
		Assert.assertEquals(1, this.stepCounter);
		
		requestBuilder.setNextToThrow(new RequestException(ERROR_MESSAGE));
		pc = new IPermissionsCallback(){
			@Override
			public void onSuccess(Permission [] permissions){
				Assert.fail("onSuccess not expected");
			}
			
			@Override
			public void onFailure(CommException e){
				Assert.assertTrue(e instanceof CommunicationException);
				Assert.assertEquals(ERROR_MESSAGE, e.getMessage());
				AdminCommunicationTest.this.stepCounter++;
			}
		};
		comms.getUserPermissions(sessionId, pc);
		Assert.assertEquals(2, this.stepCounter);
		
		requestBuilder.setNextToError(new Exception(ERROR_MESSAGE));
		pc = new IPermissionsCallback(){
			@Override
			public void onSuccess(Permission [] permissions){
				Assert.fail("onSuccess not expected");
			}
			
			@Override
			public void onFailure(CommException e){
				Assert.assertTrue(e instanceof CommunicationException);
				Assert.assertEquals(ERROR_MESSAGE, e.getMessage());
				AdminCommunicationTest.this.stepCounter++;
			}
		};
		comms.getUserPermissions(sessionId, pc);
		Assert.assertEquals(3, this.stepCounter);
		
		requestBuilder.setNextReceivedMessage("");
		requestBuilder.setResponseToSend(this.generateBadResponse());
		pc = new IPermissionsCallback(){
			@Override
			public void onSuccess(Permission [] permissions){
				Assert.fail("onSuccess not expected");
			}
			
			@Override
			public void onFailure(CommException e){
				Assert.assertTrue(e instanceof ServerException);
				AdminCommunicationTest.this.stepCounter++;
			}
		};
		comms.getUserPermissions(sessionId, pc);
		Assert.assertEquals(4, this.stepCounter);
	}
	
	@Override
	public String getModuleName() {
		return "es.deusto.weblab.WebLabClientAdmin";
	}
}
