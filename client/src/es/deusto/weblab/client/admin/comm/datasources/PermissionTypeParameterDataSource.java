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

import es.deusto.weblab.client.configuration.IConfigurationManager;
import es.deusto.weblab.client.dto.SessionID;

/**
 * DataSource for PermissionTypeParameter, the class which contains the parameters of each permission type,
 * including its name and its type.
 */
public class PermissionTypeParameterDataSource extends WebLabRestDataSource {

	public PermissionTypeParameterDataSource(SessionID sessionId, IConfigurationManager configurationManager) {
		super(sessionId, configurationManager);
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
        final DataSourceIntegerField permTypeIdField = new DataSourceIntegerField("permission_type_id", "permission_type_id"); 
        final DataSourceTextField nameDSField = new DataSourceTextField("name", "Name");
        final DataSourceTextField dataTypeDSField = new DataSourceTextField("datatype", "Datatype");
        final DataSourceTextField descDSField = new DataSourceTextField("description", "description");
        
	    this.setFields(idField, permTypeIdField, nameDSField, dataTypeDSField, descDSField);  
	    this.setFetchDataURL("data/permission_type_parameter_fetch.js");
	}
}
