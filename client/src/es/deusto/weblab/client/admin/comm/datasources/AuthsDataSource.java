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

public class AuthsDataSource extends WebLabRestDataSource {

	public AuthsDataSource(SessionID sessionId) {
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
	    final DataSourceIntegerField idAuthTypeField = new DataSourceIntegerField("auth_type_id", "ID"); 
	    final DataSourceTextField nameDSField = new DataSourceTextField("name", "Name");
	    final DataSourceIntegerField priorityDSField = new DataSourceIntegerField("priority", "Priority");
	    final DataSourceTextField configDSField = new DataSourceTextField("configuration", "Configuration");
	    
	    this.setFields(idField, idAuthTypeField, nameDSField, priorityDSField, configDSField);
	    
	    this.setFetchDataURL("data/auths_fetch.js");
	}
}

