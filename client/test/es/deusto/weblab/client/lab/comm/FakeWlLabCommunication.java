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

import com.google.gwt.json.client.JSONValue;

import es.deusto.weblab.client.comm.FakeWlCommonCommunication;
import es.deusto.weblab.client.comm.IWlCommonSerializer;
import es.deusto.weblab.client.comm.callbacks.IVoidCallback;
import es.deusto.weblab.client.dto.SessionID;
import es.deusto.weblab.client.dto.experiments.Command;
import es.deusto.weblab.client.dto.experiments.ExperimentID;
import es.deusto.weblab.client.lab.comm.callbacks.IExperimentsAllowedCallback;
import es.deusto.weblab.client.lab.comm.callbacks.IReservationCallback;
import es.deusto.weblab.client.lab.comm.callbacks.IResponseCommandCallback;

public class FakeWlLabCommunication extends FakeWlCommonCommunication implements IWlLabCommunication {

	public static final String SEND_ASYNC_FILE 		  = "FakeWeblabCommunication::sendAsyncFile";
	public static final String SEND_ASYNC_COMMAND     = "FakeWeblabCommunication::sendAsyncCommand";
	public static final String SEND_FILE              = "FakeWebLabCommunication::sendFile";
	public static final String SEND_COMMAND           = "FakeWebLabCommunication::sendCommand";
	public static final String RESERVE_EXPERIMENT     = "FakeWebLabCommunication::reserveExperiment";
	public static final String FINISHED_EXPERIMENT    = "FakeWebLabCommunication::finishedExperiment";
	public static final String POLL                   = "FakeWebLabCommunication::poll";
	public static final String LIST_EXPERIMENTS       = "FakeWebLabCommunication::listExperiments";
	public static final String GET_RESERVATION_STATUS = "FakeWebLabCommunication::getReservationStatus";
	
	@Override
	public void getReservationStatus(SessionID sessionId, IReservationCallback callback) {
		this.append(FakeWlLabCommunication.GET_RESERVATION_STATUS, new Object[]{
				sessionId,
				callback
		});
	}

	@Override
	public void listExperiments(SessionID sessionId, IExperimentsAllowedCallback callback) {
		this.append(FakeWlLabCommunication.LIST_EXPERIMENTS, new Object[]{
				sessionId,
				callback
		});
	}

	@Override
	public void poll(SessionID sessionId, IVoidCallback callback) {
		this.append(FakeWlLabCommunication.POLL, new Object[]{
				sessionId,
				callback
		});
	}

	@Override
	public void reserveExperiment(SessionID sessionId, ExperimentID experimentId, JSONValue clientInitialData, IReservationCallback callback) {
		this.append(FakeWlLabCommunication.RESERVE_EXPERIMENT, new Object[]{
				sessionId,
				experimentId,
				clientInitialData,
				callback
		});
	}

	@Override
	public void sendCommand(SessionID sessionId, Command command, IResponseCommandCallback callback) {
		this.append(FakeWlLabCommunication.SEND_COMMAND, new Object[]{
				sessionId,
				command,
				callback
		});
	}

	@Override
	public void sendFile(SessionID sessionId, UploadStructure uploadStructure, IResponseCommandCallback callback) {
		this.append(FakeWlLabCommunication.SEND_FILE, new Object[]{
				sessionId,
				uploadStructure,
				callback
		});
	}
	
	@Override
	public void sendAsyncCommand(SessionID sessionId, Command command,
			IResponseCommandCallback callback) {
		this.append(FakeWlLabCommunication.SEND_ASYNC_COMMAND, new Object[]{
				sessionId,
				command,
				callback
		});
	}

	@Override
	public void sendAsyncFile(SessionID sessionId, UploadStructure uploadStructure,
			IResponseCommandCallback callback) {
		this.append(FakeWlLabCommunication.SEND_ASYNC_FILE, new Object[]{
			sessionId,
			uploadStructure,
			callback
		});
	}

	@Override
	public void finishedExperiment(SessionID sessionId, IVoidCallback callback) {
		this.append(FakeWlLabCommunication.FINISHED_EXPERIMENT, new Object[]{ 
				sessionId,
				callback
		});
	}

	@Override
	protected IWlCommonSerializer createSerializer() {
		return new FakeWlLabSerializer();
	}


}
