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
import es.deusto.weblab.client.dto.experiments.ResponseCommand;
import es.deusto.weblab.client.dto.experiments.commands.ArrayOfInterchangedData;
import es.deusto.weblab.client.dto.experiments.commands.InterchangedData;
import es.deusto.weblab.client.dto.users.User;
import es.deusto.weblab.client.lab.comm.IWlLabCommunication;
import es.deusto.weblab.client.lab.comm.UploadStructure;
import es.deusto.weblab.client.lab.comm.callbacks.IExperimentsAllowedCallback;
import es.deusto.weblab.client.lab.comm.callbacks.IResponseCommandCallback;
import es.deusto.weblab.client.lab.comm.exceptions.NoCurrentReservationException;
import es.deusto.weblab.client.lab.experiments.ExperimentBase;
import es.deusto.weblab.client.lab.experiments.ExperimentFactory;
import es.deusto.weblab.client.lab.experiments.ExperimentBase.IBoardBaseController;
import es.deusto.weblab.client.lab.experiments.ExperimentFactory.IExperimentLoadedCallback;
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
		
		this.communications.reserveExperiment(this.currentSession, experimentId, new ArrayOfInterchangedData(new InterchangedData[]{}), reservationStatusCallback);
	}

	@Override
	public void finishReservation() {
		this.communications.finishedExperiment(this.currentSession, new IVoidCallback(){
			@Override
			public void onSuccess(){
				WlLabController.this.cleanReservation();
				// TODO: Cancelling State, it should "poll" somehow
				// TODO: If the user is in any queue and clicks "finish", he'll be in this state 
			}
			@Override
			public void onFailure(WlCommException e) {
				WlLabController.this.cleanReservation();
//				WlLabController.this.uimanager.onErrorAndFinishReservation(e.getMessage());
			}
		});
	}

	@Override
	public void finishReservationAndLogout(){
		this.communications.finishedExperiment(this.currentSession, new IVoidCallback(){
			@Override
			public void onSuccess(){
				WlLabController.this.cleanReservation();
				// TODO: Cancelling State, it should "poll" somehow
				// TODO: If the user is in any queue and clicks "finish", he'll be in this state 
				WlLabController.this.logout();
			}
			@Override
			public void onFailure(WlCommException e) {
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
							// XXX: tell experiment that it has finished
						}else{
							WlLabController.this.uimanager.onErrorAndFinishReservation(e.getMessage());
							WlLabController.this.finishReservation();
						}
					}
				}
			);
	}

	@Override
	public void chooseExperiment(final ExperimentAllowed experimentAllowed) {
	    final IBoardBaseController boardBaseController = new IBoardBaseController(){
	    	@Override
	    	public boolean isFacebook(){
	    		return WlLabController.this.isFacebook;
	    	}
	    	
	    	@Override
	    	public SessionID getSessionId(){
	    		return WlLabController.this.currentSession;
	    	}
	    	
	    	@Override
		public void onClean(){
	    		WlLabController.this.finishReservation();
	    	}
	    	
	    	// Ignore the callback
	    	@Override
			public void sendCommand(Command command){
	    	    WlLabController.this.sendCommand(command, new IResponseCommandCallback(){
	    		@Override
				public void onSuccess(
	    			ResponseCommand responseCommand) {
	    		    // nothing
	    		}

	    		@Override
				public void onFailure(WlCommException e) {
	    		    WlLabController.this.uimanager.onError("Error sending command: " + e.getMessage());
	    		}
	    	    });
	    	}
	    	
	    	@Override
	    	public void sendCommand(final String command){
	    		sendCommand(new Command() {
					@Override
					public String getCommandString() {
						return command;
					}
				});
	    	}

	    	@Override
	    	public void sendCommand(final String command, IResponseCommandCallback callback){
	    		sendCommand(new Command() {
					@Override
					public String getCommandString() {
						return command;
					}
				}, callback);
	    	}

	    	@Override
			public void sendCommand(Command command, IResponseCommandCallback callback) {
	    	    WlLabController.this.sendCommand(command, callback);
	    	}

		@Override
		public void sendFile(UploadStructure uploadStructure,
			IResponseCommandCallback callback) {
		    WlLabController.this.sendFile(uploadStructure, callback);
		    
		}
		
		@Override
		public void sendAsyncFile(UploadStructure uploadStructure,
				IResponseCommandCallback callback) {
			WlLabController.this.sendAsyncFile(uploadStructure, callback);
		}

		@Override
		public void sendAsyncCommand(Command command) {
    	    WlLabController.this.sendAsyncCommand(command, new IResponseCommandCallback(){
	    		@Override
				public void onSuccess(
	    			ResponseCommand responseCommand) {
	    		    // nothing
	    		}

	    		@Override
				public void onFailure(WlCommException e) {
	    		    WlLabController.this.uimanager.onError("Error sending async command: " + e.getMessage());
	    		}
	    	    });
		}

		@Override
		public void sendAsyncCommand(Command command,
				IResponseCommandCallback callback) {
			WlLabController.this.sendAsyncCommand(command, callback);
		}

		@Override
		public void sendAsyncCommand(final String command) {
    		sendAsyncCommand(new Command() {
				@Override
				public String getCommandString() {
					return command;
				}
			});
		}

		@Override
		public void sendAsyncCommand(final String command,
				IResponseCommandCallback callback) {
    		sendCommand(new Command() {
				@Override
				public String getCommandString() {
					return command;
				}
			}, callback);
		}
	    };
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
			}
		};
	    factory.experimentFactory(experimentAllowed.getExperiment().getExperimentUniqueName(), experimentLoadedCallback, this.isMobile);
	}

	@Override
	public void cleanReservation() {
	    this.pollingHandler.stop();
	    this.uimanager.onReservationFinished();
	}
}
