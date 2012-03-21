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
* Author: Luis Rodriguez <luis.rodriguez@opendeusto.es>
*
*/ 
package es.deusto.weblab.client.lab.comm.callbacks;

import es.deusto.weblab.client.comm.callbacks.IWebLabAsyncCallback;
import es.deusto.weblab.client.dto.experiments.AsyncRequestStatus;


/**
 *  Specific callback interface to be invoked when a check_async_command_status request
 *  finishes. It adds an specific success notification to the existing, general
 *  IWlAsyncCallback interface.
 *  
 *  The onSuccess method that this interface provides will be invoked with the status
 *  of the requests already deserialized, so it is the one that will actually handle
 *  the response. (As opposed to CheckAsyncCommandStatusRequestCallback).
 */
public interface IResponseCheckAsyncCommandStatusCallback extends IWebLabAsyncCallback {
	public void onSuccess(AsyncRequestStatus [] requests);
	//throws WlCommException, SessionNotFoundException
}
