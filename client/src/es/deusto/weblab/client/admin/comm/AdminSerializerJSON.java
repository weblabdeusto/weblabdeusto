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

import com.google.gwt.json.client.JSONArray;
import com.google.gwt.json.client.JSONObject;
import com.google.gwt.json.client.JSONValue;

import es.deusto.weblab.client.comm.CommonSerializerJSON;
import es.deusto.weblab.client.comm.exceptions.SerializationException;
import es.deusto.weblab.client.comm.exceptions.WebLabServerException;
import es.deusto.weblab.client.comm.exceptions.core.SessionNotFoundException;
import es.deusto.weblab.client.comm.exceptions.core.UserProcessingException;
import es.deusto.weblab.client.dto.SessionID;
import es.deusto.weblab.client.dto.users.Permission;
import es.deusto.weblab.client.dto.users.PermissionParameter;

public class AdminSerializerJSON extends CommonSerializerJSON implements IAdminSerializer {

	@Override
	public Permission[] parseGetUserPermissionsResponse(String responseText)
			throws SerializationException, SessionNotFoundException,
			UserProcessingException, WebLabServerException {
			/*{
			    "result": [
			            {
			                "name": "experiment_allowed",
			                "parameters": [
			                      { "name": "experiment_permanent_id",
			                        "datatype": "string",
			                        "value": "ud-fpga"
			                      },
			                      { "name": "experiment_category_id",
			                        "datatype": "string",
			                        "value": "FPGA experiments"
			                      },
			                      { "name": "time_allowed",
			                        "datatype": "float",
			                        "value": "300"
			                      } 
			                ]
			            },
			            {
			                "name": "admin_panel_access",
			                "parameters": [
			                      { "name": "full_privileges",
			                        "datatype": "bool",
			                        "value": "1"
			                      }
			                ]
			            }
			    ],
			    "is_exception": false
			}*/
		final JSONArray result = this.parseResultArray(responseText);
		final Permission [] permissions = new Permission[result.size()];
		for(int i = 0; i < result.size(); ++i){
		    final JSONValue value = result.get(i);
		    final JSONObject jsonPermission = value.isObject();
		    if(jsonPermission == null)
		    	throw new SerializationException("Expected JSON Object as Permission, found: " + value);
		    final String name = this.json2string(jsonPermission.get("name"));
		    final JSONValue jsonParametersValue = jsonPermission.get("parameters");
		    final JSONArray jsonParameters = jsonParametersValue.isArray();
		    if(jsonParameters == null)
		    	throw new SerializationException("Expected JSON Array as PermissionParameters, found: " + jsonParametersValue);
		    final PermissionParameter[] parameters = new PermissionParameter[jsonParameters.size()];
		    for ( int j = 0; j < jsonParameters.size(); ++j) {
		    	final JSONValue jsonParameterValue = jsonParameters.get(j);
		    	final JSONObject jsonParameter = jsonParameterValue.isObject();
			    if(jsonParameter == null)
			    	throw new SerializationException("Expected JSON Object as PermissionParameter, found: " + jsonParameterValue);
		    	parameters[j] = this.parsePermissionParameter(jsonParameter);
		    }
		    permissions[i] = new Permission(name, parameters);
		}
		return permissions;
	}

	@Override
	public String serializeGetUserPermissionsRequest(SessionID sessionId)
			throws SerializationException {
		final JSONObject params = new JSONObject();
		params.put("session_id", this.serializeSessionId(sessionId));
		return this.serializeRequest("get_user_permissions", params);
	}
}
