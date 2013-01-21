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
* 		  Luis Rodriguez <luis.rodriguez@opendeusto.es>
*
*/ 
package es.deusto.weblab.client.lab.controller;

//TODO: current reportMessages are not good at all :-(
//TODO: translations

import java.util.Date;
import java.util.HashMap;
import java.util.Map;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.logical.shared.ValueChangeEvent;
import com.google.gwt.event.logical.shared.ValueChangeHandler;
import com.google.gwt.json.client.JSONValue;
import com.google.gwt.user.client.Cookies;
import com.google.gwt.user.client.History;
import com.google.gwt.user.client.Timer;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.Window.ClosingEvent;
import com.google.gwt.user.client.Window.ClosingHandler;

import es.deusto.weblab.client.HistoryProperties;
import es.deusto.weblab.client.WebLabLabLoader;
import es.deusto.weblab.client.comm.callbacks.ISessionIdCallback;
import es.deusto.weblab.client.comm.callbacks.IUserInformationCallback;
import es.deusto.weblab.client.comm.callbacks.IVoidCallback;
import es.deusto.weblab.client.comm.exceptions.CommException;
import es.deusto.weblab.client.comm.exceptions.core.SessionNotFoundException;
import es.deusto.weblab.client.comm.exceptions.login.LoginException;
import es.deusto.weblab.client.configuration.IConfigurationManager;
import es.deusto.weblab.client.dto.NullSessionID;
import es.deusto.weblab.client.dto.SessionID;
import es.deusto.weblab.client.dto.experiments.Command;
import es.deusto.weblab.client.dto.experiments.Experiment;
import es.deusto.weblab.client.dto.experiments.ExperimentAllowed;
import es.deusto.weblab.client.dto.experiments.ExperimentID;
import es.deusto.weblab.client.dto.reservations.ConfirmedReservationStatus;
import es.deusto.weblab.client.dto.reservations.PostReservationReservationStatus;
import es.deusto.weblab.client.dto.reservations.ReservationStatus;
import es.deusto.weblab.client.dto.users.User;
import es.deusto.weblab.client.lab.comm.ILabCommunication;
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

public class LabController implements ILabController {
	
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
	public static final int DEFAULT_WAITING_CONFIRMATION_POLLING_TIME = 400;

	// These two constants are specially useful while debugging the application
	public static final boolean REPORT_BIG_ERROR_ON_STATE_FAILURE = true;
	public static final boolean RETURN_ON_STATE_FAILURE = true;

	// Managers
	private final IConfigurationManager configurationManager;
	private final ILabCommunication communications;
	private IUIManager uimanager;
	
	// Current session variables
	private SessionID currentSession;
	private final IPollingHandler pollingHandler;
	private ExperimentAllowed[] experimentsAllowed;
	
	private boolean externallyLoggedIn = false;
	private boolean externallyReserved = false;
	private boolean finishOnClose = true;
	
	private class SessionVariables {
		private ExperimentBase currentExperimentBase;
		private boolean experimentVisible = false;
		private SessionID reservationId = new NullSessionID();
		
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
		
		public void setReservationId(String reservationId) {
			this.reservationId = new SessionID(reservationId);
		}
		
		public void removeReservationId() {
			this.reservationId = new NullSessionID();
		}
		
		public SessionID getReservationId(){
			return this.reservationId;
		}
	}
	
	private final SessionVariables     sessionVariables = new SessionVariables();
	private final boolean              isMobile;
	private final boolean              isFacebook;
	
	public LabController(
				IConfigurationManager configurationManager,
				ILabCommunication  communications,
				IPollingHandler       pollingHandler,
				boolean               isMobile,
				boolean               isFacebook
			){
		this.configurationManager = configurationManager;
		this.communications       = communications;
		this.pollingHandler       = pollingHandler;
		this.isMobile             = isMobile;
		this.isFacebook           = isFacebook;
		
		Window.addWindowClosingHandler(new ClosingHandler() {
			@Override
			public void onWindowClosing(ClosingEvent event) {
				onWindowClose();
			}
		});
		
		History.addValueChangeHandler(new ValueChangeHandler<String>() {
			
			@Override
			public void onValueChange(ValueChangeEvent<String> event) {
				if(getCurrentSession() != null && !getCurrentSession().isNull()) {
					HistoryProperties.reloadHistory();
					loadUserHomeWindow();
				}
			}
		});
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
	
	public class TimerCreator{
		public void createTimer(int millis, IControllerRunnable runnable){
			LabController.this.createTimer(millis, runnable);
		}
	}
	
	@Override
	public void checkSessionIdStillValid(SessionID sessionId, final IValidSessionCallback callback) {
		this.communications.getUserInformation(sessionId, new IUserInformationCallback() {
			
			@Override
			public void onFailure(CommException e) {
				callback.sessionRejected();
			}
			
			@Override
			public void onSuccess(User userInformation) {
				callback.sessionConfirmed();
			}
		});
	}
	
	@Override
	public void setReservationId(String reservationId){
		this.sessionVariables.setReservationId(reservationId);
	}
	
	@Override
	public void removeReservationId(){
		this.sessionVariables.removeReservationId();
	}
	
	@Override
	public SessionID getReservationId(){
		return this.sessionVariables.getReservationId();
	}
	
	@Override
	public boolean isExperimentReserved() {
		return !this.sessionVariables.getReservationId().isNull();
	}
	
	private void startSession(SessionID sessionID){
		this.currentSession = sessionID;
		
		this.communications.getUserInformation(this.currentSession, new IUserInformationCallback(){
			@Override
			public void onSuccess(final User userInformation) {
				LabController.this.uimanager.onLoggedIn(userInformation);
			}
			
			@Override
			public void onFailure(CommException e) {
				LabController.this.uimanager.onError(e.getMessage());
			}
		});		
	}	
	
	@Override
	public void login(String username, String password){
		this.communications.login(username, password, new ISessionIdCallback(){
			@Override
			public void onSuccess(SessionID sessionId) {
				LabController.this.startSession(sessionId);
			}

			@Override
			public void onFailure(CommException e) {
				if(e instanceof LoginException){
					LabController.this.uimanager.onWrongLoginOrPasswordGiven();
				}else{
					LabController.this.uimanager.onErrorAndFinishSession(e.getMessage());
				}
			}
		});
	}

	@Override
	public void startLoggedIn(SessionID sessionId, boolean externallyLoggedIn){
		this.externallyLoggedIn = externallyLoggedIn;
		this.startSession(sessionId);
	}
	
	@Override
	public void startReserved(final SessionID reservationId, final ExperimentID experimentId){
		this.externallyLoggedIn = true;
		this.externallyReserved = true;
		
		this.currentSession = null;
		setReservationId(reservationId.getRealId());
		
		final IBoardBaseController boardBaseController = new BoardBaseController(this);
	    final ExperimentFactory factory = new ExperimentFactory(boardBaseController);
	    final IExperimentLoadedCallback experimentLoadedCallback = new IExperimentLoadedCallback() {
			
			@Override
			public void onFailure(Throwable e) {
				LabController.this.uimanager.onError("Couldn't instantiate experiment: " + e.getMessage());
				e.printStackTrace();
			}
			
			@Override
			public void onExperimentLoaded(ExperimentBase experimentBase) {
				// Show the experiment
				LabController.this.sessionVariables.setCurrentExperimentBase(experimentBase);
				final ExperimentAllowed defaultExperimentAllowed = new ExperimentAllowed(new Experiment(0, experimentId.getExperimentName(), experimentId.getCategory(), new Date(), new Date()), 100);
				LabController.this.uimanager.onExperimentChosen(defaultExperimentAllowed, experimentBase, true);
				experimentBase.initializeReserved();
				LabController.this.sessionVariables.showExperiment();
				
				// And start in the queue
				final ReservationStatusCallback reservationStatusCallback = createReservationStatusCallback(experimentId);
				LabController.this.communications.getReservationStatus(reservationId, reservationStatusCallback);
			}
		};
	    factory.experimentFactory(experimentId, experimentLoadedCallback, this.isMobile);
	}
	
	@Override
	public boolean startedLoggedIn(){
		return this.externallyLoggedIn;
	}

	@Override
	public boolean startedReserved(){
		return this.externallyReserved;
	}

	@Override
	public void logout(){
		this.communications.logout(this.currentSession, new IVoidCallback(){
			@Override
			public void onSuccess() {
				// Sometimes stored with different paths
				Cookies.removeCookie(WebLabLabLoader.LOGIN_WEBLAB_SESSION_ID_COOKIE);
				Cookies.removeCookie(WebLabLabLoader.LOGIN_WEBLAB_SESSION_ID_COOKIE);
				Cookies.removeCookie(WebLabLabLoader.WEBLAB_SESSION_ID_COOKIE);
				Cookies.removeCookie(WebLabLabLoader.WEBLAB_SESSION_ID_COOKIE);
				LabController.this.uimanager.onLoggedOut();
			}
			
			@Override
			public void onFailure(CommException e) {
				// Sometimes stored with different paths
				Cookies.removeCookie(WebLabLabLoader.LOGIN_WEBLAB_SESSION_ID_COOKIE);
				Cookies.removeCookie(WebLabLabLoader.LOGIN_WEBLAB_SESSION_ID_COOKIE);
				Cookies.removeCookie(WebLabLabLoader.WEBLAB_SESSION_ID_COOKIE);
				Cookies.removeCookie(WebLabLabLoader.WEBLAB_SESSION_ID_COOKIE);
				LabController.this.sessionVariables.hideExperiment();
				LabController.this.uimanager.onErrorAndFinishSession(e.getMessage());
			}
		});
	}

	@Override
	public void retrieveAllowedExperiments() {
		LabController.this.communications.listExperiments(LabController.this.currentSession, new IExperimentsAllowedCallback(){
			@Override
			public void onSuccess(ExperimentAllowed[] experimentsAllowed) {
				LabController.this.experimentsAllowed = experimentsAllowed;
				loadUserHomeWindow();
			}
			
			@Override
			public void onFailure(CommException e) {
				LabController.this.uimanager.onError(e.getMessage());
			}
		});	    
	}
	
	@Override
	public void loadUserHomeWindow(){
		this.uimanager.setAllowedExperiments(this.experimentsAllowed);
		
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
		
		HistoryProperties.setValue(HistoryProperties.PAGE, HistoryProperties.HOME);
		
		this.uimanager.onAllowedExperimentsRetrieved(this.experimentsAllowed);
	}
	
	@Override
	public void cleanExperimentPanel(){
		if(!this.externallyLoggedIn){
			loadUserHomeWindow();
		}else{
			this.uimanager.onExperimentInteractionFinished();
		}
	}

	@Override
	public void reserveExperiment(ExperimentID experimentId){
		final ReservationStatusCallback reservationStatusCallback = createReservationStatusCallback(experimentId);

		final JSONValue initialData = this.sessionVariables.getCurrentExperimentBase().getInitialData();
		this.communications.reserveExperiment(this.currentSession, experimentId, initialData, reservationStatusCallback);
	}

	private ReservationStatusCallback createReservationStatusCallback(ExperimentID experimentId) {
		// We delegate the reservation on the ReservationHandler class 
		final ReservationStatusCallback reservationStatusCallback = new ReservationStatusCallback();
		
		// Set the different parameters
		reservationStatusCallback.setTimerCreator(new TimerCreator());
		reservationStatusCallback.setUimanager(this.uimanager);
		reservationStatusCallback.setConfigurationManager(this.configurationManager);
		reservationStatusCallback.setPollingHandler(this.pollingHandler);
		reservationStatusCallback.setExperimentBeingReserved(experimentId);
		reservationStatusCallback.setCommunications(this.communications);
		reservationStatusCallback.setController(this);
		reservationStatusCallback.setExperimentBaseBeingReserved(this.sessionVariables.getCurrentExperimentBase());
		return reservationStatusCallback;
	}
	
	final IReservationCallback postReservationDataCallback = new IReservationCallback() {

		private void onError(String message){
			LabController.this.sessionVariables.hideExperiment();
			LabController.this.uimanager.onCleanReservation();
			LabController.this.uimanager.onError(message);
		}
		
		@Override
		public void onFailure(CommException e) {
			onError(e.getMessage());
			e.printStackTrace();
		}
		
		@Override
		public void onSuccess(ReservationStatus reservation) {
			if(!LabController.this.sessionVariables.isExperimentVisible())
				return;
			
			if(reservation instanceof PostReservationReservationStatus){
				final PostReservationReservationStatus status = (PostReservationReservationStatus)reservation;
				if(status.isFinished()){
					LabController.this.sessionVariables.getCurrentExperimentBase().postEndWrapper(status.getInitialData(), status.getEndData());
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
		this.communications.getReservationStatus(this.sessionVariables.getReservationId(), this.postReservationDataCallback);
	}

	private void onWindowClose() {
		if(isExperimentReserved() && this.finishOnClose) {
			this.communications.finishedExperiment(this.sessionVariables.getReservationId(), new IVoidCallback(){
				@Override
				public void onFailure(CommException e) { }

				@Override
				public void onSuccess() { }
			});
		}
	}
	
	@Override
	public void disableFinishOnClose() {
		this.finishOnClose = false;
	}

	@Override
	public void finishReservation() {
		this.pollingHandler.stop();
		this.sessionVariables.getCurrentExperimentBase().endWrapper();
		
		this.communications.finishedExperiment(this.sessionVariables.getReservationId(), new IVoidCallback(){
			
			@Override
			public void onSuccess(){
				if(LabController.this.sessionVariables.getCurrentExperimentBase().expectsPostEnd()
						&& LabController.this.sessionVariables.isExperimentVisible()){
					
					pollForPostReservationData();
					
				}else{
					System.out.println("expects post end?" + LabController.this.sessionVariables.getCurrentExperimentBase().expectsPostEnd());
					System.out.println("is experiment visible?" + LabController.this.sessionVariables.isExperimentVisible());
					LabController.this.sessionVariables.hideExperiment();
					LabController.this.uimanager.onCleanReservation();
				}
			}
			
			@Override
			public void onFailure(CommException e) {
				LabController.this.sessionVariables.hideExperiment();
				LabController.this.uimanager.onCleanReservation();
				LabController.this.uimanager.onError(e.getMessage());
				e.printStackTrace();
			}
		});
	}
	
	public void cleanExperiment() {
		
		this.pollingHandler.stop();
		this.sessionVariables.getCurrentExperimentBase().endWrapper();
		
		this.communications.finishedExperiment(this.sessionVariables.getReservationId(), new IVoidCallback(){
			@Override
			public void onSuccess(){
				LabController.this.sessionVariables.hideExperiment();
				LabController.this.uimanager.onCleanReservation();
			}
			@Override
			public void onFailure(CommException e) {
				LabController.this.sessionVariables.hideExperiment();
				LabController.this.uimanager.onCleanReservation();
			}
		});
	}

	@Override
	public void finishReservationAndLogout(){
		
		this.pollingHandler.stop();
		this.sessionVariables.getCurrentExperimentBase().endWrapper();
		
		this.communications.finishedExperiment(this.sessionVariables.getReservationId(), new IVoidCallback(){
			@Override
			public void onSuccess(){
				LabController.this.sessionVariables.hideExperiment();
				LabController.this.uimanager.onCleanReservation();
				LabController.this.logout();
			}
			@Override
			public void onFailure(CommException e) {
				LabController.this.sessionVariables.hideExperiment();
				LabController.this.uimanager.onCleanReservation();
				LabController.this.logout();
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
		this.communications.sendAsyncCommand(this.sessionVariables.getReservationId(), command, callback);
	}
	
	/**
	 * Sends a file to be handled asynchronously on the server side.
	 * @param uploadStructure Upload structure describing the file to send
	 * @param callback Callback through which to notify when the request has finished,
	 * which might take a while.
	 */
	@Override
	public void sendAsyncFile(UploadStructure uploadStructure, IResponseCommandCallback callback) {
		this.communications.sendAsyncFile(this.sessionVariables.getReservationId(), uploadStructure, callback);
	}

	/**
	 * Sends a command to be executed synchronously on the server side. Note that this call,
	 * client-side, is still asynchronous.
	 * @param command Command to execute
	 * @param callback Callback through which to notify when the request has finished.
	 */
	@Override
	public void sendCommand(Command command, IResponseCommandCallback callback) {
		this.communications.sendCommand(this.sessionVariables.getReservationId(), command, callback);
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
		this.communications.sendFile(this.sessionVariables.getReservationId(), uploadStructure, callback);
	}

	@Override
	public void poll(){
		this.communications.poll(
				this.sessionVariables.getReservationId(), 
				new IVoidCallback(){
					@Override
					public void onSuccess() {
						// Nothing to do
					}
					
					@Override
					public void onFailure(CommException e) {
						if(e instanceof NoCurrentReservationException){
							LabController.this.finishReservation();
						} else if (e instanceof SessionNotFoundException) {
							LabController.this.finishReservationAndLogout();
						} else {
							LabController.this.sessionVariables.hideExperiment();
							LabController.this.uimanager.onErrorAndFinishReservation(e.getMessage());
							LabController.this.cleanExperiment();
						}
					}
				}
			);
	}

	@Override
	public void chooseExperiment(final ExperimentAllowed experimentAllowed) {
		final Map<String, String> newHistoryValues = new HashMap<String, String>();
		newHistoryValues.put(HistoryProperties.EXPERIMENT_CATEGORY, experimentAllowed.getExperiment().getCategory().getCategory());
		newHistoryValues.put(HistoryProperties.EXPERIMENT_NAME,     experimentAllowed.getExperiment().getName());
		newHistoryValues.put(HistoryProperties.PAGE,                HistoryProperties.EXPERIMENT);
		HistoryProperties.setValues(newHistoryValues);
		
	    final IBoardBaseController boardBaseController = new BoardBaseController(this);
	    final ExperimentFactory factory = new ExperimentFactory(boardBaseController);
	    final IExperimentLoadedCallback experimentLoadedCallback = new IExperimentLoadedCallback() {
			
			@Override
			public void onFailure(Throwable e) {
				LabController.this.uimanager.onError("Couldn't instantiate experiment: " + e.getMessage());
				e.printStackTrace();
			}
			
			@Override
			public void onExperimentLoaded(ExperimentBase experimentBase) {
				LabController.this.sessionVariables.setCurrentExperimentBase(experimentBase);
				LabController.this.uimanager.onExperimentChosen(experimentAllowed, experimentBase, false);
				experimentBase.initialize();
				LabController.this.sessionVariables.showExperiment();
			}
		};
	    factory.experimentFactory(experimentAllowed.getExperiment().getExperimentUniqueName(), experimentLoadedCallback, this.isMobile);
	}

	@Override
	public void stopPolling() {
		this.pollingHandler.stop();
	}
}
