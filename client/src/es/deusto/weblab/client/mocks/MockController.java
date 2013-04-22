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
* Author: Pablo Orduña <pablo@ordunya.com>
*
*/ 
package es.deusto.weblab.client.mocks;

import com.google.gwt.user.client.Timer;

import es.deusto.weblab.client.dto.SessionID;
import es.deusto.weblab.client.dto.experiments.Category;
import es.deusto.weblab.client.dto.experiments.Command;
import es.deusto.weblab.client.dto.experiments.Experiment;
import es.deusto.weblab.client.dto.experiments.ExperimentAllowed;
import es.deusto.weblab.client.dto.experiments.ExperimentID;
import es.deusto.weblab.client.dto.reservations.WaitingConfirmationReservationStatus;
import es.deusto.weblab.client.dto.reservations.WaitingReservationStatus;
import es.deusto.weblab.client.dto.users.Role;
import es.deusto.weblab.client.dto.users.User;
import es.deusto.weblab.client.lab.comm.UploadStructure;
import es.deusto.weblab.client.lab.comm.callbacks.IResponseCommandCallback;
import es.deusto.weblab.client.lab.controller.ILabController;
import es.deusto.weblab.client.lab.controller.IValidSessionCallback;
import es.deusto.weblab.client.lab.experiments.exceptions.ExperimentException;
import es.deusto.weblab.client.lab.ui.IUIManager;

public class MockController implements ILabController {

	private String reservationId;
	private IUIManager uimanager;
	private int n;
	
	@Override
	public void setUIManager(IUIManager uimanager){
		this.uimanager = uimanager;
	}

	@Override
	public void login(String username, String password) {
		final User user = new User(username, username + "full name", "weblab@deusto.es", new Role("student"), "");
		this.uimanager.onLoggedIn(user);
	}

	@Override
	public void startLoggedIn(SessionID sessionId, boolean externallyLoggedIn) {
		final User user = new User("tester", "tester full name", "weblab@deusto.es", new Role("student"), "");
	    this.uimanager.onLoggedIn(user);
	}
	
	@Override
	public boolean startedLoggedIn(){
		return false;
	}

	@Override
	public boolean startedReserved(){
		return false;
	}

	@Override
	public void retrieveAllowedExperiments() {
	    final Category category = new Category("PLD experiments");
		final Experiment experiment = new Experiment(-1, "pld-deusto", category, null, null);
		final ExperimentAllowed experimentAllowed = new ExperimentAllowed(experiment, 100);
		
		this.uimanager.setAllowedExperiments(new ExperimentAllowed[] {experimentAllowed});
		this.uimanager.onAllowedExperimentsRetrieved(new ExperimentAllowed[] {experimentAllowed});
	}

	@Override
	public void chooseExperiment(ExperimentAllowed experimentAllowed) {
	}
	
	@Override
	public void reserveExperiment(ExperimentID experimentId) {
		this.n = 3;
		this.nextWaitingReservationStatus();
	}
	
	@Override
	public void sendAsyncCommand(Command command,
			IResponseCommandCallback callback) {
	}

	@Override
	public void sendAsyncFile(UploadStructure uploadStructure,
			IResponseCommandCallback callback) {
	}	

	@Override
	public void sendFile(UploadStructure uploadStructure,
		IResponseCommandCallback callback) {
	}

	@Override
	public void sendCommand(Command command, IResponseCommandCallback callback) {
	}

	@Override
	public void poll() {
	}

	@Override
	public void finishReservation() {
		// TODO This one is important
	}

	@Override
	public void finishReservationAndLogout() {
		
	}
	
	@Override
	public void logout() {
		this.uimanager.onInit();
	}

	private void nextWaitingReservationStatus(){
		final WaitingReservationStatus waitingReservation = new WaitingReservationStatus("foo");
		waitingReservation.setPosition(this.n);
		this.uimanager.onWaitingReservation(waitingReservation);
		if(--this.n >= 0){
			final Timer t = new Timer(){
				@Override
				public void run(){
					MockController.this.nextWaitingReservationStatus();
				}
			};
			t.schedule(500);
		}else{
			final WaitingConfirmationReservationStatus confirmationReservation = new WaitingConfirmationReservationStatus("foo");
			this.uimanager.onWaitingReservationConfirmation(confirmationReservation);
			final Timer t = new Timer(){
				@Override
				public void run(){
					MockController.this.afterShowingWaitingConfirmation();
				}
			};
			t.schedule(500);
		}
	}
	
	private void afterShowingWaitingConfirmation(){
		final ExperimentID experimentID = new ExperimentID();
		experimentID.setCategory(new Category("PLD experiments"));
		experimentID.setExperimentName("pld-deusto");
		
		try {
			this.uimanager.onExperimentReserved(experimentID, null);
		} catch (final ExperimentException e) {
			e.printStackTrace();
			return;
		}
		this.uimanager.onMessage("Programming device...");
		final Timer t = new Timer(){
			@Override
			public void run(){
				MockController.this.uimanager.onMessage("Ready to serve");
			}
		};
		t.schedule(600);
	}

	@Override
	public void loadUserHomeWindow() {
	}

	@Override
	public void setReservationId(String reservationId) {
		this.reservationId = reservationId;
	}

	@Override
	public SessionID getReservationId() {
		return new SessionID(this.reservationId);
	}

	@Override
	public void startReserved(SessionID sessionId, ExperimentID experimentId) {
	}

	@Override
	public void cleanExperimentPanel() {
		loadUserHomeWindow();
	}

	@Override
	public void removeReservationId() {
		this.reservationId = null;
	}

	@Override
	public boolean isExperimentReserved() {
		return this.reservationId != null;
	}

	@Override
	public void checkSessionIdStillValid(SessionID sessionId,
			IValidSessionCallback callback) {
		callback.sessionRejected();
	}

	@Override
	public void disableFinishOnClose() {
	}

	@Override
	public void stopPolling() {
		// TODO Auto-generated method stub
		
	}
}
