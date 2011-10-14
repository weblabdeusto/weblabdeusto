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

package es.deusto.weblab.client.admin.comm.datasources;

import com.smartgwt.client.data.OperationBinding;
import com.smartgwt.client.data.fields.DataSourceIntegerField;
import com.smartgwt.client.data.fields.DataSourceTextField;
import com.smartgwt.client.types.DSOperationType;
import com.smartgwt.client.types.DSProtocol;

import es.deusto.weblab.client.admin.dto.GroupRecord;
import es.deusto.weblab.client.dto.SessionID;

public class GroupsDataSource extends WebLabRestDataSource {

	public GroupsDataSource(SessionID sessionId) {
		super(sessionId);
	}
	
	@Override
	public void initialize() {
	    final OperationBinding fetch = new OperationBinding();  
	    fetch.setOperationType(DSOperationType.FETCH);  
	    fetch.setDataProtocol(DSProtocol.GETPARAMS);
	    
	    this.setOperationBindings(fetch);
	    
	    // i18n
        final DataSourceIntegerField idField = new DataSourceIntegerField(GroupRecord.ID, "ID");  
        idField.setPrimaryKey(true);
        idField.setCanEdit(false);  
        final DataSourceTextField nameDSField = new DataSourceTextField(GroupRecord.NAME, "Name");
        final DataSourceIntegerField parentIdDSField = new DataSourceIntegerField(GroupRecord.PARENT_ID, null);
        parentIdDSField.setForeignKey(GroupRecord.ID);     
        
	    this.setFields(idField, nameDSField, parentIdDSField);  
	    this.setFetchDataURL("/weblab/administration/json/groups");
	    this.setUpdateDataURL("/weblab/administration/json/groups");
	}
}
