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
* Author: Pablo Orduña <pablo@ordunya.com>
*         Jaime Irurzun <jaime.irurzun@gmail.com>
*
*/

package es.deusto.weblab.client.admin.controller;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import junit.framework.Assert;

import com.google.gwt.junit.client.GWTTestCase;

import es.deusto.weblab.client.admin.comm.FakeWlAdminCommunication;
import es.deusto.weblab.client.admin.comm.callbacks.IPermissionsCallback;
import es.deusto.weblab.client.admin.ui.FakeUIManager;
import es.deusto.weblab.client.comm.FakeWlCommonCommunication;
import es.deusto.weblab.client.comm.callbacks.ISessionIdCallback;
import es.deusto.weblab.client.comm.callbacks.IUserInformationCallback;
import es.deusto.weblab.client.comm.callbacks.IVoidCallback;
import es.deusto.weblab.client.comm.exceptions.WlCommException;
import es.deusto.weblab.client.comm.exceptions.login.LoginException;
import es.deusto.weblab.client.configuration.FakeConfiguration;
import es.deusto.weblab.client.configuration.IConfigurationManager;
import es.deusto.weblab.client.dto.SessionID;
import es.deusto.weblab.client.dto.users.Permission;
import es.deusto.weblab.client.dto.users.PermissionParameter;
import es.deusto.weblab.client.dto.users.Role;
import es.deusto.weblab.client.dto.users.User;
import es.deusto.weblab.client.testing.util.WlFake.Methods;

public class WlAdminControllerTest  extends GWTTestCase {
	
	private IConfigurationManager configurationManager;
	private FakeWlAdminCommunication fakeCommunications;
	private FakeUIManager fakeUIManager;
	
	public void testLoginFailure() throws Exception{
		final WlAdminController controller = this.createController();
		controller.login("whatever", "whatever");
		
		List<Methods> v = this.fakeCommunications.getMethodByName(FakeWlCommonCommunication.LOGIN);
		Assert.assertEquals(1, v.size());
		final Methods m = v.get(0);
		final Object [] parametersReceived = m.getParameters();
		Assert.assertEquals(3, parametersReceived.length);
		final ISessionIdCallback callback = (ISessionIdCallback)parametersReceived[2];
		
		callback.onFailure(new LoginException("WRONG!"));
		v = this.fakeUIManager.getMethodByName(FakeUIManager.ON_WRONG_LOGIN_OR_PASSWORD_GIVEN);
		Assert.assertEquals(1, v.size());
		
		callback.onFailure(new WlCommException("other error"));
		v = this.fakeUIManager.getMethodByName(FakeUIManager.ON_ERROR_AND_FINISH_SESSION);
		Assert.assertEquals(1, v.size());
	}
	
	public void testLoginSucceeded() throws Exception{
		final User user = new User("porduna", "Pablo Orduña Fernández", "porduna@tecnologico.deusto.es", new Role("student"));
		final Permission [] permissions = new Permission[1];
		final PermissionParameter[] parameters = new PermissionParameter[1];
		parameters[0] = new PermissionParameter("full_privileges", "bool", "1");
		permissions[0] = new Permission("admin_panel_access", parameters);
		
		final WlAdminController controller = this.createController();
		
		// login
		controller.login("whatever", "whatever");
		List<Methods> v = this.fakeCommunications.getMethodByName(FakeWlCommonCommunication.LOGIN);
		Assert.assertEquals(1, v.size());
		Methods m = v.get(0);
		final Object [] parametersReceived = m.getParameters();
		Assert.assertEquals(3, parametersReceived.length);
		final ISessionIdCallback sessionIdCallback = (ISessionIdCallback)parametersReceived[2];
		final SessionID sessionID = new SessionID("your session!");

		sessionIdCallback.onSuccess(sessionID);
		v = this.fakeCommunications.getMethodByName(FakeWlAdminCommunication.GET_USER_PERMISSIONS);
		Assert.assertEquals(1, v.size());		
		m = v.get(0);
		Assert.assertEquals(2, m.getParameters().length);
		Assert.assertEquals(sessionID, m.getParameters()[0]);
		final IPermissionsCallback permissionsCallback = (IPermissionsCallback)m.getParameters()[1];

		permissionsCallback.onSuccess(permissions);
		v = this.fakeCommunications.getMethodByName(FakeWlCommonCommunication.GET_USER_INFORMATION);
		Assert.assertEquals(1, v.size());		
		m = v.get(0);
		Assert.assertEquals(2, m.getParameters().length);
		Assert.assertEquals(sessionID, m.getParameters()[0]);
		final IUserInformationCallback userInformationCallback = (IUserInformationCallback)m.getParameters()[1];
		
		userInformationCallback.onSuccess(user);
		v = this.fakeUIManager.getMethodByName(FakeUIManager.ON_LOGGED_IN);
		Assert.assertEquals(1, v.size());
		
		// logout
		controller.logout();		
		v = this.fakeCommunications.getMethodByName(FakeWlCommonCommunication.LOGOUT);
		Assert.assertEquals(1,v.size());
		m = v.get(0);
		Assert.assertEquals(2,m.getParameters().length);
		Assert.assertEquals(sessionID,m.getParameters()[0]);		
		final IVoidCallback voidCallback = (IVoidCallback)m.getParameters()[1];
		
    		// failure
    		voidCallback.onFailure(new WlCommException("haw haw"));
    		// Was called in the previous "test failure"
    		Assert.assertEquals(1,this.fakeUIManager.getMethodByName(FakeUIManager.ON_ERROR_AND_FINISH_SESSION).size());
    		
    		// success
    		voidCallback.onSuccess();
    		Assert.assertEquals(1,this.fakeUIManager.getMethodByName(FakeUIManager.ON_LOGGED_OUT).size());
	}
	
	public void testLoginSucceededButNotAllowedToAccess() throws Exception{
		final Permission [] permissions = new Permission[1];
		final PermissionParameter[] parameters = new PermissionParameter[3];
		parameters[0] = new PermissionParameter("experiment_name", "string", "ud-fpga");
		parameters[1] = new PermissionParameter("experiment_cat", "string", "FPGA experiments");
		parameters[2] = new PermissionParameter("time_allowed", "float", "300");
		permissions[0] = new Permission("experiment_allowed", parameters);
		
		final WlAdminController controller = this.createController();
		
		// login
		controller.login("whatever", "whatever");
		List<Methods> v = this.fakeCommunications.getMethodByName(FakeWlCommonCommunication.LOGIN);
		Assert.assertEquals(1, v.size());
		Methods m = v.get(0);
		final Object [] parametersReceived = m.getParameters();
		Assert.assertEquals(3, parametersReceived.length);
		final ISessionIdCallback sessionIdCallback = (ISessionIdCallback)parametersReceived[2];
		final SessionID sessionID = new SessionID("your session!");

		sessionIdCallback.onSuccess(sessionID);
		v = this.fakeCommunications.getMethodByName(FakeWlAdminCommunication.GET_USER_PERMISSIONS);
		Assert.assertEquals(1, v.size());		
		m = v.get(0);
		Assert.assertEquals(2, m.getParameters().length);
		Assert.assertEquals(sessionID, m.getParameters()[0]);
		final IPermissionsCallback permissionsCallback = (IPermissionsCallback)m.getParameters()[1];

		permissionsCallback.onSuccess(permissions);
		v = this.fakeUIManager.getMethodByName(FakeUIManager.ON_NOT_ALLOWED_TO_ACCESS_ADMIN_PANEL);
		Assert.assertEquals(1, v.size());
		
		// logout
		controller.logout();		
		v = this.fakeCommunications.getMethodByName(FakeWlCommonCommunication.LOGOUT);
		Assert.assertEquals(1,v.size());
		m = v.get(0);
		Assert.assertEquals(2,m.getParameters().length);
		Assert.assertEquals(sessionID,m.getParameters()[0]);		
		final IVoidCallback voidCallback = (IVoidCallback)m.getParameters()[1];
		
    		// failure
    		voidCallback.onFailure(new WlCommException("haw haw"));
    		// Was called in the previous "test failure"
    		Assert.assertEquals(1,this.fakeUIManager.getMethodByName(FakeUIManager.ON_ERROR_AND_FINISH_SESSION).size());
    		
    		// success
    		voidCallback.onSuccess();
    		Assert.assertEquals(1,this.fakeUIManager.getMethodByName(FakeUIManager.ON_LOGGED_OUT).size());
	}	
	
	/*
	 * Auxiliar methods
	 */
	
	private Map<String, String> createConfiguration(){
		final Map<String, String> map = new HashMap<String, String>();
		return map;
	}
	
	private FakeWebLabController createController() {
		this.configurationManager = new FakeConfiguration(this.createConfiguration());
		this.fakeCommunications = new FakeWlAdminCommunication();
		this.fakeUIManager = new FakeUIManager();
			
		final FakeWebLabController controller = new FakeWebLabController(
				this.configurationManager,
				this.fakeCommunications,
				this.fakeUIManager
			);
		return controller;
	}
		
	/*
	 * Auxiliar structures and classes
	 */
	
	@Override
	public String getModuleName() {
		return "es.deusto.weblab.WebLabClient";
	}
		
	private class FakeWebLabController extends WlAdminController{
		
	    public FakeWebLabController( IConfigurationManager configurationManager, FakeWlAdminCommunication fakeCommunications, FakeUIManager fakeUIManager) {
			super(configurationManager, fakeCommunications);
			this.setUIManager(fakeUIManager);
		}
	}
}