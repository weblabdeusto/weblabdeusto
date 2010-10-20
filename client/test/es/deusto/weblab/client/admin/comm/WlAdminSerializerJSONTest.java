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

import junit.framework.Assert;

import com.google.gwt.junit.client.GWTTestCase;

import es.deusto.weblab.client.dto.SessionID;
import es.deusto.weblab.client.dto.users.Permission;

public class WlAdminSerializerJSONTest extends GWTTestCase {
	
	public void testParseGetUserPermissionsResponse() throws Exception{
		final IWlAdminSerializer weblabSerializer = new WlAdminSerializerJSON();
		final Permission [] permissions = weblabSerializer.parseGetUserPermissionsResponse(
			"{ \"result\":" +
				"[" +
					"{" +
		                "\"name\": \"experiment_allowed\"," +
		                "\"parameters\": [" +
		                      "{ \"name\": \"experiment_permanent_id\"," +
		                        "\"datatype\": \"string\"," +
		                        "\"value\": \"ud-fpga\"" +
		                      "}," +
		                      "{ \"name\": \"experiment_category_id\"," +
		                        "\"datatype\": \"string\"," +
		                        "\"value\": \"FPGA experiments\"" +
		                      "}," +
		                      "{ \"name\": \"time_allowed\"," +
		                        "\"datatype\": \"float\"," +
		                        "\"value\": \"300\"" +
		                      "} " +
		                "]" +
		            "}," +
		            "{" +
		                "\"name\": \"admin_panel_access\"," +
		                "\"parameters\": [" +
		                      "{ \"name\": \"full_privileges\"," +
		                        "\"datatype\": \"bool\"," +
		                        "\"value\": \"1\"" +
		                      "}" +
		                "]" +
		            "}" +
			    "]," +
			    "\"is_exception\": false" +
			"}"
		);
		
		Assert.assertEquals(2, permissions.length);
		
		// 0
		Assert.assertEquals("experiment_allowed",      permissions[0].getName());
		Assert.assertEquals("experiment_permanent_id", permissions[0].getParameters()[0].getName());
		Assert.assertEquals("string",                  permissions[0].getParameters()[0].getDatatype());
		Assert.assertEquals("ud-fpga",                 permissions[0].getParameters()[0].getValue());
		Assert.assertEquals("experiment_category_id",  permissions[0].getParameters()[1].getName());
		Assert.assertEquals("string",                  permissions[0].getParameters()[1].getDatatype());
		Assert.assertEquals("FPGA experiments",        permissions[0].getParameters()[1].getValue());
		Assert.assertEquals("time_allowed",            permissions[0].getParameters()[2].getName());
		Assert.assertEquals("float",                   permissions[0].getParameters()[2].getDatatype());
		Assert.assertEquals("300",                     permissions[0].getParameters()[2].getValue());
		
		// 1
		Assert.assertEquals("admin_panel_access",      permissions[1].getName());
		Assert.assertEquals("full_privileges",         permissions[1].getParameters()[0].getName());
		Assert.assertEquals("bool",                    permissions[1].getParameters()[0].getDatatype());
		Assert.assertEquals("1",                       permissions[1].getParameters()[0].getValue());
	}		
	
	public void testGetUserPermissionsRequest() throws Exception{
		final IWlAdminSerializer weblabSerializer = new WlAdminSerializerJSON();
		final String MESSAGE = "whatever the session id real id";
		
		final SessionID sessionId = new SessionID(MESSAGE);
		final String serializedMessage = weblabSerializer.serializeGetUserPermissionsRequest(sessionId);
		
		Assert.assertEquals(
				"{\"params\":{\"session_id\":{\"id\":\"" + MESSAGE + "\"}}, \"method\":\"get_user_permissions\"}",
				serializedMessage
			);
	}	   
    
	@Override
	public String getModuleName() {
		return "es.deusto.weblab.WebLabClient";
	}
}
