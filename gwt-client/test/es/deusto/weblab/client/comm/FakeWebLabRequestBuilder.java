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
package es.deusto.weblab.client.comm;

import com.google.gwt.http.client.Header;
import com.google.gwt.http.client.Request;
import com.google.gwt.http.client.RequestBuilder;
import com.google.gwt.http.client.RequestCallback;
import com.google.gwt.http.client.RequestException;
import com.google.gwt.http.client.Response;

public class FakeWebLabRequestBuilder extends RequestBuilder{

	public FakeWebLabRequestBuilder() {
		super(RequestBuilder.POST, "/weblab");
	}
	
	private boolean nextAnswer = false;
	private boolean nextThrow = false;
	private boolean nextError = false;
	
	private String message;
	private RequestException toThrow;
	private Throwable toError; 
	
	public void setNextReceivedMessage(String message){
		this.nextAnswer = true;
		this.nextThrow  = false;
		this.nextError  = false;
		this.message = message;
	}
			
	public void setNextToThrow(RequestException toThrow){
		this.nextAnswer = false;
		this.nextThrow  = true;
		this.nextError  = false;
		this.toThrow = toThrow;
	}
	
	public void setNextToError(Throwable toError){
		this.nextAnswer = false;
		this.nextThrow  = false;
		this.nextError  = true;
		this.toError = toError;
	}
	
	@Override
	public Request sendRequest(String header, RequestCallback callback) throws RequestException {
		if(this.nextAnswer){
			callback.onResponseReceived(null, this.getResponseToSend());
		}else if(this.nextThrow){
			throw this.toThrow;
		}else if(this.nextError){
			callback.onError(null, this.toError);
		}
		return null;
	}
	
	public void setResponseToSend(Response response){
		this.responseToSend = response;
	}
	
	public final Response DEFAULT_RESPONSE = new Response(){
		@Override
		public String getHeader(String header) {
			return null;
		}
		@Override
		public Header[] getHeaders() {
			return null;
		}
		@Override
		public String getHeadersAsString() {
			return null;
		}
		@Override
		public int getStatusCode() {
			return 200;
		}
		@Override
		public String getStatusText() {
			return null;
		}
		@Override
		public String getText() {
			return FakeWebLabRequestBuilder.this.message;
		}
	};

	private Response responseToSend = this.DEFAULT_RESPONSE;
	
	private Response getResponseToSend() {
		return this.responseToSend;
	}
}