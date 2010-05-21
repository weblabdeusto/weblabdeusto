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
import java.util.Calendar;
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
import es.deusto.weblab.client.dto.experiments.ExperimentUse;
import es.deusto.weblab.client.dto.users.Group;
import es.deusto.weblab.client.dto.users.Role;
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
	public ArrayList<Experiment> getExperiments() {
		// Temporal Fake
		ArrayList<Experiment> experiments = new ArrayList<Experiment>();
		experiments.add(new Experiment("ud-fpga", new Category("FPGA experiments"), new Date(), new Date()));
		experiments.add(new Experiment("ud-pld", new Category("PLD experiments"), new Date(), new Date()));
		experiments.add(new Experiment("ud-logic", new Category("PIC experiments"), new Date(), new Date()));
		return experiments;
	}

	@Override
	public ArrayList<Group> getGroups() {
		// Temporal Fake
		ArrayList<Group> groups = new ArrayList<Group>();
		groups.add(new Group("Course 2009/10", null));
		groups.add(new Group("Telecomunications", groups.get(0)));
		groups.add(new Group("Mechatronics", groups.get(0)));
		return groups;
	}

	@Override
	public ArrayList<ExperimentUse> getExperimentUses(Date fromDate, Date toDate, Group group, Experiment experiment) {
		// Temporal Fake
		ArrayList<ExperimentUse> allExperimentUses = new ArrayList<ExperimentUse>();		
		
		allExperimentUses.add(new ExperimentUse(
				new User("jaime.irurzun", "Jaime Irurzun", "jaime.irurzun@opendeusto.es", new Role("student")),
				new Experiment("ud-fpga", new Category("FPGA experiments"), new Date(), new Date()),
				new Date(2010-1900, 04, 17, 15, 00, 00), new Date(2010-1900, 04, 17, 15, 00, 30))
		);
		allExperimentUses.add(new ExperimentUse(
				new User("pablo.orduna", "Pablo Orduña", "pablo.ordunya@opendeusto.es", new Role("student")),
				new Experiment("ud-fpga", new Category("FPGA experiments"), new Date(), new Date()),
				new Date(2010-1900, 04, 18, 15, 00, 00), new Date(2010-1900, 04, 18, 15, 00, 15))
		);
		allExperimentUses.add(new ExperimentUse(
				new User("jaime.irurzun", "Jaime Irurzun", "jaime.irurzun@opendeusto.es", new Role("student")),
				new Experiment("ud-pld", new Category("PLD experiments"), new Date(), new Date()),
				new Date(2010-1900, 04, 20, 15, 00, 00), new Date(2010-1900, 04, 20, 15, 00, 25))
		);
		
		ArrayList<ExperimentUse> experimentUses = new ArrayList<ExperimentUse>();
		
		if ( fromDate != null && toDate != null ) {
			for ( ExperimentUse eu: allExperimentUses ) {
				if ( eu.getStartTimestamp().after(fromDate) && eu.getStartTimestamp().before(toDate) ) {
					experimentUses.add(eu);
				}
			}
		} else if ( fromDate == null && toDate == null ) {
			experimentUses.addAll(allExperimentUses);
		} else if ( fromDate == null ) {
			for ( ExperimentUse eu: allExperimentUses ) {
				if ( eu.getStartTimestamp().before(toDate) ) {
					experimentUses.add(eu);
				}
			}			
		} else if ( toDate == null ) {
			for ( ExperimentUse eu: allExperimentUses ) {
				if ( eu.getStartTimestamp().after(fromDate) ) {
					experimentUses.add(eu);
				}
			}			
		}
		
		return experimentUses;
	}
}