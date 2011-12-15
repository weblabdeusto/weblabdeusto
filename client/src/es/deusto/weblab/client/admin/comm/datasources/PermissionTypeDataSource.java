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

public class PermissionTypeDataSource extends WebLabRestDataSource {

	public PermissionTypeDataSource(SessionID sessionId) {
		super(sessionId);
	}
	
	@Override
	public void initialize() {
	    final OperationBinding fetch = new OperationBinding();  
	    fetch.setOperationType(DSOperationType.FETCH);  
	    fetch.setDataProtocol(DSProtocol.GETPARAMS);
	    
	    this.setOperationBindings(fetch);

        final DataSourceTextField nameDSField = new DataSourceTextField("name", "Name");
        nameDSField.setPrimaryKey(true);
        nameDSField.setCanEdit(false);
        final DataSourceTextField descDSField = new DataSourceTextField("description", "Description");    
        final DataSourceIntegerField userAppId = new DataSourceIntegerField("user_applicable_id", "User Applicable ID");
        final DataSourceIntegerField roleAppId = new DataSourceIntegerField("role_applicable_id", "Role Applicable ID");
        final DataSourceIntegerField groupAppId = new DataSourceIntegerField("group_applicable_id", "Group Applicable ID");
        final DataSourceIntegerField eeAppId = new DataSourceIntegerField("ee_applicable_id", "EE Applicable ID");
        
	    this.setFields(nameDSField, descDSField, userAppId, roleAppId, groupAppId, eeAppId);  
	    this.setFetchDataURL("weblab/administration/json/permission_types");
	}
}
