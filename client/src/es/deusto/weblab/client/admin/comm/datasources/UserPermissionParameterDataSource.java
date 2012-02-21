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
* Author: Luis Rodriguez <luis.rodriguez@opendeusto.es>
*
*/

package es.deusto.weblab.client.admin.comm.datasources;

import com.smartgwt.client.data.OperationBinding;
import com.smartgwt.client.data.fields.DataSourceIntegerField;
import com.smartgwt.client.data.fields.DataSourceTextField;
import com.smartgwt.client.types.DSOperationType;
import com.smartgwt.client.types.DSProtocol;

import es.deusto.weblab.client.dto.SessionID;

/**
 * DataSource for UserPermissionParameter, the class which contains the actual parameter
 * values. Each UserPermissionParameter is, in a way, an instance of a 
 * PermissionTypeParameter.
 */
public class UserPermissionParameterDataSource extends WebLabRestDataSource {

	public UserPermissionParameterDataSource(SessionID sessionId) {
		super(sessionId);
	}
	
	@Override
	public void initialize() {
	    final OperationBinding fetch = new OperationBinding();  
	    fetch.setOperationType(DSOperationType.FETCH);  
	    fetch.setDataProtocol(DSProtocol.GETPARAMS);
	    
	    this.setOperationBindings(fetch);

        final DataSourceIntegerField idField = new DataSourceIntegerField("id", "ID");  
        idField.setPrimaryKey(true);
        idField.setCanEdit(false);  
        final DataSourceIntegerField permissionIdField = new DataSourceIntegerField("permission_id", "permission_id"); 
        final DataSourceTextField permissionTypeParameterIdField = new DataSourceTextField("permission_type_parameter_id", "permission_type_parameter_id");
        final DataSourceTextField valueField = new DataSourceTextField("value", "value");
        
	    this.setFields(idField, permissionIdField, permissionTypeParameterIdField, valueField);  
	    this.setFetchDataURL("data/user_permission_parameter_fetch.js");
	}
}