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
import com.smartgwt.client.data.fields.DataSourceDateTimeField;
import com.smartgwt.client.data.fields.DataSourceIntegerField;
import com.smartgwt.client.data.fields.DataSourceTextField;
import com.smartgwt.client.types.DSOperationType;
import com.smartgwt.client.types.DSProtocol;
import com.smartgwt.client.types.DateDisplayFormat;

import es.deusto.weblab.client.admin.dto.ExperimentUseRecord;
import es.deusto.weblab.client.configuration.IConfigurationManager;
import es.deusto.weblab.client.dto.SessionID;

public class ExperimentUsesDataSource extends WebLabRestDataSource {

	public ExperimentUsesDataSource(SessionID sessionId, IConfigurationManager configurationManager) {
		super(sessionId, configurationManager);
	}
	
	@Override
	public void initialize() {
	    final OperationBinding fetch = new OperationBinding();  
	    fetch.setOperationType(DSOperationType.FETCH);  
	    fetch.setDataProtocol(DSProtocol.GETPARAMS);
	    
	    this.setOperationBindings(fetch);
	    
	    // i18n
	    final DataSourceIntegerField idField = new DataSourceIntegerField(ExperimentUseRecord.ID, "#");  
	    idField.setPrimaryKey(true);
	    idField.setCanEdit(false);  
	    
	    final DataSourceDateTimeField startDateDSField = new DataSourceDateTimeField(ExperimentUseRecord.START_DATE, "Start Date");
	    startDateDSField.setDisplayFormat(DateDisplayFormat.TOEUROPEANSHORTDATE);
	    
	    final DataSourceDateTimeField endDateDSField = new DataSourceDateTimeField(ExperimentUseRecord.END_DATE, "End Date");
	    endDateDSField.setDisplayFormat(DateDisplayFormat.TOEUROPEANSHORTDATE);
	    
	    final DataSourceTextField agentLoginDSField = new DataSourceTextField(ExperimentUseRecord.AGENT_LOGIN, "Login");
	    final DataSourceTextField agentNameDSField = new DataSourceTextField(ExperimentUseRecord.AGENT_NAME, "Name");
	    final DataSourceTextField agentEmailDSField = new DataSourceTextField(ExperimentUseRecord.AGENT_EMAIL, "E-mail");
	    final DataSourceTextField experimentNameDSField = new DataSourceTextField(ExperimentUseRecord.EXPERIMENT_NAME, "Experiment Name");
	    final DataSourceTextField experimentCategoryDSField = new DataSourceTextField(ExperimentUseRecord.EXPERIMENT_CATEGORY, "Experiment Category");
	    final DataSourceTextField originDSField = new DataSourceTextField(ExperimentUseRecord.ORIGIN, "Origin");
	    
	    this.setFields(idField, startDateDSField, endDateDSField, agentLoginDSField, agentNameDSField, agentEmailDSField, experimentNameDSField, experimentCategoryDSField, originDSField);  
	    this.setFetchDataURL(this.baseLocation + "/weblab/administration/json/experiment_uses");
	}
}
