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
*         Jaime Irurzun <jaime.irurzun@gmail.com>
*
*/

package es.deusto.weblab.client.comm;

import java.util.Map;

import com.google.gwt.dom.client.Element;
import com.google.gwt.dom.client.InputElement;
import com.google.gwt.http.client.RequestBuilder;
import com.google.gwt.http.client.RequestCallback;
import com.google.gwt.http.client.RequestException;
import com.google.gwt.user.client.DOM;

import es.deusto.weblab.client.WebLabClient;
import es.deusto.weblab.client.comm.callbacks.ISessionIdCallback;
import es.deusto.weblab.client.comm.callbacks.IUserInformationCallback;
import es.deusto.weblab.client.comm.callbacks.IVoidCallback;
import es.deusto.weblab.client.comm.callbacks.IWebLabAsyncCallback;
import es.deusto.weblab.client.comm.exceptions.CommunicationException;
import es.deusto.weblab.client.comm.exceptions.SerializationException;
import es.deusto.weblab.client.comm.exceptions.WebLabServerException;
import es.deusto.weblab.client.comm.exceptions.core.SessionNotFoundException;
import es.deusto.weblab.client.comm.exceptions.login.InvalidCredentialsException;
import es.deusto.weblab.client.comm.exceptions.login.LoginException;
import es.deusto.weblab.client.configuration.IConfigurationManager;
import es.deusto.weblab.client.dto.SessionID;
import es.deusto.weblab.client.dto.users.User;

public abstract class CommonCommunication implements ICommonCommunication {
	
	public static final String WEBLAB_LOGIN_SERVICE_URL_PROPERTY = "weblab.service.login.url";
	public static final String DEFAULT_WEBLAB_LOGIN_SERVICE_URL = "/weblab/login/json/";
	public static final String WEBLAB_SERVICE_URL_PROPERTY = "weblab.service.url";
	public static final String DEFAULT_WEBLAB_SERVICE_URL = "/weblab/json/";

	protected final IConfigurationManager configurationManager;
	protected ICommonSerializer serializer;
	
	protected CommonCommunication(IConfigurationManager configurationManager){
		this.configurationManager = configurationManager;
		this.serializer = this.createSerializer();
	}

	protected abstract ICommonSerializer createSerializer();

	protected void setSerializer(ICommonSerializer serializer){
		this.serializer = serializer;
	}
	
	private String getServiceUrl(){
		final String baseLocation = this.configurationManager.getProperty(WebLabClient.BASE_LOCATION, WebLabClient.DEFAULT_BASE_LOCATION);
		return baseLocation + this.configurationManager.getProperty(
					CommonCommunication.WEBLAB_SERVICE_URL_PROPERTY,
					CommonCommunication.DEFAULT_WEBLAB_SERVICE_URL
				);
	}
	
	
	/**
	 * Performs a request. The request is sent to the server, and when finished,
	 * its result is returned through a callback.
	 * @param requestSerialized The request to be performed, already serialized. 
	 * @param failureCallback Callback to invoke if the request fails.
	 * @param rci Callback to invoke when the request finishes.
	 */
	public void performRequest(String requestSerialized, IWebLabAsyncCallback failureCallback, RequestCallback rci){
		performRequest(requestSerialized, failureCallback, rci, null);
	}
	
	public void performRequest(String requestSerialized, IWebLabAsyncCallback failureCallback, RequestCallback rci, Map<String, String> headers){
		final RequestBuilder rb = this.createRequestBuilder(RequestBuilder.POST, this.getServiceUrl());
		if(headers != null)
			for(String header : headers.keySet()) 
				rb.setHeader(header, headers.get(header));
			
		try {
			rb.sendRequest(requestSerialized, rci);
		} catch (final RequestException e) {
			failureCallback.onFailure(new CommunicationException(e.getMessage(), e));
		}
	}	
	
	private String getLoginServiceUrl(){
		final String baseLocation = this.configurationManager.getProperty(WebLabClient.BASE_LOCATION, WebLabClient.DEFAULT_BASE_LOCATION);
		return baseLocation + this.configurationManager.getProperty(
					CommonCommunication.WEBLAB_LOGIN_SERVICE_URL_PROPERTY,
					CommonCommunication.DEFAULT_WEBLAB_LOGIN_SERVICE_URL
				);
	}
	
	// For testing purposes
	protected RequestBuilder createRequestBuilder(RequestBuilder.Method method, String url){
		return new RequestBuilder(method, url);
	}
	
	private void performLoginRequest(String requestSerialized,
			IWebLabAsyncCallback failureCallback, RequestCallback rci) {
	        	final RequestBuilder rb = this.createRequestBuilder(RequestBuilder.POST, this.getLoginServiceUrl());
	        	try {
	        		rb.sendRequest(requestSerialized, rci);
	        	} catch (final RequestException e) {
	        		failureCallback.onFailure(new CommunicationException(e.getMessage(), e));
	        	}
		}

	private class LoginRequestCallback extends WebLabRequestCallback{
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
				sessionId = CommonCommunication.this.serializer.parseLoginResponse(response);
			} catch (final SerializationException e) {
				if(response.contains("503 for URL"))
					this.sessionIdCallback.onFailure(new SerializationException("Is the WebLab-Deusto server down? Got an " + e.getMessage(), e));
				else
					this.sessionIdCallback.onFailure(e);
				return;
			} catch (final InvalidCredentialsException e) {
				this.sessionIdCallback.onFailure(e);
				return;
			} catch (final LoginException e) {
				this.sessionIdCallback.onFailure(e);
				return;
			} catch (final WebLabServerException e) {
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

	@Override
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
	


	private class LogoutRequestCallback extends WebLabRequestCallback{
		private final IVoidCallback voidCallback;
		
		public LogoutRequestCallback(IVoidCallback voidCallback){
			super(voidCallback);
			this.voidCallback = voidCallback;
		}
		
		@Override
		public void onSuccessResponseReceived(String response) {
			try {
				CommonCommunication.this.serializer.parseLogoutResponse(response);
			} catch (final SerializationException e) {
				this.voidCallback.onFailure(e);
				return;
			} catch (final WebLabServerException e) {
				this.voidCallback.onFailure(e);
				return;
			}
			this.voidCallback.onSuccess();
		}
	}

	@Override
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
	
	private class UserInformationRequestCallback extends WebLabRequestCallback{
		private final IUserInformationCallback userInformationCallback;
		
		public UserInformationRequestCallback(IUserInformationCallback userInformationCallback){
			super(userInformationCallback);
			this.userInformationCallback = userInformationCallback;
		}
		
		@Override
		public void onSuccessResponseReceived(String response) {
			User user;
			try {
				user = CommonCommunication.this.serializer.parseGetUserInformationResponse(response);
			} catch (final SerializationException e) {
				this.userInformationCallback.onFailure(e);
				return;
			} catch (final SessionNotFoundException e) {
				this.userInformationCallback.onFailure(e);
				return;
			} catch (final WebLabServerException e) {
				this.userInformationCallback.onFailure(e);
				return;
			}
			this.userInformationCallback.onSuccess(user);
		}
	}
	
	@Override
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
	
	
}
