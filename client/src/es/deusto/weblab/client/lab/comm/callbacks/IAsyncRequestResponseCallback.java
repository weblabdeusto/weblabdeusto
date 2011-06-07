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
* Author: Luis Rodriguez <luis.rodriguez@opendeusto.es>
*
*/ 
package es.deusto.weblab.client.lab.comm.callbacks;

import es.deusto.weblab.client.comm.callbacks.IWlAsyncCallback;
import es.deusto.weblab.client.dto.experiments.ResponseCommand;


/**
 * Interface that will be used to notify the result of an asynchronous
 * request, such as an async_send_file or async_send_command, to the caller.
 * TODO: Consider adding an onTimeout or similar for time-out support. 
 */
public interface IAsyncRequestResponseCallback extends IWlAsyncCallback {
	
	/**
	 * Invoked whenever the request is successful. 
	 * @param responseCommand The response to the request, contained in a ResponseCommand object.
	 */
	public void onSuccess(ResponseCommand responseCommand);
	
	/**
	 * Invoked whenever the request failed.
	 * @param responseCommand The response to the request, which in this case will most often be
	 * some kind of error message describing the remote exception that occurred. 
	 */
	public void onFailure(ResponseCommand responseCommand);
	
}
