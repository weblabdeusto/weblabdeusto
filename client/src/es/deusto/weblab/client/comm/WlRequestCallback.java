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

import com.google.gwt.http.client.Request;
import com.google.gwt.http.client.RequestCallback;
import com.google.gwt.http.client.Response;

import es.deusto.weblab.client.comm.callbacks.IWlAsyncCallback;
import es.deusto.weblab.client.comm.exceptions.CommunicationException;
import es.deusto.weblab.client.comm.exceptions.ServerException;

abstract public class WlRequestCallback implements RequestCallback{

	private final IWlAsyncCallback callback;
	
	public WlRequestCallback(IWlAsyncCallback callback){
		this.callback = callback;
	}
	
	@Override
	public void onError(Request request, Throwable exception) {
		this.callback.onFailure(new CommunicationException(exception.getMessage(), exception));
	}

	@Override
	public void onResponseReceived(Request request, Response response) {
		final int stateCode = response.getStatusCode();
		// 5XX and 4XX are server errors
		// 500 might be returned when a SOAP-Fault is raised, so we're not going to filter it
		final int firstNumber = (stateCode / 100) % 1000;
		if(firstNumber == 4 || (firstNumber == 5 && stateCode != 500)){
			this.callback.onFailure(new ServerException("Couldn't contact with the server: " + response.getStatusText()));
		}else{
			this.onSuccessResponseReceived(response.getText());
		}
	}

	public abstract void onSuccessResponseReceived(String message);
}
