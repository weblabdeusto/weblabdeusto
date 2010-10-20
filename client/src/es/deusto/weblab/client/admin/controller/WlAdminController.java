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

import es.deusto.weblab.client.admin.comm.IWlAdminCommunication;
import es.deusto.weblab.client.admin.comm.callbacks.IPermissionsCallback;
import es.deusto.weblab.client.admin.ui.IUIManager;
import es.deusto.weblab.client.comm.callbacks.ISessionIdCallback;
import es.deusto.weblab.client.comm.callbacks.IUserInformationCallback;
import es.deusto.weblab.client.comm.callbacks.IVoidCallback;
import es.deusto.weblab.client.comm.exceptions.WlCommException;
import es.deusto.weblab.client.comm.exceptions.login.LoginException;
import es.deusto.weblab.client.configuration.IConfigurationManager;
import es.deusto.weblab.client.dto.SessionID;
import es.deusto.weblab.client.dto.users.Permission;
import es.deusto.weblab.client.dto.users.User;

public class WlAdminController implements IWlAdminController {

	@SuppressWarnings("unused")
	private final IConfigurationManager configurationManager;
	private final IWlAdminCommunication communications;
	private IUIManager uimanager;
	private SessionID currentSession;
	
	public WlAdminController(IConfigurationManager configurationManager, IWlAdminCommunication communications) {
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
				WlAdminController.this.startSession(sessionId);
			}

			@Override
			public void onFailure(WlCommException e) {
				if(e instanceof LoginException){
					WlAdminController.this.uimanager.onWrongLoginOrPasswordGiven();
				}else{
					WlAdminController.this.uimanager.onErrorAndFinishSession(e.getMessage());
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
				WlAdminController.this.uimanager.onLoggedOut();
			}
			
			@Override
			public void onFailure(WlCommException e) {
				WlAdminController.this.uimanager.onErrorAndFinishSession(e.getMessage());
			}
		});
	}

	private void startSession(SessionID sessionID) {
		this.currentSession = sessionID;
		
		this.communications.getUserPermissions(this.currentSession, new IPermissionsCallback() {
			
			@Override
			public void onSuccess(Permission[] permissions) {
				if ( WlAdminController.this.hasAdminPanelAccessPermission(permissions) ) {
					WlAdminController.this.communications.getUserInformation(WlAdminController.this.currentSession, new IUserInformationCallback(){
						@Override
						public void onSuccess(final User userInformation) {
							WlAdminController.this.uimanager.onLoggedIn(userInformation, WlAdminController.this.currentSession);
						}
						
						@Override
						public void onFailure(WlCommException e) {
							WlAdminController.this.uimanager.onError(e.getMessage());
						}
					});					
				} else {
					WlAdminController.this.uimanager.onNotAllowedToAccessAdminPanel();
				}
			}
			
			@Override
			public void onFailure(WlCommException e) {
				WlAdminController.this.uimanager.onError(e.getMessage());
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