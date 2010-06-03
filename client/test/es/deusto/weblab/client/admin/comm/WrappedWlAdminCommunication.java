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

import com.google.gwt.http.client.RequestBuilder;

import es.deusto.weblab.client.comm.IWlCommonSerializer;
import es.deusto.weblab.client.configuration.IConfigurationManager;

public class WrappedWlAdminCommunication extends WlAdminCommunication {
	
	private final IWlAdminSerializer wrappedSerializer;
	private final RequestBuilder wrappedRequestBuilder;
	
	public WrappedWlAdminCommunication(IWlAdminSerializer wrappedSerializer, RequestBuilder wrappedRequestBuilder, IConfigurationManager configurationManager){
		super(configurationManager);
		this.wrappedSerializer = wrappedSerializer;
		this.wrappedRequestBuilder = wrappedRequestBuilder;
		this.serializer = this.wrappedSerializer;
	}
	
	@Override
	protected IWlCommonSerializer createSerializer(){
		return null;
	}
	
	@Override
	protected RequestBuilder createRequestBuilder(RequestBuilder.Method method, String url){
		return this.wrappedRequestBuilder;
	}	
}
