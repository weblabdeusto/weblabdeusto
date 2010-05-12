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
* Author: FILLME
*
*/

package es.deusto.weblab.client.admin.controller;

import es.deusto.weblab.client.admin.comm.IWlAdminCommunication;
import es.deusto.weblab.client.admin.ui.IUIManager;
import es.deusto.weblab.client.admin.ui.WlAdminThemeBase;
import es.deusto.weblab.client.configuration.ConfigurationManager;
import es.deusto.weblab.client.configuration.IConfigurationManager;
import es.deusto.weblab.client.dto.SessionID;

public class WlAdminController implements IWlAdminController {

	private IConfigurationManager configurationManager;
	private IWlAdminCommunication communications;
	private IUIManager uimanager;
	private SessionID currentSession;

	public WlAdminController(ConfigurationManager configurationManager, IWlAdminCommunication communications) {
		this.configurationManager = configurationManager;
		this.communications = communications;
	}

	@Override
	public void setUIManager(WlAdminThemeBase uimanager) {
		this.uimanager = uimanager;
	}

	@Override
	public void startLoggedIn(SessionID sessionID) {
		this.startSession(sessionID);
	}

	private void startSession(SessionID sessionID) {
		this.currentSession = sessionID;
		
		/*this.communications.getUserInformation(this.currentSession, new IUserInformationCallback(){
			public void onSuccess(final User userInformation) {
				WlLabController.this.uimanager.onLoggedIn(userInformation);
			}
			
			public void onFailure(WlCommException e) {
				WlLabController.this.uimanager.onError(e.getMessage());
			}
		});	*/			
	}

}