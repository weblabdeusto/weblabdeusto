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
* Author: Jaime Irurzun <jaime.irurzun@gmail.com>
*
*/

package es.deusto.weblab.client.admin.comm.datasources;

import com.smartgwt.client.data.OperationBinding;
import com.smartgwt.client.data.fields.DataSourceIntegerField;
import com.smartgwt.client.data.fields.DataSourceTextField;
import com.smartgwt.client.types.DSOperationType;
import com.smartgwt.client.types.DSProtocol;

import es.deusto.weblab.client.admin.dto.ExperimentRecord;
import es.deusto.weblab.client.configuration.IConfigurationManager;
import es.deusto.weblab.client.dto.SessionID;

public class ExperimentsDataSource extends WebLabRestDataSource {

	public ExperimentsDataSource(SessionID sessionId, IConfigurationManager configurationManager) {
		super(sessionId, configurationManager);
	}
	
	@Override
	public void initialize() {
	    final OperationBinding fetch = new OperationBinding();  
	    fetch.setOperationType(DSOperationType.FETCH);  
	    fetch.setDataProtocol(DSProtocol.GETPARAMS);
	    
	    this.setOperationBindings(fetch);
	    
	    // i18n
	    final DataSourceIntegerField idField = new DataSourceIntegerField(ExperimentRecord.ID, "ID");  
	    idField.setPrimaryKey(true);
	    idField.setCanEdit(false);  
	    final DataSourceTextField nameDSField = new DataSourceTextField(ExperimentRecord.NAME, "Name");
	    final DataSourceTextField categoryDSField = new DataSourceTextField(ExperimentRecord.CATEGORY, "Category");
	    
	    this.setFields(idField, nameDSField, categoryDSField);  
	    this.setFetchDataURL(this.baseLocation + "/weblab/administration/json/experiments");
	}
}
