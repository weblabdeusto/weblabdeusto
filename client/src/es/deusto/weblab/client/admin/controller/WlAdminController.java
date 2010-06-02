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

import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.Date;

import es.deusto.weblab.client.admin.comm.IWlAdminCommunication;
import es.deusto.weblab.client.admin.comm.callbacks.IGroupsCallback;
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
import es.deusto.weblab.client.dto.experiments.Experiment;
import es.deusto.weblab.client.dto.experiments.ExperimentUse;
import es.deusto.weblab.client.dto.users.Group;
import es.deusto.weblab.client.dto.users.User;

public class WlAdminController implements IWlAdminController {

	private IConfigurationManager configurationManager;
	private IWlAdminCommunication communications;
	private IUIManager uimanager;
	private SessionID currentSession;
	private TemporalFakeData temporalFakeData;
	
	public WlAdminController(ConfigurationManager configurationManager, IWlAdminCommunication communications) {
		this.configurationManager = configurationManager;
		this.communications = communications;
		this.temporalFakeData = new TemporalFakeData();
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
	public ArrayList<Experiment> getExperiments() {
		return this.temporalFakeData.experiments;
	}

	@Override
	public void getGroups() {
		WlAdminController.this.uimanager.onGroupsRetrieved(this.temporalFakeData.groups);
		/*
		this.communications.getGroups(this.currentSession, new IGroupsCallback(){
			public void onSuccess(final ArrayList<Group> groups) {
				WlAdminController.this.uimanager.onGroupsRetrieved(groups);
			}
			
			public void onFailure(WlCommException e) {
				WlAdminController.this.uimanager.onError(e.getMessage());
			}
		});
		*/	
	}

	@Override
	public ArrayList<ExperimentUse> getExperimentUses(Date fromDate, Date toDate, Group group, Experiment experiment) {
		
		ArrayList<ExperimentUse> experimentUses = new ArrayList<ExperimentUse>();
		
		for ( ExperimentUse eu: this.temporalFakeData.allExperimentUses ) {
			boolean valid = true;
			
			if ( fromDate != null && toDate != null ) {
				if ( ! ( eu.getStartTimestamp().after(fromDate) && eu.getStartTimestamp().before(toDate) ) ) {
					valid = false;
				}
			} else if ( fromDate == null && toDate != null ) {
				if ( ! eu.getStartTimestamp().before(toDate) ) {
					valid = false;
				}
			} else if ( toDate == null && fromDate != null ) {
				if ( ! eu.getStartTimestamp().after(fromDate) ) {
					valid = false;
				}
			}
			
			if ( group != null ) {
				if ( ! eu.getUser().isMemberOf(group) ) {
					valid = false;
				}
			}
			
			if ( experiment != null ) {
				if ( ! eu.getExperiment().equals(experiment) ) {
					valid = false;
				}
			}
			
			if ( valid ) {
				experimentUses.add(eu);
			}
		}
		
		Collections.sort(experimentUses, new Comparator<ExperimentUse>() {
			@Override
			public int compare(ExperimentUse o1, ExperimentUse o2) {
				return o2.getStartTimestamp().compareTo(o1.getStartTimestamp());
			}
		});
		
		return experimentUses;
	}
}