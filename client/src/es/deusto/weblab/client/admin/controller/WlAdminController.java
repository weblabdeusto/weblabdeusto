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

import java.util.Date;

import es.deusto.weblab.client.admin.comm.IWlAdminCommunication;
import es.deusto.weblab.client.admin.ui.IUIManager;
import es.deusto.weblab.client.admin.ui.WlAdminThemeBase;
import es.deusto.weblab.client.comm.callbacks.ISessionIdCallback;
import es.deusto.weblab.client.comm.callbacks.IUserInformationCallback;
import es.deusto.weblab.client.comm.callbacks.IVoidCallback;
import es.deusto.weblab.client.comm.exceptions.WlCommException;
import es.deusto.weblab.client.comm.exceptions.login.LoginException;
import es.deusto.weblab.client.configuration.ConfigurationManager;
import es.deusto.weblab.client.configuration.IConfigurationManager;
import es.deusto.weblab.client.dto.SessionID;
import es.deusto.weblab.client.dto.experiments.Category;
import es.deusto.weblab.client.dto.experiments.Experiment;
import es.deusto.weblab.client.dto.users.Group;
import es.deusto.weblab.client.dto.users.User;

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
	public void login(String username, String password) {
		this.communications.login(username, password, new ISessionIdCallback(){
			public void onSuccess(SessionID sessionId) {
				WlAdminController.this.startSession(sessionId);
			}

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
			public void onSuccess() {
				WlAdminController.this.uimanager.onLoggedOut();
			}
			
			public void onFailure(WlCommException e) {
				WlAdminController.this.uimanager.onErrorAndFinishSession(e.getMessage());
			}
		});
	}

	private void startSession(SessionID sessionID) {
		this.currentSession = sessionID;
		
		this.communications.getUserInformation(this.currentSession, new IUserInformationCallback(){
			public void onSuccess(final User userInformation) {
				WlAdminController.this.uimanager.onLoggedIn(userInformation);
			}
			
			public void onFailure(WlCommException e) {
				WlAdminController.this.uimanager.onError(e.getMessage());
			}
		});			
	}

	@Override
	public Experiment[] getExperiments() {
		// Temporal Fake
		Experiment[] experiments = new Experiment[3];
		experiments[0] = new Experiment("ud-fpga", new Category("FPGA experiments"), new Date(), new Date());
		experiments[1] = new Experiment("ud-pld", new Category("PLD experiments"), new Date(), new Date());
		experiments[2] = new Experiment("ud-logic", new Category("PIC experiments"), new Date(), new Date());
		return experiments;
	}

	@Override
	public Group[] getGroups() {
		// Temporal Fake
		Group[] groups = new Group[3];
		groups[0] = new Group("Course 2009/10", null);
		groups[1] = new Group("Telecomunications", groups[0]);
		groups[2] = new Group("Mechatronics", groups[0]);
		return groups;
	}
}