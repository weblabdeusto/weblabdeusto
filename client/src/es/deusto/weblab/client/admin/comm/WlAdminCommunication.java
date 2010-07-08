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

import java.util.ArrayList;
import java.util.Date;

import com.google.gwt.http.client.RequestBuilder;
import com.google.gwt.http.client.RequestCallback;
import com.google.gwt.http.client.RequestException;

import es.deusto.weblab.client.admin.comm.callbacks.IExperimentUsesCallback;
import es.deusto.weblab.client.admin.comm.callbacks.IExperimentsCallback;
import es.deusto.weblab.client.admin.comm.callbacks.IGroupsCallback;
import es.deusto.weblab.client.admin.comm.callbacks.IUsersCallback;
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
import es.deusto.weblab.client.dto.experiments.Experiment;
import es.deusto.weblab.client.dto.experiments.ExperimentUse;
import es.deusto.weblab.client.dto.users.Group;
import es.deusto.weblab.client.dto.users.User;

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
	
	private class GetExperimentsRequestCallback extends WlRequestCallback{
		private final IExperimentsCallback experimentsCallback;
		
		public GetExperimentsRequestCallback(IExperimentsCallback callback){
			super(callback);
			this.experimentsCallback = callback;
		}
		
		@Override
		public void onSuccessResponseReceived(String response){
			ArrayList<Experiment> groups;
			try {
				groups = ((IWlAdminSerializer)WlAdminCommunication.this.serializer).parseGetExperimentsResponse(response);
			} catch (final SerializationException e) {
				this.experimentsCallback.onFailure(e);
				return;
			} catch (final SessionNotFoundException e) {
				this.experimentsCallback.onFailure(e);
				return;
			} catch (final WlServerException e) {
				this.experimentsCallback.onFailure(e);
				return;
			}
			this.experimentsCallback.onSuccess(groups);
		}
	}	
	
	@Override
	public void getExperiments(SessionID sessionId, IExperimentsCallback callback) {
		String requestSerialized;
		try {
			requestSerialized = ((IWlAdminSerializer)this.serializer).serializeGetExperimentsRequest(sessionId);
		} catch (final SerializationException e) {
			callback.onFailure(e);
			return;
		}
		this.performAdminRequest(
				requestSerialized, 
				callback, 
				new GetExperimentsRequestCallback(callback)
			);
	}
	
	
	
	private class GetUsersRequestCallback extends WlRequestCallback{
		private final IUsersCallback usersCallback;
		
		public GetUsersRequestCallback(IUsersCallback usersCallback){
			super(usersCallback);
			this.usersCallback = usersCallback;
		}
		
		@Override
		public void onSuccessResponseReceived(String response){
			ArrayList<User> users;
			try {
				users = ((IWlAdminSerializer)WlAdminCommunication.this.serializer).parseGetUsersResponse(response);
			} catch (final SerializationException e) {
				this.usersCallback.onFailure(e);
				return;
			} catch (final SessionNotFoundException e) {
				this.usersCallback.onFailure(e);
				return;
			} catch (final WlServerException e) {
				this.usersCallback.onFailure(e);
				return;
			}
			this.usersCallback.onSuccess(users);
		}
	}
	
	
	@Override
	public void getUsers(SessionID sessionId, IUsersCallback callback) {
		String requestSerialized;
		try {
			requestSerialized = ((IWlAdminSerializer)this.serializer).serializeGetUsersRequest(sessionId);
		} catch (final SerializationException e) {
			callback.onFailure(e);
			return;
		}
		this.performAdminRequest(
				requestSerialized, 
				callback, 
				new GetUsersRequestCallback(callback)
			);
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
	
	private class GetExperimentUsesRequestCallback extends WlRequestCallback{
		private final IExperimentUsesCallback experimentUsesCallback;
		
		public GetExperimentUsesRequestCallback(IExperimentUsesCallback callback){
			super(callback);
			this.experimentUsesCallback = callback;
		}
		
		@Override
		public void onSuccessResponseReceived(String response){
			ArrayList<ExperimentUse> groups;
			try {
				groups = ((IWlAdminSerializer)WlAdminCommunication.this.serializer).parseGetExperimentUsesResponse(response);
			} catch (final SerializationException e) {
				this.experimentUsesCallback.onFailure(e);
				return;
			} catch (final SessionNotFoundException e) {
				this.experimentUsesCallback.onFailure(e);
				return;
			} catch (final WlServerException e) {
				this.experimentUsesCallback.onFailure(e);
				return;
			}
			this.experimentUsesCallback.onSuccess(groups);
		}
	}

	@Override
	public void getExperimentUses(SessionID sessionId, Date fromDate, Date toDate, int groupId, int experimentId, IExperimentUsesCallback callback) {
		String requestSerialized;
		try {
			requestSerialized = ((IWlAdminSerializer)this.serializer).serializeGetExperimentUsesRequest(sessionId, fromDate, toDate, groupId, experimentId);
		} catch (final SerializationException e) {
			callback.onFailure(e);
			return;
		}
		this.performAdminRequest(
				requestSerialized, 
				callback, 
				new GetExperimentUsesRequestCallback(callback)
			);
	}

}
