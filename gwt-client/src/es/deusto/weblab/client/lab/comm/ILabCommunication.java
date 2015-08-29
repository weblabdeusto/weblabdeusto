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
*         Luis Rodriguez <luis.rodriguez@opendeusto.es>
*
*/ 
package es.deusto.weblab.client.lab.comm;

import com.google.gwt.json.client.JSONValue;

import es.deusto.weblab.client.comm.ICommonCommunication;
import es.deusto.weblab.client.comm.callbacks.IVoidCallback;
import es.deusto.weblab.client.dto.SessionID;
import es.deusto.weblab.client.dto.experiments.Command;
import es.deusto.weblab.client.dto.experiments.ExperimentID;
import es.deusto.weblab.client.lab.comm.callbacks.IExperimentsAllowedCallback;
import es.deusto.weblab.client.lab.comm.callbacks.IReservationCallback;
import es.deusto.weblab.client.lab.comm.callbacks.IResponseCommandCallback;

public interface ILabCommunication extends ICommonCommunication {
	
	public void listExperiments(SessionID sessionId, IExperimentsAllowedCallback callback);

	public void reserveExperiment(SessionID sessionId, ExperimentID experimentId, JSONValue clientInitialData, IReservationCallback callback);

	public void finishedExperiment(SessionID sessionId, IVoidCallback callback);
	
	public void getReservationStatus(SessionID sessionId, IReservationCallback callback);

	/**
	 * To send a file. The laboratory server will execute the request synchronously.
	 * @param sessionId Session id
	 * @param structure Structure for file uploading
	 * @param callback Callback notified when the request finishes
	 */
	public void sendFile(SessionID sessionId, UploadStructure structure, IResponseCommandCallback callback);
	
	/**
	 * To send a file. The laboraty server will execute the request asynchronously, on
	 * its own thread.
	 * @param sessionId Session id
	 * @param structure Structure for file uploading
	 * @param callback Callback notified when the request finishes
	 */
	public void sendAsyncFile(SessionID sessionId, UploadStructure structure, IResponseCommandCallback callback);
	
	/**
	 * To send a command. The laboratory server will handle the command asynchronously,
	 * on its own thread.
	 * @param sessionId Session id
	 * @param command Command to send
	 * @param callback Callback notified when the request finishes
	 */
	public void sendAsyncCommand(SessionID sessionId, Command command, IResponseCommandCallback callback);
	
	/**
	 * To send a command. The laboratory server will handle the command synchronously.
	 * @param sessionId Session id
	 * @param command Command to send
	 * @param callback Callback notified when the request finishes
	 */
	public void sendCommand(SessionID sessionId, Command command, IResponseCommandCallback callback);

	public void poll(SessionID sessionId, IVoidCallback callback);
}