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

package es.deusto.weblab.client.admin.comm;

import java.util.ArrayList;

import com.google.gwt.http.client.RequestBuilder;
import com.google.gwt.http.client.RequestCallback;
import com.google.gwt.http.client.RequestException;

import es.deusto.weblab.client.admin.comm.callbacks.IGroupsCallback;
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
import es.deusto.weblab.client.dto.users.Group;

public class WlAdminCommunication extends WlCommonCommunication implements IWlAdminCommunication {
	
	public static final String WEBLAB_ADMIN_SERVICE_URL_PROPERTY = "weblab.service.admin.url";
	public static final String DEFAULT_WEBLAB_ADMIN_SERVICE_URL = "/weblab/admin/json/";

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
	
	private class GetGroupsRequestCallback extends WlRequestCallback{
		private final IGroupsCallback groupsCallback;
		
		public GetGroupsRequestCallback(IGroupsCallback groupsCallback){
			super(groupsCallback);
			this.groupsCallback = groupsCallback;
		}
		
		@Override
		public void onSuccessResponseReceived(String response){
			ArrayList<Group> groups;
			try {
				groups = ((IWlAdminSerializer)WlAdminCommunication.this.serializer).parseGetGroupsResponse(response);
			} catch (final SerializationException e) {
				this.groupsCallback.onFailure(e);
				return;
			} catch (final SessionNotFoundException e) {
				this.groupsCallback.onFailure(e);
				return;
			} catch (final WlServerException e) {
				this.groupsCallback.onFailure(e);
				return;
			}
			this.groupsCallback.onSuccess(groups);
		}
	}

	@Override
	public void getGroups(SessionID sessionId, IGroupsCallback callback) {
		String requestSerialized;
		try {
			requestSerialized = ((IWlAdminSerializer)this.serializer).serializeGetGroupsRequest(sessionId);
		} catch (final SerializationException e) {
			callback.onFailure(e);
			return;
		}
		this.performAdminRequest(
				requestSerialized, 
				callback, 
				new GetGroupsRequestCallback(callback)
			);
	}
}
