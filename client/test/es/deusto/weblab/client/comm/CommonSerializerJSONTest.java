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

import junit.framework.Assert;

import com.google.gwt.junit.client.GWTTestCase;

import es.deusto.weblab.client.comm.exceptions.SerializationException;
import es.deusto.weblab.client.comm.exceptions.WebLabServerException;
import es.deusto.weblab.client.comm.exceptions.core.SessionNotFoundException;
import es.deusto.weblab.client.comm.exceptions.core.UserProcessingException;
import es.deusto.weblab.client.comm.exceptions.login.InvalidCredentialsException;
import es.deusto.weblab.client.comm.exceptions.login.LoginException;
import es.deusto.weblab.client.dto.SessionID;
import es.deusto.weblab.client.dto.users.User;

public class CommonSerializerJSONTest extends GWTTestCase {
	
	public void testParseGetUserInformationResponse() throws Exception{
		final ICommonSerializer weblabSerializer = new CommonSerializerJSON();
		final User user = weblabSerializer.parseGetUserInformationResponse(
				"{\"result\": {\"login\": \"porduna\", \"email\": \"porduna@tecnologico.deusto.es\", \"full_name\": \"Pablo Orduna\", \"role\": {\"name\": \"student\"}}, \"is_exception\": false, \"admin_url\" : \"\"}"
		);
		Assert.assertEquals("porduna", user.getLogin());
		Assert.assertEquals("Pablo Orduna", user.getFullName());
		Assert.assertEquals("porduna@tecnologico.deusto.es", user.getEmail());
		Assert.assertEquals("student", user.getRole().getName());
		Assert.assertEquals("", user.getAdminUrl());
	}

	public void testParseGetUserInformationResponse_Exceptions() throws Exception{
		final ICommonSerializer weblabSerializer = new CommonSerializerJSON();
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
		final ICommonSerializer weblabSerializer = new CommonSerializerJSON();
		final SessionID sessionId = weblabSerializer.parseLoginResponse(
				"{\"result\": {\"id\": \"whatever\"}, \"is_exception\":false}"
			);
		Assert.assertEquals("whatever",sessionId.getRealId());
	}

	public void testParseLoginResponse_Faults() throws Exception{
		final ICommonSerializer weblabSerializer = new CommonSerializerJSON();
		
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
		} catch (final WebLabServerException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
		try {
			weblabSerializer.parseLoginResponse(
				whole_message.replaceFirst("THE_FAULT_CODE", "JSON:Server.Voodoo")
			);
			Assert.fail("Exception expected");
		} catch (final WebLabServerException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
		try {
			weblabSerializer.parseLoginResponse(
				whole_message.replaceFirst("THE_FAULT_CODE", "JSON:Server.Python")
			);
			Assert.fail("Exception expected");
		} catch (final WebLabServerException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
	}

	public void testParseLoginResponse_Exceptions() throws Exception{
		final ICommonSerializer weblabSerializer = new CommonSerializerJSON();
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
		final ICommonSerializer weblabSerializer = new CommonSerializerJSON();
		weblabSerializer.parseLogoutResponse(
				"{\"result\": {}, \"is_exception\": false}"
			);
	}

	public void testParseLogoutResponse_Faults() throws Exception{
		final ICommonSerializer weblabSerializer = new CommonSerializerJSON();
		
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
		} catch (final WebLabServerException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
		try {
			weblabSerializer.parseLogoutResponse(
				whole_message.replaceFirst("THE_FAULT_CODE", "JSON:Server.Voodoo")
			);
			Assert.fail("Exception expected");
		} catch (final WebLabServerException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
		try {
			weblabSerializer.parseLogoutResponse(
				whole_message.replaceFirst("THE_FAULT_CODE", "JSON:Server.Python")
			);
			Assert.fail("Exception expected");
		} catch (final WebLabServerException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
	}

	public void testParseLogoutResponse_Exceptions() throws Exception{
		final ICommonSerializer weblabSerializer = new CommonSerializerJSON();
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
	
	public void testSerializeGetUserInformationRequest() throws Exception{
		final ICommonSerializer weblabSerializer = new CommonSerializerJSON();
		final String MESSAGE = "whatever the session id real id";
		
		final SessionID sessionId = new SessionID(MESSAGE);
		final String serializedMessage = weblabSerializer.serializeGetUserInformationRequest(sessionId);
		
		Assert.assertEquals(
				"{\"params\":{\"session_id\":{\"id\":\"" + MESSAGE + "\"}}, \"method\":\"get_user_information\"}",
				serializedMessage
			);
	}
	
	public void testSerializeLoginRequest() throws Exception{
		final ICommonSerializer weblabSerializer = new CommonSerializerJSON();
		
		final String USERNAME = "my username";
		final String PASSWORD = "my password";
		
		final String serializedMessage = weblabSerializer.serializeLoginRequest(USERNAME, PASSWORD);
		
		Assert.assertEquals(
				"{\"params\":{\"username\":\"" + USERNAME + "\", \"password\":\"" + PASSWORD + "\"}, \"method\":\"login\"}",
				serializedMessage
			);
	}
	
	public void testSerializeLogoutRequest() throws Exception{
		final ICommonSerializer weblabSerializer = new CommonSerializerJSON();
		final String MESSAGE = "whatever the session id real id";
		
		final SessionID sessionId = new SessionID(MESSAGE);
		final String serializedMessage = weblabSerializer.serializeLogoutRequest(sessionId);
		
		Assert.assertEquals(
				"{\"params\":{\"session_id\":{\"id\":\"" + MESSAGE + "\"}}, \"method\":\"logout\"}",
				serializedMessage
			);
	}	
	
	@Override
	public String getModuleName() {
		return "es.deusto.weblab.WebLabClient";
	}	
}