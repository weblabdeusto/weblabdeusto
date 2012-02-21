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

public class UserPermissionsDataSource extends WebLabRestDataSource {

	public UserPermissionsDataSource(SessionID sessionId) {
		super(sessionId);
	}
	
	@Override
	public void initialize() {
	    final OperationBinding fetch = new OperationBinding();  
	    fetch.setOperationType(DSOperationType.FETCH);  
	    fetch.setDataProtocol(DSProtocol.GETPARAMS);
	    
	    this.setOperationBindings(fetch);
	    
	    // TODO: Get rid of hard-coded strings.
	    final DataSourceIntegerField idField = new DataSourceIntegerField("id", "ID");  
	    idField.setPrimaryKey(true);
	    idField.setCanEdit(false);  
	    final DataSourceIntegerField idAuthTypeField = new DataSourceIntegerField("user_id", "ID"); 
	    final DataSourceIntegerField permissionTypeField = new DataSourceIntegerField("applicable_permission_type_id", "PermissionType");
	    final DataSourceTextField permanentIdField = new DataSourceTextField("permanent_id", "PermanentId");
	    final DataSourceTextField dateField = new DataSourceTextField("date", "Date");
	    final DataSourceTextField commentsField = new DataSourceTextField("comments", "Comments");
	    
	    this.setFields(idField, idAuthTypeField, permissionTypeField, permanentIdField, dateField, commentsField);
	    
	    
	    //this.setFetchDataURL("data/permissions_fetch.js");
	    this.setFetchDataURL("/weblab/administration/json/user_permissions");
	}
}

