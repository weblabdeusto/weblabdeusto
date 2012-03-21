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
import com.smartgwt.client.data.fields.DataSourceTextField;
import com.smartgwt.client.types.DSOperationType;
import com.smartgwt.client.types.DSProtocol;

import es.deusto.weblab.client.configuration.IConfigurationManager;
import es.deusto.weblab.client.dto.SessionID;


public class UsersDataSource extends WebLabRestDataSource {

	public UsersDataSource(SessionID sessionId, IConfigurationManager configurationManager) {
		super(sessionId, configurationManager);
	}
	
	@Override
	public void initialize() {
		
	    final OperationBinding fetch = new OperationBinding();  
	    fetch.setOperationType(DSOperationType.FETCH);  
	    fetch.setDataProtocol(DSProtocol.GETPARAMS);
	    
	    final OperationBinding update = new OperationBinding();
	    update.setOperationType(DSOperationType.UPDATE);
	    update.setDataProtocol(DSProtocol.GETPARAMS);
	    
	    final OperationBinding remove = new OperationBinding();
	    remove.setOperationType(DSOperationType.REMOVE);
	    remove.setDataProtocol(DSProtocol.GETPARAMS);
	    
	    final OperationBinding add = new OperationBinding();
	    add.setOperationType(DSOperationType.ADD);
	    add.setDataProtocol(DSProtocol.GETPARAMS);
	    
	    this.setOperationBindings(fetch, update, remove, add);
	    
	    // TODO: Get rid of hard-coded strings.
	    final DataSourceTextField loginDSField = new DataSourceTextField("login", "Login");
	    loginDSField.setPrimaryKey(true);
	    loginDSField.setCanEdit(false);
	    final DataSourceTextField fullNameDSField = new DataSourceTextField("full_name", "Full Name");
	    final DataSourceTextField emailDSField = new DataSourceTextField("email", "E-Mail");
	    final DataSourceTextField avatarDSField = new DataSourceTextField("avatar", "Avatar");
	    final DataSourceTextField roleIdDSField = new DataSourceTextField("role", "Role");
	    
	    this.setFields(loginDSField, fullNameDSField, emailDSField, avatarDSField, roleIdDSField);
	    
	    this.setFetchDataURL(this.baseLocation + "/weblab/administration/json/users");
	    //this.setFetchDataURL("data/users_fetch.js");
	    this.setRemoveDataURL("data/user_remove.js");
	    this.setAddDataURL("data/user_add.js");
	    this.setUpdateDataURL("data/user_update.js");
	}
}
