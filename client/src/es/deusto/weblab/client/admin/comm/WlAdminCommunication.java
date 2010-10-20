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
* Author: Jaime Irurzun <jaime.irurzun@gmail.com>
*
*/

package es.deusto.weblab.client.admin.comm;

import com.google.gwt.http.client.RequestBuilder;
import com.google.gwt.http.client.RequestCallback;
import com.google.gwt.http.client.RequestException;

import es.deusto.weblab.client.admin.comm.callbacks.IPermissionsCallback;
import es.deusto.weblab.client.comm.IWlCommonSerializer;
import es.deusto.weblab.client.comm.WlCommonCommunication;
import es.deusto.weblab.client.comm.WlRequestCallback;
import es.deusto.weblab.client.comm.callbacks.IWlAsyncCallback;
import es.deusto.weblab.client.comm.exceptions.CommunicationException;
import es.deusto.weblab.client.comm.exceptions.SerializationException;
import es.deusto.weblab.client.comm.exceptions.WlServerException;
import es.deusto.weblab.client.comm.exceptions.core.SessionNotFoundException;
import es.deusto.weblab.client.configuration.IConfigurationManager;
import es.deusto.weblab.client.dto.SessionID;
import es.deusto.weblab.client.dto.users.Permission;

public class WlAdminCommunication extends WlCommonCommunication implements IWlAdminCommunication {
	
	public static final String WEBLAB_ADMIN_SERVICE_URL_PROPERTY = "weblab.service.admin.url";
	public static final String DEFAULT_WEBLAB_ADMIN_SERVICE_URL = "/weblab/json/";

	public WlAdminCommunication(IConfigurationManager configurationManager) {
		super(configurationManager);
	}

	@Override
	protected IWlCommonSerializer createSerializer() {
		return new WlAdminSerializerJSON();
	}
	
	private String getAdminServiceUrl(){
		return this.configurationManager.getProperty(
					WlAdminCommunication.WEBLAB_ADMIN_SERVICE_URL_PROPERTY,
					WlAdminCommunication.DEFAULT_WEBLAB_ADMIN_SERVICE_URL
				);
	}	
	
	protected void performAdminRequest(String requestSerialized, IWlAsyncCallback failureCallback, RequestCallback rci){
		final RequestBuilder rb = this.createRequestBuilder(RequestBuilder.POST, this.getAdminServiceUrl());
		try {
			rb.sendRequest(requestSerialized, rci);
		} catch (final RequestException e) {
			failureCallback.onFailure(new CommunicationException(e.getMessage(), e));
		}
	}		
	
	private class GetUserPermissionsRequestCallback extends WlRequestCallback{
		private final IPermissionsCallback permissionsCallback;
		
		public GetUserPermissionsRequestCallback(IPermissionsCallback permissionsCallback){
			super(permissionsCallback);
			this.permissionsCallback = permissionsCallback;
		}
		
		@Override
		public void onSuccessResponseReceived(String response){
			Permission [] permissions;
			try {
				permissions = ((IWlAdminSerializer)WlAdminCommunication.this.serializer).parseGetUserPermissionsResponse(response);
			} catch (final SerializationException e) {
				this.permissionsCallback.onFailure(e);
				return;
			} catch (final SessionNotFoundException e) {
				this.permissionsCallback.onFailure(e);
				return;
			} catch (final WlServerException e) {
				this.permissionsCallback.onFailure(e);
				return;
			}
			this.permissionsCallback.onSuccess(permissions);
		}
	}

	@Override
	public void getUserPermissions(SessionID sessionId, IPermissionsCallback callback) {
		String requestSerialized;
		try {
			requestSerialized = ((IWlAdminSerializer)this.serializer).serializeGetUserPermissionsRequest(sessionId);
		} catch (final SerializationException e1) {
			callback.onFailure(e1);
			return;
		}
		this.performRequest(
				requestSerialized, 
				callback, 
				new GetUserPermissionsRequestCallback(callback)
			);
	}	
}
