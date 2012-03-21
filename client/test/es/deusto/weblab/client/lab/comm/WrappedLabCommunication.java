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
*
*/ 
package es.deusto.weblab.client.lab.comm;

import com.google.gwt.http.client.RequestBuilder;

import es.deusto.weblab.client.comm.ICommonSerializer;
import es.deusto.weblab.client.configuration.IConfigurationManager;

public class WrappedLabCommunication extends LabCommunication {
	
	private final ILabSerializer wrappedSerializer;
	private final RequestBuilder wrappedRequestBuilder;
	
	public WrappedLabCommunication(ILabSerializer wrappedSerializer, RequestBuilder wrappedRequestBuilder, IConfigurationManager configurationManager){
		super(configurationManager);
		this.wrappedSerializer = wrappedSerializer;
		this.wrappedRequestBuilder = wrappedRequestBuilder;
		this.serializer = this.wrappedSerializer;
	}
	
	@Override
	protected ICommonSerializer createSerializer(){
		return null;
	}
	
	@Override
	protected RequestBuilder createRequestBuilder(RequestBuilder.Method method, String url){
		return this.wrappedRequestBuilder;
	}	
}
