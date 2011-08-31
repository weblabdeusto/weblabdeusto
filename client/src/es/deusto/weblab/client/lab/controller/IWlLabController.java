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
*
*/ 
package es.deusto.weblab.client.lab.controller;

import es.deusto.weblab.client.dto.SessionID;
import es.deusto.weblab.client.dto.experiments.Command;
import es.deusto.weblab.client.dto.experiments.ExperimentAllowed;
import es.deusto.weblab.client.dto.experiments.ExperimentID;
import es.deusto.weblab.client.lab.comm.UploadStructure;
import es.deusto.weblab.client.lab.comm.callbacks.IResponseCommandCallback;
import es.deusto.weblab.client.lab.ui.IUIManager;

public interface IWlLabController {
	public void login(String username, String password);
	public void startLoggedIn(SessionID sessionId);
	public boolean startedLoggedIn();
	public void logout();
	
	public void setUIManager(IUIManager uimanager);
	
	public void retrieveAllowedExperiments();
	public void loadUserHomeWindow();
	public void chooseExperiment(ExperimentAllowed experiment);
	public void reserveExperiment(ExperimentID experiment);
	
	public void sendCommand(Command command, IResponseCommandCallback callback);
	public void sendFile(UploadStructure uploadStructure, IResponseCommandCallback callback);
	
	public void sendAsyncCommand(Command command, IResponseCommandCallback callback);
	public void sendAsyncFile(UploadStructure uploadStructure, IResponseCommandCallback callback);
	
	public void finishReservation();
	public void finishReservationAndLogout();
	
	public void poll();
}
