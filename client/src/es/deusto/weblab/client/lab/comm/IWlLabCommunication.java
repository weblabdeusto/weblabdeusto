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
package es.deusto.weblab.client.lab.comm;

import es.deusto.weblab.client.comm.IWlCommonCommunication;
import es.deusto.weblab.client.comm.callbacks.IUserInformationCallback;
import es.deusto.weblab.client.comm.callbacks.IVoidCallback;
import es.deusto.weblab.client.dto.SessionID;
import es.deusto.weblab.client.dto.experiments.Command;
import es.deusto.weblab.client.dto.experiments.ExperimentID;
import es.deusto.weblab.client.lab.comm.callbacks.IExperimentsAllowedCallback;
import es.deusto.weblab.client.lab.comm.callbacks.IReservationCallback;
import es.deusto.weblab.client.lab.comm.callbacks.IResponseCommandCallback;

public interface IWlLabCommunication extends IWlCommonCommunication {
	
	public void logout(SessionID sessionId, IVoidCallback callback);

	public void listExperiments(SessionID sessionId, IExperimentsAllowedCallback callback);

	public void reserveExperiment(SessionID sessionId, ExperimentID experimentId, IReservationCallback callback);

	public void finishedExperiment(SessionID sessionId, IVoidCallback callback);
	
	public void getReservationStatus(SessionID sessionId, IReservationCallback callback);

	public void sendFile(SessionID sessionId, UploadStructure structure, IResponseCommandCallback callback);

	public void sendCommand(SessionID sessionId, Command command, IResponseCommandCallback callback);

	public void poll(SessionID sessionId, IVoidCallback callback);

	public void getUserInformation(SessionID sessionId, IUserInformationCallback callback);
}