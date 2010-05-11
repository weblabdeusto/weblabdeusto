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

import com.google.gwt.http.client.RequestBuilder;

import es.deusto.weblab.client.configuration.IConfigurationManager;
import es.deusto.weblab.client.lab.comm.IWlLabSerializer;
import es.deusto.weblab.client.lab.comm.WlLabCommunication;

public class WrappedWebLabCommunication extends WlLabCommunication {
	
	private final IWlLabSerializer wrappedSerializer;
	private final RequestBuilder wrappedRequestBuilder;
	
	public WrappedWebLabCommunication(IWlLabSerializer wrappedSerializer, RequestBuilder wrappedRequestBuilder, IConfigurationManager configurationManager){
		super(configurationManager);
		this.wrappedSerializer = wrappedSerializer;
		this.wrappedRequestBuilder = wrappedRequestBuilder;
		this.setSerializer(this.wrappedSerializer);
	}
	
	@Override
	protected void createSerializer(){}
	
	@Override
	protected RequestBuilder createRequestBuilder(RequestBuilder.Method method, String url){
		return this.wrappedRequestBuilder;
	}	
}
