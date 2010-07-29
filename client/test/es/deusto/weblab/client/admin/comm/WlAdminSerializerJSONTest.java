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
*         Jaime Irurzun <jaime.irurzun@gmail.com>
*
*/

package es.deusto.weblab.client.admin.comm;

import java.util.ArrayList;
import java.util.Date;

import junit.framework.Assert;

import com.google.gwt.junit.client.GWTTestCase;

import es.deusto.weblab.client.comm.exceptions.SerializationException;
import es.deusto.weblab.client.comm.exceptions.WlServerException;
import es.deusto.weblab.client.comm.exceptions.core.SessionNotFoundException;
import es.deusto.weblab.client.comm.exceptions.core.UserProcessingException;
import es.deusto.weblab.client.dto.SessionID;
import es.deusto.weblab.client.dto.experiments.Experiment;
import es.deusto.weblab.client.dto.experiments.ExperimentUse;
import es.deusto.weblab.client.dto.users.ExternalEntity;
import es.deusto.weblab.client.dto.users.Group;
import es.deusto.weblab.client.dto.users.Role;
import es.deusto.weblab.client.dto.users.User;

public class WlAdminSerializerJSONTest extends GWTTestCase {
	
	public void testParseGetUsersResponse() throws Exception {
		final IWlAdminSerializer weblabSerializer = new WlAdminSerializerJSON();
		final ArrayList<User> users = weblabSerializer.parseGetUsersResponse(
				"{\"result\": [" +
					  "{\"id\":1, \"login\":\"firstlogin\", \"full_name\":\"First Student\", \"email\":\"stud1@mail.com\", \"avatar\":\"av1\", \"role\":{\"id\":1, \"name\":\"firstrole\"} }," +
					  "{\"id\":2, \"login\":\"secondlogin\", \"full_name\":\"Second Student\", \"email\":\"stud2@mail.com\", \"avatar\":\"av2\", \"role\":{\"id\":3, \"name\":\"secondrole\"} }," +
					  "], \"is_exception\": false }"
				);
		
		Assert.assertEquals(2, users.size());
		
		final User us1 = users.get(0);
		//Assert.assertEquals(1, users.get(0).getId());
		Assert.assertEquals("firstlogin", us1.getLogin());
		Assert.assertEquals("First Student", us1.getFullName());
		Assert.assertEquals("stud1@mail.com", us1.getEmail());
		//Assert.assertEquals("av1", users.get(0).getAvatar());
		final Role rol1 = us1.getRole();
		Assert.assertEquals("firstrole", rol1.getName());
		
		final User us2 = users.get(1);
		//Assert.assertEquals(2, us2.getId());
		Assert.assertEquals("secondlogin", us2.getLogin());
		Assert.assertEquals("Second Student", us2.getFullName());
		Assert.assertEquals("stud2@mail.com", us2.getEmail());
		//Assert.assertEquals("av2", us2.getAvatar());
		final Role rol2 = us2.getRole();
		Assert.assertEquals("secondrole", rol2.getName());
	}

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
	
	private void parseGetExperimentsResponse(String response) throws SerializationException, SessionNotFoundException, UserProcessingException, WlServerException {
		final IWlAdminSerializer weblabSerializer = new WlAdminSerializerJSON();
		final ArrayList<Experiment> experiments = weblabSerializer.parseGetExperimentsResponse(response);
		
		Assert.assertEquals(2, experiments.size());
		
		// 1
		Assert.assertEquals(1,                   experiments.get(0).getId());
		Assert.assertEquals("ud-dummy",          experiments.get(0).getName());
		Assert.assertEquals("Dummy experiments", experiments.get(0).getCategory().getCategory());		
		Assert.assertEquals(1167606000000l,      experiments.get(0).getStartDate().getTime()); // 2007-01-01 00:00:00
		Assert.assertEquals(1199142000000l,      experiments.get(0).getEndDate().getTime()); // 2008-01-01 00:00:00
		
		// 2
		Assert.assertEquals(2,                  experiments.get(1).getId());
		Assert.assertEquals("ud-fpga",          experiments.get(1).getName());
		Assert.assertEquals("FPGA experiments", experiments.get(1).getCategory().getCategory());
		Assert.assertEquals(1104534000000l,     experiments.get(1).getStartDate().getTime()); // 2005-01-01 00:00:00
		Assert.assertEquals(1136070000000l,     experiments.get(1).getEndDate().getTime()); // 2006-01-01 00:00:00		
	}

	public void testParseGetExperimentsResponse() throws Exception {
		this.parseGetExperimentsResponse(
			"{\"result\": [" +
				"{\"id\": 1, \"name\": \"ud-dummy\", \"category\": {\"name\": \"Dummy experiments\"}, \"start_date\": \"2007-01-01\", \"end_date\": \"2008-01-01\"}, " +
				"{\"id\": 2, \"name\": \"ud-fpga\", \"category\": {\"name\": \"FPGA experiments\"}, \"start_date\": \"2005-01-01\", \"end_date\": \"2006-01-01\"}" +
			"], \"is_exception\": false}"
		);
	}
	
	public void testParseGetExperimentsResponseWithOtherDateFormat() throws Exception{
		this.parseGetExperimentsResponse(
			"{\"result\": [" +
				"{\"id\": 1, \"name\": \"ud-dummy\", \"category\": {\"name\": \"Dummy experiments\"}, \"start_date\": \"2007-01-01 00:00:00\", \"end_date\": \"2008-01-01 00:00:00\"}, " +
				"{\"id\": 2, \"name\": \"ud-fpga\", \"category\": {\"name\": \"FPGA experiments\"}, \"start_date\": \"2005-01-01 00:00:00\", \"end_date\": \"2006-01-01 00:00:00\"}" +
			"], \"is_exception\": false}"
		);
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
	
	private void parseGetExperimentUsesResponse(String response) throws SerializationException, SessionNotFoundException, UserProcessingException, WlServerException {
		final IWlAdminSerializer weblabSerializer = new WlAdminSerializerJSON();
		final ArrayList<ExperimentUse> experimentUses = weblabSerializer.parseGetExperimentUsesResponse(response);
		
		Assert.assertEquals(2, experimentUses.size());
		
		// 1
		Assert.assertEquals(1,                               experimentUses.get(0).getId());
		Assert.assertEquals(1104534000000l,                  experimentUses.get(0).getStartDate().getTime()); // 2005-01-01 00:00:00
		Assert.assertEquals(1136070000000l,                  experimentUses.get(0).getEndDate().getTime()); // 2006-01-01 00:00:00
		Assert.assertEquals("unknown",                       experimentUses.get(0).getOrigin());
		
		Assert.assertEquals(1,                               experimentUses.get(0).getExperiment().getId());
		Assert.assertEquals("ud-dummy",                      experimentUses.get(0).getExperiment().getName());
		Assert.assertEquals("Dummy experiments",             experimentUses.get(0).getExperiment().getCategory().getCategory());
		Assert.assertEquals(1167606000000l,                  experimentUses.get(0).getExperiment().getStartDate().getTime()); // 2007-01-01 00:00:00
		Assert.assertEquals(1199142000000l,                  experimentUses.get(0).getExperiment().getEndDate().getTime()); // 2008-01-01 00:00:00
		
		Assert.assertEquals("porduna",                       ((User)experimentUses.get(0).getAgent()).getLogin());
		Assert.assertEquals("Pablo Orduna",                  ((User)experimentUses.get(0).getAgent()).getFullName());
		Assert.assertEquals("porduna@tecnologico.deusto.es", ((User)experimentUses.get(0).getAgent()).getEmail());
		Assert.assertEquals("student",                       ((User)experimentUses.get(0).getAgent()).getRole().getName());
		
		// 2
		Assert.assertEquals(2,                               experimentUses.get(1).getId());
		Assert.assertEquals(1167606000000l,                  experimentUses.get(1).getStartDate().getTime()); // 2007-01-01 00:00:00
		Assert.assertEquals(1199142000000l,                  experimentUses.get(1).getEndDate().getTime()); // 2008-01-01 00:00:00
		Assert.assertEquals("unknown",                       experimentUses.get(1).getOrigin());
		
		Assert.assertEquals(2,                               experimentUses.get(1).getExperiment().getId());
		Assert.assertEquals("ud-fpga",                       experimentUses.get(1).getExperiment().getName());
		Assert.assertEquals("FPGA experiments",              experimentUses.get(1).getExperiment().getCategory().getCategory());
		Assert.assertEquals(1104534000000l,                  experimentUses.get(1).getExperiment().getStartDate().getTime()); // 2005-01-01 00:00:00
		Assert.assertEquals(1136070000000l,                  experimentUses.get(1).getExperiment().getEndDate().getTime()); // 2006-01-01 00:00:00
		
		Assert.assertEquals(1,                               ((ExternalEntity)experimentUses.get(1).getAgent()).getId());
		Assert.assertEquals("UNED",                          ((ExternalEntity)experimentUses.get(1).getAgent()).getName());
		Assert.assertEquals("Spain",                         ((ExternalEntity)experimentUses.get(1).getAgent()).getCountry());
		Assert.assertEquals("Spanish University...",         ((ExternalEntity)experimentUses.get(1).getAgent()).getDescription());
		Assert.assertEquals("smartin@ieec.uned.es",          ((ExternalEntity)experimentUses.get(1).getAgent()).getEmail());		
	}
	
	public void testParseGetExperimentUsesResponse() throws Exception {
		this.parseGetExperimentUsesResponse(
			"{\"result\": [" +
				"{\"id\": 1, " +
					"\"start_date\": \"2005-01-01\", " +
					"\"end_date\": \"2006-01-01\", " +
					"\"experiment\": {" +
						"\"id\": 1, " +
						"\"name\": \"ud-dummy\", " +
						"\"category\": {" +
							"\"name\": \"Dummy experiments\"}, " +
						"\"start_date\": \"2007-01-01\", " +
						"\"end_date\": \"2008-01-01\"}, " +
					"\"agent\": {" +
						"\"login\": \"porduna\", " +
						"\"email\": \"porduna@tecnologico.deusto.es\", " +
						"\"full_name\": \"Pablo Orduna\", " +
						"\"role\": {" +
							"\"name\": \"student\"}}, " +
					"\"origin\": \"unknown\" }, " +
				"{\"id\": 2, " +
					"\"start_date\": \"2007-01-01\", " +
					"\"end_date\": \"2008-01-01\", " +
					"\"experiment\": {" +
						"\"id\": 2, " +
						"\"name\": \"ud-fpga\", " +
						"\"category\": {" +
							"\"name\": \"FPGA experiments\"}, " +
						"\"start_date\": \"2005-01-01\", " +
						"\"end_date\": \"2006-01-01\"}, " +
					"\"agent\": {" +
						"\"id\": 1, " +
						"\"name\": \"UNED\", " +
						"\"country\": \"Spain\", " +
						"\"description\": \"Spanish University...\", " +
						"\"email\": \"smartin@ieec.uned.es\"}, " +
					"\"origin\": \"unknown\" }" +
			"], \"is_exception\": false}"
		);
	}
	
	public void testParseGetExperimentUsesResponseWithOtherDateFormat() throws Exception{
		this.parseGetExperimentUsesResponse(
				"{\"result\": [" +
					"{\"id\": 1, " +
						"\"start_date\": \"2005-01-01 00:00:00\", " +
						"\"end_date\": \"2006-01-01 00:00:00\", " +
						"\"experiment\": {" +
							"\"id\": 1, " +
							"\"name\": \"ud-dummy\", " +
							"\"category\": {" +
								"\"name\": \"Dummy experiments\"}, " +
							"\"start_date\": \"2007-01-01 00:00:00\", " +
							"\"end_date\": \"2008-01-01 00:00:00\"}, " +
						"\"agent\": {" +
							"\"login\": \"porduna\", " +
							"\"email\": \"porduna@tecnologico.deusto.es\", " +
							"\"full_name\": \"Pablo Orduna\", " +
							"\"role\": {" +
								"\"name\": \"student\"}}, " +
						"\"origin\": \"unknown\" }, " +
					"{\"id\": 2, " +
						"\"start_date\": \"2007-01-01 00:00:00\", " +
						"\"end_date\": \"2008-01-01 00:00:00\", " +
						"\"experiment\": {" +
							"\"id\": 2, " +
							"\"name\": \"ud-fpga\", " +
							"\"category\": {" +
								"\"name\": \"FPGA experiments\"}, " +
							"\"start_date\": \"2005-01-01 00:00:00\", " +
							"\"end_date\": \"2006-01-01 00:00:00\"}, " +
						"\"agent\": {" +
							"\"id\": 1, " +
							"\"name\": \"UNED\", " +
							"\"country\": \"Spain\", " +
							"\"description\": \"Spanish University...\", " +
							"\"email\": \"smartin@ieec.uned.es\"}, " +
						"\"origin\": \"unknown\" }" +
				"], \"is_exception\": false}"
			);
	}

	public void testParseGetExperimentUsesResponse_Faults() throws Exception{
		final IWlAdminSerializer weblabSerializer = new WlAdminSerializerJSON();
		
		final String MESSAGE = "my message";
		final String whole_message = "{\"message\": \"" + MESSAGE + "\", \"code\": \"THE_FAULT_CODE\", \"is_exception\": true}";
		
		try {
			weblabSerializer.parseGetExperimentUsesResponse(
				whole_message.replaceFirst("THE_FAULT_CODE", "JSON:Client.SessionNotFound")
			);
			Assert.fail("Exception expected");
		} catch (final SessionNotFoundException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
		try {
			weblabSerializer.parseGetExperimentUsesResponse(
				whole_message.replaceFirst("THE_FAULT_CODE", "JSON:Server.UserProcessing")
			);
			Assert.fail("Exception expected");
		} catch (final UserProcessingException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
		try {
			weblabSerializer.parseGetExperimentUsesResponse(
				whole_message.replaceFirst("THE_FAULT_CODE", "JSON:Server.WebLab")
			);
			Assert.fail("Exception expected");
		} catch (final WlServerException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
		try {
			weblabSerializer.parseGetExperimentUsesResponse(
				whole_message.replaceFirst("THE_FAULT_CODE", "JSON:Server.Voodoo")
			);
			Assert.fail("Exception expected");
		} catch (final WlServerException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
		try {
			weblabSerializer.parseGetExperimentUsesResponse(
				whole_message.replaceFirst("THE_FAULT_CODE", "JSON:Server.Python")
			);
			Assert.fail("Exception expected");
		} catch (final WlServerException e) {
			Assert.assertEquals(MESSAGE, e.getMessage());
		}
	}		
	
	public void testSerializeGetGroupsRequest() throws Exception {
		final IWlAdminSerializer weblabSerializer = new WlAdminSerializerJSON();
		final String SESSION_ID = "whatever the session id real id";
		
		final SessionID sessionId = new SessionID(SESSION_ID);
		final String serializedMessage = weblabSerializer.serializeGetGroupsRequest(sessionId);
		
		Assert.assertEquals(
				"{\"params\":{\"session_id\":{\"id\":\"" + SESSION_ID + "\"}}, \"method\":\"get_groups\"}",
				serializedMessage
			);
	}
	
	public void testSerializeGetExperimentsRequest() throws Exception {
		final IWlAdminSerializer weblabSerializer = new WlAdminSerializerJSON();
		final String SESSION_ID = "whatever the session id real id";
		
		final SessionID sessionId = new SessionID(SESSION_ID);
		final String serializedMessage = weblabSerializer.serializeGetExperimentsRequest(sessionId);
		
		Assert.assertEquals(
				"{\"params\":{\"session_id\":{\"id\":\"" + SESSION_ID + "\"}}, \"method\":\"get_experiments\"}",
				serializedMessage
			);
	}
	
	public void testSerializeGetExperimentUsesRequest() throws Exception {
		final IWlAdminSerializer weblabSerializer = new WlAdminSerializerJSON();
		final String SESSION_ID = "whatever the session id real id";
		final Date fromDate = new Date();
		final Date toDate = new Date();
		final int groupId = 1;
		final int experimentId = 2;
		
		final SessionID sessionId = new SessionID(SESSION_ID);
		final String serializedMessage = weblabSerializer.serializeGetExperimentUsesRequest(sessionId, fromDate, toDate, groupId, experimentId );
		
		Assert.assertEquals(
				"{\"params\":{" +
					"\"session_id\":{\"id\":\"" + SESSION_ID + "\"}, " +
					"\"from_date\":\"" + fromDate + "\", " + 
					"\"to_date\":\"" + toDate + "\", " + 
					"\"group_id\":" + groupId + ", " + 
					"\"experiment_id\":" + experimentId + 
				"}, \"method\":\"get_experiment_uses\"}",
				serializedMessage
			);
	}
	
	public void testSerializeGetExperimentUsesRequestWithNullParams() throws Exception {
		final IWlAdminSerializer weblabSerializer = new WlAdminSerializerJSON();
		final String SESSION_ID = "whatever the session id real id";
		final Date fromDate = null;
		final Date toDate = null;
		final int groupId = -1;
		final int experimentId = -1;
		
		final SessionID sessionId = new SessionID(SESSION_ID);
		final String serializedMessage = weblabSerializer.serializeGetExperimentUsesRequest(sessionId, fromDate, toDate, groupId, experimentId );
		
		Assert.assertEquals(
				"{\"params\":{" +
					"\"session_id\":{\"id\":\"" + SESSION_ID + "\"}, " +
					"\"from_date\":" + null + ", " + 
					"\"to_date\":" + null + ", " + 
					"\"group_id\":" + null + ", " + 
					"\"experiment_id\":" + null + 
				"}, \"method\":\"get_experiment_uses\"}",
				serializedMessage
			);
	}
	
	@Override
	public String getModuleName() {
		return "es.deusto.weblab.WebLabClient";
	}
}
