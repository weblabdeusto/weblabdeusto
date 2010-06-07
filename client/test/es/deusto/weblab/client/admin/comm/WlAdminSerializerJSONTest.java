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

import junit.framework.Assert;

import com.google.gwt.junit.client.GWTTestCase;

import es.deusto.weblab.client.comm.exceptions.WlServerException;
import es.deusto.weblab.client.comm.exceptions.core.SessionNotFoundException;
import es.deusto.weblab.client.comm.exceptions.core.UserProcessingException;
import es.deusto.weblab.client.dto.SessionID;
import es.deusto.weblab.client.dto.experiments.Experiment;
import es.deusto.weblab.client.dto.users.Group;

public class WlAdminSerializerJSONTest extends GWTTestCase {

	public void testParseGetGroupsResponse() throws Exception {
		final IWlAdminSerializer weblabSerializer = new WlAdminSerializerJSON();
		final ArrayList<Group> groups = weblabSerializer.parseGetGroupsResponse(
			"{\"result\": [" +
				"{\"id\": 1, \"name\": \"Course 200910\", \"children\": [" +
					"{\"id\": 2, \"name\": \"Telecomunications\", \"children\": []}, " +
					"{\"id\": 3, \"name\": \"Mecatronics\", \"children\": [" +
						"{\"id\": 4, \"name\": \"Morning\", \"children\": []} ] } ] }, " +
				"{\"id\": 5, \"name\": \"Course 201011\", \"children\": []} ], " +
			"\"is_exception\": false}"
		);
		
		Assert.assertEquals(2, groups.size());

		Assert.assertEquals(1,     				 groups.get(0).getId() );
		Assert.assertEquals("Course 200910",     groups.get(0).getName() );
		Assert.assertEquals(2,                   groups.get(0).getChildren().size());

		Assert.assertEquals(2,     				 groups.get(0).getChildren().get(0).getId() );
		Assert.assertEquals("Telecomunications", groups.get(0).getChildren().get(0).getName());
		Assert.assertEquals(0,                   groups.get(0).getChildren().get(0).getChildren().size());

		Assert.assertEquals(3,     				 groups.get(0).getChildren().get(1).getId() );
		Assert.assertEquals("Mecatronics",       groups.get(0).getChildren().get(1).getName());
		Assert.assertEquals(1,                   groups.get(0).getChildren().get(1).getChildren().size());

		Assert.assertEquals(4,     				 groups.get(0).getChildren().get(1).getChildren().get(0).getId() );
		Assert.assertEquals("Morning",       	 groups.get(0).getChildren().get(1).getChildren().get(0).getName());
		Assert.assertEquals(0,                   groups.get(0).getChildren().get(1).getChildren().get(0).getChildren().size());

		Assert.assertEquals(5,     				 groups.get(1).getId() );
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

	public void testParseGetExperimentsResponse() throws Exception {
		final IWlAdminSerializer weblabSerializer = new WlAdminSerializerJSON();
		final ArrayList<Experiment> experiments = weblabSerializer.parseGetExperimentsResponse(
			"{\"result\": [" +
				"{\"id\": 1, \"name\": \"ud-dummy\", \"category\": {\"name\": \"Dummy experiments\"}, \"start_date\": \"2007-01-01\", \"end_date\": \"2008-01-01\"}, " +
				"{\"id\": 2, \"name\": \"ud-fpga\", \"category\": {\"name\": \"FPGA experiments\"}, \"start_date\": \"2005-01-01\", \"end_date\": \"2006-01-01\"}" +
			"], \"is_exception\": false}"
		);
		
		Assert.assertEquals(2, experiments.size());
		
		// 1
		Assert.assertEquals(1,                   experiments.get(0).getId());
		Assert.assertEquals("ud-dummy",          experiments.get(0).getName());
		Assert.assertEquals("Dummy experiments", experiments.get(0).getCategory().getCategory());
		// 2007-01-01 00:00:00
		Assert.assertEquals(1167606000000l,      experiments.get(0).getStartDate().getTime());
		// 2008-01-01 00:00:00
		Assert.assertEquals(1199142000000l,      experiments.get(0).getEndDate().getTime());
		
		// 2
		Assert.assertEquals(2,                  experiments.get(1).getId());
		Assert.assertEquals("ud-fpga",          experiments.get(1).getName());
		Assert.assertEquals("FPGA experiments", experiments.get(1).getCategory().getCategory());
		// 2005-01-01 00:00:00
		Assert.assertEquals(1104534000000l,     experiments.get(1).getStartDate().getTime());
		// 2006-01-01 00:00:00
		Assert.assertEquals(1136070000000l,     experiments.get(1).getEndDate().getTime());

	}
	
	public void testParseGetExperimentsResponseWithOtherDateFormat() throws Exception{
		final IWlAdminSerializer weblabSerializer = new WlAdminSerializerJSON();
		final ArrayList<Experiment> experiments = weblabSerializer.parseGetExperimentsResponse(
			"{\"result\": [" +
				"{\"id\": 1, \"name\": \"ud-dummy\", \"category\": {\"name\": \"Dummy experiments\"}, \"start_date\": \"2007-01-01 00:00:00\", \"end_date\": \"2008-01-01 00:00:00\"}, " +
				"{\"id\": 2, \"name\": \"ud-fpga\", \"category\": {\"name\": \"FPGA experiments\"}, \"start_date\": \"2005-01-01 00:00:00\", \"end_date\": \"2006-01-01 00:00:00\"}" +
			"], \"is_exception\": false}"
		);
		
		Assert.assertEquals(2, experiments.size());
		
		// 1
		Assert.assertEquals(1,                   experiments.get(0).getId());
		Assert.assertEquals("ud-dummy",          experiments.get(0).getName());
		Assert.assertEquals("Dummy experiments", experiments.get(0).getCategory().getCategory());
		// 2007-01-01 00:00:00
		Assert.assertEquals(1167606000000l,      experiments.get(0).getStartDate().getTime());
		// 2008-01-01 00:00:00
		Assert.assertEquals(1199142000000l,      experiments.get(0).getEndDate().getTime());
		
		// 2
		Assert.assertEquals(2,                  experiments.get(1).getId());
		Assert.assertEquals("ud-fpga",          experiments.get(1).getName());
		Assert.assertEquals("FPGA experiments", experiments.get(1).getCategory().getCategory());
		// 2005-01-01 00:00:00
		Assert.assertEquals(1104534000000l,     experiments.get(1).getStartDate().getTime());
		// 2006-01-01 00:00:00
		Assert.assertEquals(1136070000000l,     experiments.get(1).getEndDate().getTime());
	}

	public void testParseGetExperimentsResponse_Faults() throws Exception{
		final IWlAdminSerializer weblabSerializer = new WlAdminSerializerJSON();
		
		final String MESSAGE = "my message";
		final String whole_message = "{\"message\": \"" + MESSAGE + "\", \"code\": \"THE_FAULT_CODE\", \"is_exception\": true}";
		
		try {
			weblabSerializer.parseGetExperimentsResponse(
				whole_message.replaceFirst("THE_FAULT_CODE", "JSON:Client.SessionNotFound")
			);
			Assert.fail("Exception expected");
		} catch (final SessionNotFoundException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
		try {
			weblabSerializer.parseGetExperimentsResponse(
				whole_message.replaceFirst("THE_FAULT_CODE", "JSON:Server.UserProcessing")
			);
			Assert.fail("Exception expected");
		} catch (final UserProcessingException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
		try {
			weblabSerializer.parseGetExperimentsResponse(
				whole_message.replaceFirst("THE_FAULT_CODE", "JSON:Server.WebLab")
			);
			Assert.fail("Exception expected");
		} catch (final WlServerException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
		try {
			weblabSerializer.parseGetExperimentsResponse(
				whole_message.replaceFirst("THE_FAULT_CODE", "JSON:Server.Voodoo")
			);
			Assert.fail("Exception expected");
		} catch (final WlServerException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
		try {
			weblabSerializer.parseGetExperimentsResponse(
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
	
	public void testSerializeGetExperimentsRequest() throws Exception {
		final IWlAdminSerializer weblabSerializer = new WlAdminSerializerJSON();
		final String MESSAGE = "whatever the session id real id";
		
		final SessionID sessionId = new SessionID(MESSAGE);
		final String serializedMessage = weblabSerializer.serializeGetExperimentsRequest(sessionId);
		
		Assert.assertEquals(
				"{\"params\":{\"session_id\":{\"id\":\"" + MESSAGE + "\"}}, \"method\":\"get_experiments\"}",
				serializedMessage
			);
	}
	
	@Override
	public String getModuleName() {
		return "es.deusto.weblab.WebLabClient";
	}
}
