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
package es.deusto.weblab.client.comm;

import com.google.gwt.core.client.GWT;
import com.google.gwt.dom.client.Element;
import com.google.gwt.dom.client.InputElement;
import com.google.gwt.http.client.RequestBuilder;
import com.google.gwt.http.client.RequestCallback;
import com.google.gwt.http.client.RequestException;
import com.google.gwt.user.client.DOM;
import com.google.gwt.user.client.ui.FormPanel;
import com.google.gwt.user.client.ui.Hidden;
import com.google.gwt.user.client.ui.FormPanel.SubmitCompleteEvent;
import com.google.gwt.user.client.ui.FormPanel.SubmitCompleteHandler;

import es.deusto.weblab.client.comm.callbacks.IExperimentsAllowedCallback;
import es.deusto.weblab.client.comm.callbacks.IReservationCallback;
import es.deusto.weblab.client.comm.callbacks.IResponseCommandCallback;
import es.deusto.weblab.client.comm.callbacks.ISessionIdCallback;
import es.deusto.weblab.client.comm.callbacks.IUserInformationCallback;
import es.deusto.weblab.client.comm.callbacks.IVoidCallback;
import es.deusto.weblab.client.comm.callbacks.IWlAsyncCallback;
import es.deusto.weblab.client.comm.exceptions.CommunicationException;
import es.deusto.weblab.client.comm.exceptions.SerializationException;
import es.deusto.weblab.client.comm.exceptions.WlCommException;
import es.deusto.weblab.client.comm.exceptions.WlServerException;
import es.deusto.weblab.client.comm.exceptions.login.InvalidCredentialsException;
import es.deusto.weblab.client.comm.exceptions.login.LoginException;
import es.deusto.weblab.client.comm.exceptions.user_processing.SessionNotFoundException;
import es.deusto.weblab.client.comm.exceptions.user_processing.UnknownExperimentIdException;
import es.deusto.weblab.client.configuration.IConfigurationManager;
import es.deusto.weblab.client.dto.SessionID;
import es.deusto.weblab.client.dto.experiments.Command;
import es.deusto.weblab.client.dto.experiments.ExperimentAllowed;
import es.deusto.weblab.client.dto.experiments.ExperimentID;
import es.deusto.weblab.client.dto.experiments.ResponseCommand;
import es.deusto.weblab.client.dto.reservations.ReservationStatus;
import es.deusto.weblab.client.dto.users.User;


public class WebLabCommunication implements IWebLabCommunication {

	public static final String FILE_SENT_ATTR  = "file_sent";
	public static final String SESSION_ID_ATTR = "session_id";
	public static final String FILE_INFO_ATTR  = "file_info"; 

	public static final String WEBLAB_SERVICE_URL_PROPERTY = "weblab.service.url";
	public static final String DEFAULT_WEBLAB_SERVICE_URL = "/weblab/json/";
	public static final String WEBLAB_LOGIN_SERVICE_URL_PROPERTY = "weblab.service.login.url";
	public static final String DEFAULT_WEBLAB_LOGIN_SERVICE_URL = "/weblab/login/json/";
	public static final String WEBLAB_FILE_UPLOAD_POST_SERVICE_URL_PROPERTY = "weblab.service.fileupload.post.url";
	public static final String DEFAULT_WEBLAB_FILE_UPLOAD_POST_SERVICE_URL = "/weblab/fileUpload.py"; 
	
	private IWebLabSerializer serializer;
	private final IConfigurationManager configurationManager;
	
	public WebLabCommunication(IConfigurationManager configurationManager){
		this.configurationManager = configurationManager;
		this.createSerializer();
	}
	
	private String getServiceUrl(){
		return this.configurationManager.getProperty(
					WebLabCommunication.WEBLAB_SERVICE_URL_PROPERTY,
					WebLabCommunication.DEFAULT_WEBLAB_SERVICE_URL
				);
	}
	
	private String getLoginServiceUrl(){
		return this.configurationManager.getProperty(
					WebLabCommunication.WEBLAB_LOGIN_SERVICE_URL_PROPERTY,
					WebLabCommunication.DEFAULT_WEBLAB_LOGIN_SERVICE_URL
				);
	}
	
	private String getFilePostUrl(){
		return this.configurationManager.getProperty(
					WebLabCommunication.WEBLAB_FILE_UPLOAD_POST_SERVICE_URL_PROPERTY, 
					WebLabCommunication.DEFAULT_WEBLAB_FILE_UPLOAD_POST_SERVICE_URL
				);
	}
	
	// For testing purposes
	protected void createSerializer(){
		this.setSerializer(new WebLabSerializerJSON());
	}
	
	protected void setSerializer(IWebLabSerializer serializer){
		this.serializer = serializer;
	}
	
	// For testing purposes
	protected RequestBuilder createRequestBuilder(RequestBuilder.Method method, String url){
		return new RequestBuilder(method, url);
	}
	
	private void performRequest(String requestSerialized,
			IWlAsyncCallback failureCallback, RequestCallback rci){
		final RequestBuilder rb = this.createRequestBuilder(RequestBuilder.POST, this.getServiceUrl());
		try {
			rb.sendRequest(requestSerialized, rci);
		} catch (final RequestException e) {
			failureCallback.onFailure(new CommunicationException(e.getMessage(), e));
		}
	}

	private void performLoginRequest(String requestSerialized,
		IWlAsyncCallback failureCallback, RequestCallback rci) {
        	final RequestBuilder rb = this.createRequestBuilder(RequestBuilder.POST, this.getLoginServiceUrl());
        	try {
        		rb.sendRequest(requestSerialized, rci);
        	} catch (final RequestException e) {
        		failureCallback.onFailure(new CommunicationException(e.getMessage(), e));
        	}
	}


	
	private class ReservationRequestCallback extends WlRequestCallback{
		private final IReservationCallback reservationCallback;
		
		public ReservationRequestCallback(IReservationCallback reservationCallback){
			super(reservationCallback);
			this.reservationCallback = reservationCallback;
		}
		
		@Override
		public void onSuccessResponseReceived(String response) {
			ReservationStatus reservation;
			try {
				reservation = WebLabCommunication.this.serializer.parseGetReservationStatusResponse(response);
			} catch (final SerializationException e) {
				this.reservationCallback.onFailure(e);
				return;
			} catch (final SessionNotFoundException e) {
				this.reservationCallback.onFailure(e);
				return;
			} catch (final WlServerException e) {
				this.reservationCallback.onFailure(e);
				return;
			}
			this.reservationCallback.onSuccess(reservation);
		}
	}
	
	public void getReservationStatus(SessionID sessionId, IReservationCallback callback) {
		String requestSerialized;
		try {
			requestSerialized = this.serializer.serializeGetReservationStatusRequest(sessionId);
		} catch (final SerializationException e1) {
			callback.onFailure(e1);
			return;
		}
		this.performRequest(
				requestSerialized, 
				callback, 
				new ReservationRequestCallback(callback)
			);
	}
	
	private class UserInformationRequestCallback extends WlRequestCallback{
		private final IUserInformationCallback userInformationCallback;
		
		public UserInformationRequestCallback(IUserInformationCallback userInformationCallback){
			super(userInformationCallback);
			this.userInformationCallback = userInformationCallback;
		}
		
		@Override
		public void onSuccessResponseReceived(String response) {
			User user;
			try {
				user = WebLabCommunication.this.serializer.parseGetUserInformationResponse(response);
			} catch (final SerializationException e) {
				this.userInformationCallback.onFailure(e);
				return;
			} catch (final SessionNotFoundException e) {
				this.userInformationCallback.onFailure(e);
				return;
			} catch (final WlServerException e) {
				this.userInformationCallback.onFailure(e);
				return;
			}
			this.userInformationCallback.onSuccess(user);
		}
	}
	
	public void getUserInformation(SessionID sessionId, IUserInformationCallback callback) {
		String requestSerialized;
		try {
			requestSerialized = this.serializer.serializeGetUserInformationRequest(sessionId);
		} catch (final SerializationException e1) {
			callback.onFailure(e1);
			return;
		}
		this.performRequest(
				requestSerialized, 
				callback, 
				new UserInformationRequestCallback(callback)
			);
	}
	
	private class ListExperimentsRequestCallback extends WlRequestCallback{
		private final IExperimentsAllowedCallback experimentsAllowedCallback;
		
		public ListExperimentsRequestCallback(IExperimentsAllowedCallback experimentsAllowedCallback){
			super(experimentsAllowedCallback);
			this.experimentsAllowedCallback = experimentsAllowedCallback;
		}
		
		@Override
		public void onSuccessResponseReceived(String response){
			ExperimentAllowed [] experimentsAllowed;
			try {
				experimentsAllowed = WebLabCommunication.this.serializer.parseListExperimentsResponse(response);
			} catch (final SerializationException e) {
				this.experimentsAllowedCallback.onFailure(e);
				return;
			} catch (final SessionNotFoundException e) {
				this.experimentsAllowedCallback.onFailure(e);
				return;
			} catch (final WlServerException e) {
				this.experimentsAllowedCallback.onFailure(e);
				return;
			}
			this.experimentsAllowedCallback.onSuccess(experimentsAllowed);
		}
	}
	
	public void listExperiments(SessionID sessionId, IExperimentsAllowedCallback callback) {
		String requestSerialized;
		try {
			requestSerialized = this.serializer.serializeListExperimentsRequest(sessionId);
		} catch (final SerializationException e1) {
			callback.onFailure(e1);
			return;
		}
		this.performRequest(
				requestSerialized, 
				callback, 
				new ListExperimentsRequestCallback(callback)
			);
	}

	private class LoginRequestCallback extends WlRequestCallback{
		private final ISessionIdCallback sessionIdCallback;
		private final String username;
		private final String password;
		
		public LoginRequestCallback(ISessionIdCallback sessionIdCallback, String username, String password){
			super(sessionIdCallback);
			this.sessionIdCallback = sessionIdCallback;
			this.username = username;
			this.password = password;
		}
		
		@Override
		public void onSuccessResponseReceived(String response) {
			SessionID sessionId;
			try {
				sessionId = WebLabCommunication.this.serializer.parseLoginResponse(response);
			} catch (final SerializationException e) {
				this.sessionIdCallback.onFailure(e);
				return;
			} catch (final InvalidCredentialsException e) {
				this.sessionIdCallback.onFailure(e);
				return;
			} catch (final LoginException e) {
				this.sessionIdCallback.onFailure(e);
				return;
			} catch (final WlServerException e) {
				this.sessionIdCallback.onFailure(e);
				return;
			}
			this.launchBrowserPasswordManager();
			this.sessionIdCallback.onSuccess(sessionId);
		}

		private void launchBrowserPasswordManager() {
			final Element usernameField = DOM.getElementById("hiddenUsername");
			final Element passwordField = DOM.getElementById("hiddenPassword");
			final Element submitField  = DOM.getElementById("hiddenLoginFormSubmitButton");
			
			if(usernameField == null || passwordField == null || submitField == null)
				return;
			
			if(usernameField instanceof InputElement)
				((InputElement)usernameField).setValue(this.username);
			else return;
			
			if(passwordField instanceof InputElement)
				((InputElement)passwordField).setValue(this.password);
			else return;
			
			if(submitField instanceof InputElement)
				((InputElement)submitField).click();
		}
	}

	public void login(String username, String password, ISessionIdCallback callback) {
		String requestSerialized;
		try {
			requestSerialized = this.serializer.serializeLoginRequest(username, password);
		} catch (final SerializationException e1) {
			callback.onFailure(e1);
			return;
		}
		this.performLoginRequest(
				requestSerialized, 
				callback, 
				new LoginRequestCallback(callback, username, password)
			);
	}

	private class LogoutRequestCallback extends WlRequestCallback{
		private final IVoidCallback voidCallback;
		
		public LogoutRequestCallback(IVoidCallback voidCallback){
			super(voidCallback);
			this.voidCallback = voidCallback;
		}
		
		@Override
		public void onSuccessResponseReceived(String response) {
			try {
				WebLabCommunication.this.serializer.parseLogoutResponse(response);
			} catch (final SerializationException e) {
				this.voidCallback.onFailure(e);
				return;
			} catch (final WlServerException e) {
				this.voidCallback.onFailure(e);
				return;
			}
			this.voidCallback.onSuccess();
		}
	}

	public void logout(SessionID sessionId, IVoidCallback callback) {
		String requestSerialized;
		try {
			requestSerialized = this.serializer.serializeLogoutRequest(sessionId);
		} catch (final SerializationException e1) {
			callback.onFailure(e1);
			return;
		}
		this.performRequest(
				requestSerialized, 
				callback, 
				new LogoutRequestCallback(callback)
			);
	}

	private class PollRequestCallback extends WlRequestCallback{
		private final IVoidCallback voidCallback;
		
		public PollRequestCallback(IVoidCallback voidCallback){
			super(voidCallback);
			this.voidCallback = voidCallback;
		}
		
		@Override
		public void onSuccessResponseReceived(String response) {
			try {
				WebLabCommunication.this.serializer.parsePollResponse(response);
			} catch (final SerializationException e) {
				this.voidCallback.onFailure(e);
				return;
			} catch (final SessionNotFoundException e) {
				this.voidCallback.onFailure(e);
				return;
			} catch (final WlServerException e) {
				this.voidCallback.onFailure(e);
				return;
			}
			this.voidCallback.onSuccess();
		}
	}

	public void poll(SessionID sessionId, IVoidCallback callback) {
		String requestSerialized;
		try {
			requestSerialized = this.serializer.serializePollRequest(sessionId);
		} catch (final SerializationException e1) {
			callback.onFailure(e1);
			return;
		}
		this.performRequest(
				requestSerialized, 
				callback, 
				new PollRequestCallback(callback)
			);
	}

	private class ReserveExperimentRequestCallback extends WlRequestCallback{
		private final IReservationCallback reservationCallback;
		
		public ReserveExperimentRequestCallback(IReservationCallback reservationCallback){
			super(reservationCallback);
			this.reservationCallback = reservationCallback;
		}
		
		@Override
		public void onSuccessResponseReceived(String response) {
			ReservationStatus reservation;
			try {
				reservation = WebLabCommunication.this.serializer.parseReserveExperimentResponse(response);
			} catch (final SerializationException e) {
				this.reservationCallback.onFailure(e);
				return;
			} catch (final UnknownExperimentIdException e) {
				this.reservationCallback.onFailure(e);
				return;
			} catch (final SessionNotFoundException e) {
				this.reservationCallback.onFailure(e);
				return;
			} catch (final WlServerException e) {
				this.reservationCallback.onFailure(e);
				return;
			}
			this.reservationCallback.onSuccess(reservation);
		}
	}

	public void reserveExperiment(SessionID sessionId, ExperimentID experimentId, IReservationCallback callback) {
		String requestSerialized;
		try {
			requestSerialized = this.serializer.serializeReserveExperimentRequest(sessionId, experimentId);
		} catch (final SerializationException e1) {
			callback.onFailure(e1);
			return;
		}
		this.performRequest(
				requestSerialized, 
				callback, 
				new ReserveExperimentRequestCallback(callback)
			);
	}

	private class SendCommandRequestCallback extends WlRequestCallback{
		private final IResponseCommandCallback responseCommandCallback;
		
		public SendCommandRequestCallback(IResponseCommandCallback responseCommandCallback){
			super(responseCommandCallback);
			this.responseCommandCallback = responseCommandCallback;
		}
		
		@Override
		public void onSuccessResponseReceived(String response) {
			ResponseCommand command;
			try {
				command = WebLabCommunication.this.serializer.parseSendCommandResponse(response);
			} catch (final SerializationException e) {
				this.responseCommandCallback.onFailure(e);
				return;
			} catch (final SessionNotFoundException e) {
				this.responseCommandCallback.onFailure(e);
				return;
			} catch (final WlServerException e) {
				this.responseCommandCallback.onFailure(e);
				return;
			}
			this.responseCommandCallback.onSuccess(command);
		}
	}
	
	public void sendCommand(SessionID sessionId, Command command, IResponseCommandCallback callback) {
		String requestSerialized;
		try {
			requestSerialized = this.serializer.serializeSendCommandRequest(sessionId, command);
		} catch (final SerializationException e1) {
			callback.onFailure(e1);
			return;
		}
		this.performRequest(
				requestSerialized, 
				callback, 
				new SendCommandRequestCallback(callback)
			);
	}
	
	private class FinishedRequestCallback extends WlRequestCallback{
		private final IVoidCallback voidCallback;
		
		public FinishedRequestCallback(IVoidCallback voidCallback){
			super(voidCallback);
			this.voidCallback = voidCallback;
		}
		
		@Override
		public void onSuccessResponseReceived(String response) {
			try {
				WebLabCommunication.this.serializer.parseFinishedExperimentResponse(response);
			} catch (final SerializationException e) {
				this.voidCallback.onFailure(e);
				return;
			} catch (final SessionNotFoundException e) {
				this.voidCallback.onFailure(e);
				return;
			} catch (final WlServerException e) {
				this.voidCallback.onFailure(e);
				return;
			}
			this.voidCallback.onSuccess();
		}
	}
	
	public void finishedExperiment(SessionID sessionId, IVoidCallback callback) {
		String requestSerialized;
		try {
			requestSerialized = this.serializer.serializeFinishedExperimentRequest(sessionId);
		} catch (final SerializationException e1) {
			callback.onFailure(e1);
			return;
		}
		this.performRequest(
				requestSerialized, 
				callback, 
				new FinishedRequestCallback(callback)
			);
	}

	public void sendFile(SessionID sessionId, final UploadStructure uploadStructure, final IResponseCommandCallback callback) {
		// "Serialize" sessionId
	    	
		final Hidden sessionIdElement = new Hidden();
		sessionIdElement.setName(WebLabCommunication.SESSION_ID_ATTR);
		sessionIdElement.setValue(sessionId.getRealId());
		
		final Hidden fileInfoElement = new Hidden();
		fileInfoElement.setName(WebLabCommunication.FILE_INFO_ATTR);
		fileInfoElement.setValue(uploadStructure.getFileInfo());
		
		// Set up uploadStructure
		uploadStructure.addInformation(sessionIdElement);
		uploadStructure.addInformation(fileInfoElement);
		uploadStructure.getFileUpload().setName(WebLabCommunication.FILE_SENT_ATTR);
		uploadStructure.getFormPanel().setAction(this.getFilePostUrl());
		uploadStructure.getFormPanel().setEncoding(FormPanel.ENCODING_MULTIPART);
		uploadStructure.getFormPanel().setMethod(FormPanel.METHOD_POST);

		// Register handler
		uploadStructure.getFormPanel().addSubmitCompleteHandler(new SubmitCompleteHandler() {

		    public void onSubmitComplete(SubmitCompleteEvent event) {
			uploadStructure.removeInformation(sessionIdElement);

			final String resultMessage = event.getResults();
			if(GWT.isScript() && resultMessage == null) {
			    this.reportFail(callback);
			} else {
			    this.processResultMessage(callback, resultMessage);
			}
		    }

		    private void processResultMessage(IResponseCommandCallback callback, String resultMessage) {
			final ResponseCommand parsedResponseCommand;
			try {
			    parsedResponseCommand = WebLabCommunication.this.serializer.parseSendFileResponse(resultMessage);
			} catch (final SerializationException e) {
			    callback.onFailure(e);
			    return;
			} catch (final SessionNotFoundException e) {
			    callback.onFailure(e);
			    return;
			} catch (final WlServerException e) {
			    callback.onFailure(e);
			    return;
			}
			callback.onSuccess(parsedResponseCommand);
		    }
		    private void reportFail(final IResponseCommandCallback callback) {
			GWT.log("reportFail could not send the file", null);
			callback.onFailure(new WlCommException("Couldn't send the file"));
		    }			
		});
	    
		// Submit
		uploadStructure.getFormPanel().submit();
	}
}
