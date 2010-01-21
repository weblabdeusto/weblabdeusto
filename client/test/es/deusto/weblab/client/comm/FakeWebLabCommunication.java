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

import es.deusto.weblab.client.comm.callbacks.IExperimentsAllowedCallback;
import es.deusto.weblab.client.comm.callbacks.IReservationCallback;
import es.deusto.weblab.client.comm.callbacks.IResponseCommandCallback;
import es.deusto.weblab.client.comm.callbacks.ISessionIdCallback;
import es.deusto.weblab.client.comm.callbacks.IUserInformationCallback;
import es.deusto.weblab.client.comm.callbacks.IVoidCallback;
import es.deusto.weblab.client.dto.SessionID;
import es.deusto.weblab.client.dto.experiments.Command;
import es.deusto.weblab.client.dto.experiments.ExperimentID;
import es.deusto.weblab.client.testing.util.WlFake;

public class FakeWebLabCommunication extends WlFake implements IWebLabCommunication{

	public static final String SEND_FILE              = "FakeWebLabCommunication::sendFile";
	public static final String SEND_COMMAND           = "FakeWebLabCommunication::sendCommand";
	public static final String RESERVE_EXPERIMENT     = "FakeWebLabCommunication::reserveExperiment";
	public static final String FINISHED_EXPERIMENT    = "FakeWebLabCommunication::finishedExperiment";
	public static final String POLL                   = "FakeWebLabCommunication::poll";
	public static final String LOGOUT                 = "FakeWebLabCommunication::logout";
	public static final String LOGIN                  = "FakeWebLabCommunication::login";
	public static final String LIST_EXPERIMENTS       = "FakeWebLabCommunication::listExperiments";
	public static final String GET_USER_INFORMATION   = "FakeWebLabCommunication::getUserInformation";
	public static final String GET_RESERVATION_STATUS = "FakeWebLabCommunication::getReservationStatus";
	
	public void getReservationStatus(SessionID sessionId, IReservationCallback callback) {
		this.append(FakeWebLabCommunication.GET_RESERVATION_STATUS, new Object[]{
				sessionId,
				callback
		});
	}

	public void getUserInformation(SessionID sessionId, IUserInformationCallback callback) {
		this.append(FakeWebLabCommunication.GET_USER_INFORMATION, new Object[]{
				sessionId,
				callback
		});
	}

	public void listExperiments(SessionID sessionId, IExperimentsAllowedCallback callback) {
		this.append(FakeWebLabCommunication.LIST_EXPERIMENTS, new Object[]{
				sessionId,
				callback
		});
	}

	public void login(String username, String password, ISessionIdCallback callback) {
		this.append(FakeWebLabCommunication.LOGIN, new Object[]{
				username,
				password,
				callback
		});
	}

	public void logout(SessionID sessionId, IVoidCallback callback) {
		this.append(FakeWebLabCommunication.LOGOUT, new Object[]{
				sessionId,
				callback
		});
	}

	public void poll(SessionID sessionId, IVoidCallback callback) {
		this.append(FakeWebLabCommunication.POLL, new Object[]{
				sessionId,
				callback
		});
	}

	public void reserveExperiment(SessionID sessionId, ExperimentID experimentId, IReservationCallback callback) {
		this.append(FakeWebLabCommunication.RESERVE_EXPERIMENT, new Object[]{
				sessionId,
				experimentId,
				callback
		});
	}

	public void sendCommand(SessionID sessionId, Command command, IResponseCommandCallback callback) {
		this.append(FakeWebLabCommunication.SEND_COMMAND, new Object[]{
				sessionId,
				command,
				callback
		});
	}

	public void sendFile(SessionID sessionId, UploadStructure uploadStructure, IResponseCommandCallback callback) {
		this.append(FakeWebLabCommunication.SEND_FILE, new Object[]{
				sessionId,
				uploadStructure,
				callback
		});
	}

	public void finishedExperiment(SessionID sessionId, IVoidCallback callback) {
		this.append(FakeWebLabCommunication.FINISHED_EXPERIMENT, new Object[]{ 
				sessionId,
				callback
		});
	}
}
