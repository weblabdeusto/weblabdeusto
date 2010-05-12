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

//TODO: current reportMessages are not good at all :-(
//TODO: translations

import com.google.gwt.core.client.GWT;
import com.google.gwt.user.client.Timer;

import es.deusto.weblab.client.comm.callbacks.ISessionIdCallback;
import es.deusto.weblab.client.comm.callbacks.IUserInformationCallback;
import es.deusto.weblab.client.comm.callbacks.IVoidCallback;
import es.deusto.weblab.client.comm.exceptions.WlCommException;
import es.deusto.weblab.client.comm.exceptions.login.LoginException;
import es.deusto.weblab.client.configuration.IConfigurationManager;
import es.deusto.weblab.client.dto.SessionID;
import es.deusto.weblab.client.dto.experiments.Command;
import es.deusto.weblab.client.dto.experiments.ExperimentAllowed;
import es.deusto.weblab.client.dto.experiments.ExperimentID;
import es.deusto.weblab.client.dto.experiments.ResponseCommand;
import es.deusto.weblab.client.dto.users.User;
import es.deusto.weblab.client.lab.comm.IWlLabCommunication;
import es.deusto.weblab.client.lab.comm.UploadStructure;
import es.deusto.weblab.client.lab.comm.callbacks.IExperimentsAllowedCallback;
import es.deusto.weblab.client.lab.comm.callbacks.IResponseCommandCallback;
import es.deusto.weblab.client.lab.experiments.ExperimentBase;
import es.deusto.weblab.client.lab.experiments.ExperimentFactory;
import es.deusto.weblab.client.lab.experiments.ExperimentFactory.IExperimentLoadedCallback;
import es.deusto.weblab.client.lab.ui.IUIManager;
import es.deusto.weblab.client.lab.ui.BoardBase.IBoardBaseController;

public class WlLabController implements IWlLabController {
	
	// Constants
	public static final String WAITING_INSTANCES_MIN_POLLING_TIME_PROPERTY = "polling.time.waitinginstances.min";
	public static final String WAITING_INSTANCES_MAX_POLLING_TIME_PROPERTY = "polling.time.waitinginstances.max";
	public static final String WAITING_CONFIRMATION_POLLING_TIME_PROPERTY = "polling.time.waitingconfirmation";
	public static final String WAITING_MIN_POLLING_TIME_PROPERTY = "polling.time.waiting.min";
	public static final String WAITING_MAX_POLLING_TIME_PROPERTY = "polling.time.waiting.max";
	
	public static final int DEFAULT_WAITING_MIN_POLLING_TIME = 1000;
	public static final int DEFAULT_WAITING_MAX_POLLING_TIME = 10 * 1000;
	public static final int DEFAULT_WAITING_INSTANCES_MIN_POLLING_TIME = 1000;
	public static final int DEFAULT_WAITING_INSTANCES_MAX_POLLING_TIME = 10 * 1000;
	public static final int DEFAULT_WAITING_CONFIRMATION_POLLING_TIME = 1200;

	// These two constants are specially useful while debugging the application
	public static final boolean REPORT_BIG_ERROR_ON_STATE_FAILURE = true;
	public static final boolean RETURN_ON_STATE_FAILURE = true;

	// Managers
	private final IConfigurationManager configurationManager;
	private final IWlLabCommunication communications;
	private IUIManager uimanager;
	
	// Current session variables
	private SessionID currentSession;
	private final IPollingHandler pollingHandler;
	private boolean isUsingExperiment = false;
	
	// TODO: QUICK FIX TO INTEGRATE TINY VISIR
	private ExperimentID lastExperiment;
	
	private class SessionVariables {
		private ExperimentBase currentExperimentBase;
		
		public void setCurrentExperimentBase(ExperimentBase currentExperimentBase) {
		    this.currentExperimentBase = currentExperimentBase;
		}
		public ExperimentBase getCurrentExperimentBase() {
		    return this.currentExperimentBase;
		}
	}
	
	private final SessionVariables     sessionVariables = new SessionVariables();
	private final boolean              isMobile;
	
	public WlLabController(
				IConfigurationManager configurationManager,
				IWlLabCommunication  communications,
				IPollingHandler       pollingHandler,
				boolean               isMobile
			){
		this.configurationManager = configurationManager;
		this.communications       = communications;
		this.pollingHandler       = pollingHandler;
		this.isMobile             = isMobile;
	}
	
	private class ExtendedTimer extends Timer{
		IControllerRunnable runnable;
		public ExtendedTimer(IControllerRunnable runnable){
			super();
			this.runnable = runnable;
		}
		@Override
		public void run() {
			this.runnable.run();
		}
	}
	
	protected void createTimer(int millis, IControllerRunnable runnable){
		final Timer timer = new ExtendedTimer(runnable);
		timer.schedule(millis);
	}
	
	public interface IControllerRunnable{
		public void run();
	}
	
	public void setUIManager(IUIManager uimanager){
		this.uimanager = uimanager;
	}
	
	public boolean isUsingExperiment() {
	    return this.isUsingExperiment;
	}

	public void setUsingExperiment(boolean isUsingExperiment) {
	    this.isUsingExperiment = isUsingExperiment;
	}	

	public class TimerCreator{
		public void createTimer(int millis, IControllerRunnable runnable){
			WlLabController.this.createTimer(millis, runnable);
		}
	}
	
	private void startSession(SessionID sessionID){
		this.currentSession = sessionID;
		
		this.communications.getUserInformation(this.currentSession, new IUserInformationCallback(){
			public void onSuccess(final User userInformation) {
				WlLabController.this.uimanager.onLoggedIn(userInformation);
			}
			
			public void onFailure(WlCommException e) {
				WlLabController.this.uimanager.onError(e.getMessage());
			}
		});		
	}	
	
	@Override
	public void login(String username, String password){
		this.communications.login(username, password, new ISessionIdCallback(){
			public void onSuccess(SessionID sessionId) {
				WlLabController.this.startSession(sessionId);
			}

			public void onFailure(WlCommException e) {
				if(e instanceof LoginException){
					WlLabController.this.uimanager.onWrongLoginOrPasswordGiven();
				}else{
					WlLabController.this.uimanager.onErrorAndFinishSession(e.getMessage());
				}
			}
		});
	}

	@Override
	public void startLoggedIn(SessionID sessionId){
		WlLabController.this.startSession(sessionId);
	}

	@Override
	public void logout(){
		this.communications.logout(this.currentSession, new IVoidCallback(){
			public void onSuccess() {
				WlLabController.this.uimanager.onLoggedOut();
			}
			
			public void onFailure(WlCommException e) {
				WlLabController.this.uimanager.onErrorAndFinishSession(e.getMessage());
			}
		});
	}

	@Override
	public void retrieveAllowedExperiments() {
		WlLabController.this.communications.listExperiments(WlLabController.this.currentSession, new IExperimentsAllowedCallback(){
			public void onSuccess(ExperimentAllowed[] experimentsAllowed) {
				WlLabController.this.uimanager.onAllowedExperimentsRetrieved(experimentsAllowed);
			}
			
			public void onFailure(WlCommException e) {
				WlLabController.this.uimanager.onError(e.getMessage());
			}
		});	    
	}

	@Override
	public void reserveExperiment(ExperimentID experimentId){
		// We delegate the reservation on the ReservationHandler class 
		final ReservationStatusCallback reservationStatusCallback = new ReservationStatusCallback();
		
		// Set the different parameters
		reservationStatusCallback.setTimerCreator(new TimerCreator());
		reservationStatusCallback.setUimanager(this.uimanager);
		reservationStatusCallback.setConfigurationManager(this.configurationManager);
		reservationStatusCallback.setPollingHandler(this.pollingHandler);
		reservationStatusCallback.setSessionID(this.currentSession);
		reservationStatusCallback.setExperimentBeingReserved(experimentId);
		reservationStatusCallback.setCommunications(this.communications);
		reservationStatusCallback.setController(this);
		reservationStatusCallback.setExperimentBaseBeingReserved(this.sessionVariables.getCurrentExperimentBase());
		
		this.lastExperiment = experimentId;//TODO: remove this line TINY VISIR

		this.communications.reserveExperiment(this.currentSession, experimentId, reservationStatusCallback);
	}

	@Override
	public void finishReservation() {
		this.communications.finishedExperiment(this.currentSession, new IVoidCallback(){
			public void onSuccess(){
				WlLabController.this.cleanReservation();
				// TODO: Cancelling State, it should "poll" somehow
				// TODO: If the user is in any queue and clicks "finish", he'll be in this state 
			}
			public void onFailure(WlCommException e) {
				WlLabController.this.uimanager.onErrorAndFinishReservation(e.getMessage());
			}
		});
	}

	@Override
	public void finishReservationAndLogout(){
		this.communications.finishedExperiment(this.currentSession, new IVoidCallback(){
			public void onSuccess(){
				WlLabController.this.cleanReservation();
				// TODO: Cancelling State, it should "poll" somehow
				// TODO: If the user is in any queue and clicks "finish", he'll be in this state 
				WlLabController.this.logout();
			}
			public void onFailure(WlCommException e) {
				WlLabController.this.uimanager.onErrorAndFinishReservation(e.getMessage());
			}
		});
	}

	@Override
	public void sendCommand(Command command, IResponseCommandCallback callback) {
		this.communications.sendCommand(this.currentSession, command, callback);
	}

	@Override
	public void sendFile(UploadStructure uploadStructure, IResponseCommandCallback callback) {
	    GWT.log("sendFile en communications", null);
		this.communications.sendFile(this.currentSession, uploadStructure, callback);
	}

	@Override
	public void poll(){
		this.communications.poll(
				this.currentSession, 
				new IVoidCallback(){
					public void onSuccess() {
						// Nothing to do
					}
					public void onFailure(WlCommException e) {
						if(WlLabController.this.lastExperiment != null && WlLabController.this.lastExperiment.getExperimentName().equals("ud-visir"))
							return;
						
						// TODO: 
						WlLabController.this.uimanager.onErrorAndFinishReservation(e.getMessage());
						WlLabController.this.finishReservation();
					}
				}
			);
	}

	@Override
	public void chooseExperiment(final ExperimentAllowed experimentAllowed) {
	    IBoardBaseController boardBaseController = new IBoardBaseController(){
	    	public void onClean(){
	    		WlLabController.this.finishReservation();
	    	}
	    	
	    	// Ignore the callback
	    	public void sendCommand(Command command){
	    	    WlLabController.this.sendCommand(command, new IResponseCommandCallback(){
	    		public void onSuccess(
	    			ResponseCommand responseCommand) {
	    		    // nothing
	    		}

	    		public void onFailure(WlCommException e) {
	    		    WlLabController.this.uimanager.onError("Error sending command: " + e.getMessage());
	    		}
	    	    });
	    	}

	    	public void sendCommand(Command command,
	    		IResponseCommandCallback callback) {
	    	    WlLabController.this.sendCommand(command, callback);
	    	}

		public void sendFile(UploadStructure uploadStructure,
			IResponseCommandCallback callback) {
		    WlLabController.this.sendFile(uploadStructure, callback);
		    
		}
	    };
	    final ExperimentFactory factory = new ExperimentFactory(this.configurationManager, boardBaseController);
	    final IExperimentLoadedCallback experimentLoadedCallback = new IExperimentLoadedCallback() {
			
			@Override
			public void onFailure(Throwable e) {
				WlLabController.this.uimanager.onError("Couldn't instantiate experiment: " + e.getMessage());
				e.printStackTrace();
			}
			
			@Override
			public void onExperimentLoaded(ExperimentBase experimentBase) {
				WlLabController.this.sessionVariables.setCurrentExperimentBase(experimentBase);
				WlLabController.this.uimanager.onExperimentChosen(experimentAllowed, experimentBase);
			}
		};
	    factory.experimentFactory(experimentAllowed.getExperiment().getExperimentID(), experimentLoadedCallback, this.isMobile);
	}

	public void cleanReservation() {
	    this.pollingHandler.stop();
	    this.uimanager.onReservationFinished();
	}
}