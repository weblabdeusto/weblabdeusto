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

public class PermissionTypesDataSource extends WebLabRestDataSource {

	public PermissionTypesDataSource(SessionID sessionId) {
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
        final DataSourceTextField nameDSField = new DataSourceTextField("name", "Name");
        final DataSourceIntegerField descDSField = new DataSourceIntegerField("description", "Description");    
        
	    this.setFields(idField, nameDSField, descDSField);  
	    this.setFetchDataURL("data/permission_types_fetch.js");
	}
}
