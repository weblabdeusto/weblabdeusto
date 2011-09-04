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

import es.deusto.weblab.client.admin.comm.IAdminCommunication;
import es.deusto.weblab.client.admin.comm.callbacks.IPermissionsCallback;
import es.deusto.weblab.client.admin.ui.IUIManager;
import es.deusto.weblab.client.comm.callbacks.ISessionIdCallback;
import es.deusto.weblab.client.comm.callbacks.IUserInformationCallback;
import es.deusto.weblab.client.comm.callbacks.IVoidCallback;
import es.deusto.weblab.client.comm.exceptions.CommException;
import es.deusto.weblab.client.comm.exceptions.login.LoginException;
import es.deusto.weblab.client.configuration.IConfigurationManager;
import es.deusto.weblab.client.dto.SessionID;
import es.deusto.weblab.client.dto.users.Permission;
import es.deusto.weblab.client.dto.users.User;

public class AdminController implements IAdminController {

	@SuppressWarnings("unused")
	private final IConfigurationManager configurationManager;
	private final IAdminCommunication communications;
	private IUIManager uimanager;
	private SessionID currentSession;
	
	public AdminController(IConfigurationManager configurationManager, IAdminCommunication communications) {
		this.configurationManager = configurationManager;
		this.communications = communications;
	}

	@Override
	public void setUIManager(IUIManager uimanager) {
		this.uimanager = uimanager;
	}

	@Override
	public void login(String username, String password) {
		this.communications.login(username, password, new ISessionIdCallback(){
			@Override
			public void onSuccess(SessionID sessionId) {
				AdminController.this.startSession(sessionId);
			}

			@Override
			public void onFailure(CommException e) {
				if(e instanceof LoginException){
					AdminController.this.uimanager.onWrongLoginOrPasswordGiven();
				}else{
					AdminController.this.uimanager.onErrorAndFinishSession(e.getMessage());
				}
			}
		});
	}

	@Override
	public void startLoggedIn(SessionID sessionID) {
		this.startSession(sessionID);
	}

	@Override
	public void logout() {
		this.communications.logout(this.currentSession, new IVoidCallback(){
			@Override
			public void onSuccess() {
				AdminController.this.uimanager.onLoggedOut();
			}
			
			@Override
			public void onFailure(CommException e) {
				AdminController.this.uimanager.onErrorAndFinishSession(e.getMessage());
			}
		});
	}

	private void startSession(SessionID sessionID) {
		this.currentSession = sessionID;
		
		this.communications.getUserPermissions(this.currentSession, new IPermissionsCallback() {
			
			@Override
			public void onSuccess(Permission[] permissions) {
				if ( AdminController.this.hasAdminPanelAccessPermission(permissions) ) {
					AdminController.this.communications.getUserInformation(AdminController.this.currentSession, new IUserInformationCallback(){
						@Override
						public void onSuccess(final User userInformation) {
							AdminController.this.uimanager.onLoggedIn(userInformation, AdminController.this.currentSession);
						}
						
						@Override
						public void onFailure(CommException e) {
							AdminController.this.uimanager.onError(e.getMessage());
						}
					});					
				} else {
					AdminController.this.uimanager.onNotAllowedToAccessAdminPanel();
				}
			}
			
			@Override
			public void onFailure(CommException e) {
				AdminController.this.uimanager.onError(e.getMessage());
			}			
		});					
	}
	
	private boolean hasAdminPanelAccessPermission(Permission[] permissions) {
		for ( Permission p: permissions ) {
			if ( p.getName().equals("admin_panel_access") )
				return true;
		}
		return false;
	}
}