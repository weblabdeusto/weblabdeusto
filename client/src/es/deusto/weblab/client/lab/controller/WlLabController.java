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
* 		  Luis Rodriguez <luis.rodriguez@opendeusto.es>
*
*/ 
package es.deusto.weblab.client.lab.controller;

//TODO: current reportMessages are not good at all :-(
//TODO: translations

import com.google.gwt.core.client.GWT;
import com.google.gwt.json.client.JSONValue;
import com.google.gwt.user.client.Timer;

import es.deusto.weblab.client.HistoryProperties;
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
import es.deusto.weblab.client.dto.reservations.ConfirmedReservationStatus;
import es.deusto.weblab.client.dto.reservations.PostReservationReservationStatus;
import es.deusto.weblab.client.dto.reservations.ReservationStatus;
import es.deusto.weblab.client.dto.users.User;
import es.deusto.weblab.client.lab.comm.IWlLabCommunication;
import es.deusto.weblab.client.lab.comm.UploadStructure;
import es.deusto.weblab.client.lab.comm.callbacks.IExperimentsAllowedCallback;
import es.deusto.weblab.client.lab.comm.callbacks.IReservationCallback;
import es.deusto.weblab.client.lab.comm.callbacks.IResponseCommandCallback;
import es.deusto.weblab.client.lab.comm.exceptions.NoCurrentReservationException;
import es.deusto.weblab.client.lab.experiments.ExperimentBase;
import es.deusto.weblab.client.lab.experiments.ExperimentFactory;
import es.deusto.weblab.client.lab.experiments.ExperimentFactory.IExperimentLoadedCallback;
import es.deusto.weblab.client.lab.experiments.IBoardBaseController;
import es.deusto.weblab.client.lab.ui.IUIManager;

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
	private ExperimentAllowed[] experimentsAllowed;
	
	private boolean loggedIn = false;
	
	private class SessionVariables {
		private ExperimentBase currentExperimentBase;
		private boolean experimentVisible = false;
		
		public void showExperiment(){
			this.experimentVisible = true;
		}
		
		public void hideExperiment(){
			this.experimentVisible = true;
		}
		
		public boolean isExperimentVisible(){
			return this.experimentVisible;
		}
		
		public void setCurrentExperimentBase(ExperimentBase currentExperimentBase) {
		    this.currentExperimentBase = currentExperimentBase;
		}
		public ExperimentBase getCurrentExperimentBase() {
		    return this.currentExperimentBase;
		}
	}
	
	private final SessionVariables     sessionVariables = new SessionVariables();
	private final boolean              isMobile;
	private final boolean              isFacebook;
	
	public WlLabController(
				IConfigurationManager configurationManager,
				IWlLabCommunication  communications,
				IPollingHandler       pollingHandler,
				boolean               isMobile,
				boolean               isFacebook
			){
		this.configurationManager = configurationManager;
		this.communications       = communications;
		this.pollingHandler       = pollingHandler;
		this.isMobile             = isMobile;
		this.isFacebook           = isFacebook;
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
	
	SessionID getCurrentSession(){
		return this.currentSession;
	}
	
	boolean isFacebook(){
		return this.isFacebook;
	}
	
	IUIManager getUIManager(){
		return this.uimanager;
	}
	
	@Override
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
			@Override
			public void onSuccess(final User userInformation) {
				WlLabController.this.uimanager.onLoggedIn(userInformation);
			}
			
			@Override
			public void onFailure(WlCommException e) {
				WlLabController.this.uimanager.onError(e.getMessage());
			}
		});		
	}	
	
	@Override
	public void login(String username, String password){
		this.communications.login(username, password, new ISessionIdCallback(){
			@Override
			public void onSuccess(SessionID sessionId) {
				WlLabController.this.startSession(sessionId);
			}

			@Override
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
		this.loggedIn = true;
		WlLabController.this.startSession(sessionId);
	}
	
	@Override
	public boolean startedLoggedIn(){
		return this.loggedIn;
	}

	@Override
	public void logout(){
		this.communications.logout(this.currentSession, new IVoidCallback(){
			@Override
			public void onSuccess() {
				WlLabController.this.uimanager.onLoggedOut();
			}
			
			@Override
			public void onFailure(WlCommException e) {
				WlLabController.this.sessionVariables.hideExperiment();
				WlLabController.this.uimanager.onErrorAndFinishSession(e.getMessage());
			}
		});
	}

	@Override
	public void retrieveAllowedExperiments() {
		WlLabController.this.communications.listExperiments(WlLabController.this.currentSession, new IExperimentsAllowedCallback(){
			@Override
			public void onSuccess(ExperimentAllowed[] experimentsAllowed) {
				WlLabController.this.experimentsAllowed = experimentsAllowed;
				loadUserHomeWindow();
			}
			
			@Override
			public void onFailure(WlCommException e) {
				WlLabController.this.uimanager.onError(e.getMessage());
			}
		});	    
	}
	
	@Override
	public void loadUserHomeWindow(){
		final String selectedExperimentName     = HistoryProperties.getValue(HistoryProperties.EXPERIMENT_NAME);
		final String selectedExperimentCategory = HistoryProperties.getValue(HistoryProperties.EXPERIMENT_CATEGORY);
		if(selectedExperimentName != null && selectedExperimentCategory != null){
			for(ExperimentAllowed experimentAllowed : this.experimentsAllowed){
				final String currentExperimentAllowedName     = experimentAllowed.getExperiment().getName();
				final String currentExperimentAllowedCategory = experimentAllowed.getExperiment().getCategory().getCategory();
				if(currentExperimentAllowedName.equals(selectedExperimentName) && currentExperimentAllowedCategory.equals(selectedExperimentCategory)){
					chooseExperiment(experimentAllowed);
					return;
				}
			}
		}
		
		WlLabController.this.uimanager.onAllowedExperimentsRetrieved(this.experimentsAllowed);
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

		final JSONValue initialData = this.sessionVariables.getCurrentExperimentBase().getInitialData();
		this.communications.reserveExperiment(this.currentSession, experimentId, initialData, reservationStatusCallback);
	}
	
	final IReservationCallback postReservationDataCallback = new IReservationCallback() {

		private void onError(String message){
			WlLabController.this.sessionVariables.hideExperiment();
			WlLabController.this.uimanager.onCleanReservation();
			WlLabController.this.uimanager.onError(message);
		}
		
		@Override
		public void onFailure(WlCommException e) {
			onError(e.getMessage());
			e.printStackTrace();
		}
		
		@Override
		public void onSuccess(ReservationStatus reservation) {
			if(!WlLabController.this.sessionVariables.isExperimentVisible())
				return;
			
			if(reservation instanceof PostReservationReservationStatus){
				final PostReservationReservationStatus status = (PostReservationReservationStatus)reservation;
				if(status.isFinished()){
					WlLabController.this.sessionVariables.getCurrentExperimentBase().postEnd(status.getInitialData(), status.getEndData());
				}else{
					final Timer t = new Timer() {
						
						@Override
						public void run() {
							pollForPostReservationData();
						}
					};
					t.schedule(200);
				}
			}else if(reservation instanceof ConfirmedReservationStatus){
				final Timer t = new Timer() {
					
					@Override
					public void run() {
						pollForPostReservationData();
					}
				};
				t.schedule(200);
			}else
				this.onError("Unexpected reservation status obtained while waiting for " + PostReservationReservationStatus.class.getName() + ": " + reservation.getClass().getName() + ": " + reservation);
		}
	};
	
	private void pollForPostReservationData(){
		this.communications.getReservationStatus(this.currentSession, this.postReservationDataCallback);
	}

	@Override
	public void finishReservation() {
		this.pollingHandler.stop();
		this.sessionVariables.getCurrentExperimentBase().end();
		
		this.communications.finishedExperiment(this.currentSession, new IVoidCallback(){
			
			@Override
			public void onSuccess(){
				if(WlLabController.this.sessionVariables.getCurrentExperimentBase().expectsPostEnd()
						&& WlLabController.this.sessionVariables.isExperimentVisible()){
					
					pollForPostReservationData();
					
				}else{
					System.out.println("expects post end?" + WlLabController.this.sessionVariables.getCurrentExperimentBase().expectsPostEnd());
					System.out.println("is experiment visible?" + WlLabController.this.sessionVariables.isExperimentVisible());
					WlLabController.this.sessionVariables.hideExperiment();
					WlLabController.this.uimanager.onCleanReservation();
				}
			}
			
			@Override
			public void onFailure(WlCommException e) {
				WlLabController.this.sessionVariables.hideExperiment();
				WlLabController.this.uimanager.onCleanReservation();
				WlLabController.this.uimanager.onError(e.getMessage());
				e.printStackTrace();
			}
		});
	}
	
	public void cleanExperiment() {
		
		this.pollingHandler.stop();
		this.sessionVariables.getCurrentExperimentBase().end();
		
		this.communications.finishedExperiment(this.currentSession, new IVoidCallback(){
			@Override
			public void onSuccess(){
				WlLabController.this.sessionVariables.hideExperiment();
				WlLabController.this.uimanager.onCleanReservation();
			}
			@Override
			public void onFailure(WlCommException e) {
				WlLabController.this.sessionVariables.hideExperiment();
				WlLabController.this.uimanager.onCleanReservation();
			}
		});
	}

	@Override
	public void finishReservationAndLogout(){
		
		this.pollingHandler.stop();
		this.sessionVariables.getCurrentExperimentBase().end();
		
		this.communications.finishedExperiment(this.currentSession, new IVoidCallback(){
			@Override
			public void onSuccess(){
				WlLabController.this.sessionVariables.hideExperiment();
				WlLabController.this.uimanager.onCleanReservation();
				WlLabController.this.logout();
			}
			@Override
			public void onFailure(WlCommException e) {
				WlLabController.this.sessionVariables.hideExperiment();
				WlLabController.this.uimanager.onErrorAndFinishReservation(e.getMessage());
			}
		});
	}
	
	/**
	 * Sends a command to be executed asynchronously on the server side. 
	 * @param  command Command to execute
	 * @param callback Callback through which to notify when the request has finished,
	 * which might take a while.
	 */
	@Override
	public void sendAsyncCommand(Command command, IResponseCommandCallback callback) {
		this.communications.sendAsyncCommand(this.currentSession, command, callback);
	}
	
	/**
	 * Sends a file to be handled asynchronously on the server side.
	 * @param uploadStructure Upload structure describing the file to send
	 * @param callback Callback through which to notify when the request has finished,
	 * which might take a while.
	 */
	@Override
	public void sendAsyncFile(UploadStructure uploadStructure, IResponseCommandCallback callback) {
		this.communications.sendAsyncFile(this.currentSession, uploadStructure, callback);
	}

	/**
	 * Sends a command to be executed synchronously on the server side. Note that this call,
	 * client-side, is still asynchronous.
	 * @param command Command to execute
	 * @param callback Callback through which to notify when the request has finished.
	 */
	@Override
	public void sendCommand(Command command, IResponseCommandCallback callback) {
		this.communications.sendCommand(this.currentSession, command, callback);
	}


	/**
	 * Sends a file to be handled synchronously on the server side. Note that this call,
	 * client-side, is still asynchronous.
	 * @param uploadStructure Upload structure describing the file to send
	 * @param callback Callback through which to notify when the request has finished.
	 */
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
					@Override
					public void onSuccess() {
						// Nothing to do
					}
					
					@Override
					public void onFailure(WlCommException e) {
						if(e instanceof NoCurrentReservationException){
							WlLabController.this.finishReservation();
						}else{
							WlLabController.this.sessionVariables.hideExperiment();
							WlLabController.this.uimanager.onErrorAndFinishReservation(e.getMessage());
							WlLabController.this.cleanExperiment();
						}
					}
				}
			);
	}

	@Override
	public void chooseExperiment(final ExperimentAllowed experimentAllowed) {
	    final IBoardBaseController boardBaseController = new BoardBaseController(this);
	    final ExperimentFactory factory = new ExperimentFactory(boardBaseController);
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
				experimentBase.initialize();
				WlLabController.this.sessionVariables.showExperiment();
			}
		};
	    factory.experimentFactory(experimentAllowed.getExperiment().getExperimentUniqueName(), experimentLoadedCallback, this.isMobile);
	}

}
