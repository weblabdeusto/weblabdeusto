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
package es.deusto.weblab.client.lab.comm.callbacks;

import es.deusto.weblab.client.comm.callbacks.IWebLabAsyncCallback;
import es.deusto.weblab.client.dto.experiments.ResponseCommand;


/**
 *  Callback interface to be invoked when a command request finishes. 
 *  Because the parent interface IWlAsyncCallback only supports failure notification, 
 *  IResponseCommandCallback extends it to support success notification as well.
 *  This callback is specifically intended to be used for the response to
 *  send_file, send_command, and the like, not for all requests.
 */
public interface IResponseCommandCallback extends IWebLabAsyncCallback {
	public void onSuccess(ResponseCommand responseCommand);
	//throws WlCommException, SessionNotFoundException
}
