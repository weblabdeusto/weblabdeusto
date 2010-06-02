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

import com.google.gwt.junit.client.GWTTestCase;

import es.deusto.weblab.client.comm.exceptions.WlServerException;
import es.deusto.weblab.client.comm.exceptions.core.SessionNotFoundException;
import es.deusto.weblab.client.comm.exceptions.core.UserProcessingException;
import es.deusto.weblab.client.dto.SessionID;
import es.deusto.weblab.client.dto.users.Group;
import junit.framework.Assert;

public class WlAdminSerializerJSONTest extends GWTTestCase {

	public void testParseGetGroupsResponse() throws Exception {
		final IWlAdminSerializer weblabSerializer = new WlAdminSerializerJSON();
		final ArrayList<Group> groups = weblabSerializer.parseGetGroupsResponse(
			"{\"result\": [" +
				"{\"name\": \"Course 200910\", \"children\": [" +
					"{\"name\": \"Telecomunications\", \"children\": []}, " +
					"{\"name\": \"Mecatronics\", \"children\": [" +
						"{\"name\": \"Morning\", \"children\": []} ] } ] }, " +
				"{\"name\": \"Course 201011\", \"children\": []} ], " +
			"\"is_exception\": false}"
		);
		
		Assert.assertEquals(2, groups.size());
		
		Assert.assertEquals("Course 200910",     groups.get(0).getName() );
		Assert.assertEquals(2,                   groups.get(0).getChildren().size());
		
		Assert.assertEquals("Telecomunications", groups.get(0).getChildren().get(0).getName());
		Assert.assertEquals(0,                   groups.get(0).getChildren().get(0).getChildren().size());
		
		Assert.assertEquals("Mecatronics",       groups.get(0).getChildren().get(1).getName());
		Assert.assertEquals(1,                   groups.get(0).getChildren().get(1).getChildren().size());

		Assert.assertEquals("Morning",       	 groups.get(0).getChildren().get(1).getChildren().get(0).getName());
		Assert.assertEquals(0,                   groups.get(0).getChildren().get(1).getChildren().get(0).getChildren().size());
		
		Assert.assertEquals("Course 201011",     groups.get(1).getName() );
		Assert.assertEquals(0,                   groups.get(1).getChildren().size());	
	}
	
	public void testParseGetGroupsResponse_Faults() throws Exception{
		final IWlAdminSerializer weblabSerializer = new WlAdminSerializerJSON();
		
		final String MESSAGE = "my message";
		final String whole_message = "{\"message\": \"" + MESSAGE + "\", \"code\": \"THE_FAULT_CODE\", \"is_exception\": true}";
		
		try {
			weblabSerializer.parseGetGroupsResponse(
				whole_message.replaceFirst("THE_FAULT_CODE", "JSON:Client.SessionNotFound")
			);
			Assert.fail("Exception expected");
		} catch (final SessionNotFoundException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
		
		try {
			weblabSerializer.parseGetGroupsResponse(
				whole_message.replaceFirst("THE_FAULT_CODE", "JSON:Server.UserProcessing")
			);
			Assert.fail("Exception expected");
		} catch (final UserProcessingException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
		
		try {
			weblabSerializer.parseGetGroupsResponse(
				whole_message.replaceFirst("THE_FAULT_CODE", "JSON:Server.WebLab")
			);
			Assert.fail("Exception expected");
		} catch (final WlServerException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
		
		try {
			weblabSerializer.parseGetGroupsResponse(
				whole_message.replaceFirst("THE_FAULT_CODE", "JSON:Server.Voodoo")
			);
			Assert.fail("Exception expected");
		} catch (final WlServerException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
		
		try {
			weblabSerializer.parseGetGroupsResponse(
				whole_message.replaceFirst("THE_FAULT_CODE", "JSON:Server.Python")
			);
			Assert.fail("Exception expected");
		} catch (final WlServerException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
	}	 	
	
	public void testSerializeGetGroupsRequest() throws Exception {
		final IWlAdminSerializer weblabSerializer = new WlAdminSerializerJSON();
		final String MESSAGE = "whatever the session id real id";
		
		final SessionID sessionId = new SessionID(MESSAGE);
		final String serializedMessage = weblabSerializer.serializeGetGroupsRequest(sessionId);
		
		Assert.assertEquals(
				"{\"params\":{\"session_id\":{\"id\":\"" + MESSAGE + "\"}}, \"method\":\"get_groups\"}",
				serializedMessage
			);
	}
	
	@Override
	public String getModuleName() {
		return "es.deusto.weblab.WebLabClient";
	}
}
