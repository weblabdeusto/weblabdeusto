/*
* Copyright (C) 2012 onwards University of Deusto
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

package es.deusto.weblab.client.lab.experiments;

import es.deusto.weblab.client.comm.exceptions.CommException;
import es.deusto.weblab.client.dto.experiments.ResponseCommand;
import es.deusto.weblab.client.lab.comm.callbacks.IResponseCommandCallback;

public final class CallbackWrapper implements ISimpleResponseCallback {
	
	private final IResponseCommandCallback callback;
	
	public CallbackWrapper(IResponseCommandCallback callback) {
		this.callback = callback;
	}
	
	@Override
	public void onFailure(String e) {
		this.callback.onFailure(new CommException(e));
	}
	
	@Override
	public void onSuccess(String responseCommand) {
		this.callback.onSuccess(new ResponseCommand(responseCommand));
	}
}