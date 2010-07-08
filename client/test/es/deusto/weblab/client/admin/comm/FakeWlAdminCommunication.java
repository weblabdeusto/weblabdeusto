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
*         Jaime Irurzun <jaime.irurzun@gmail.com>
*
*/

package es.deusto.weblab.client.admin.comm;

import java.util.Date;

import es.deusto.weblab.client.admin.comm.callbacks.IExperimentUsesCallback;
import es.deusto.weblab.client.admin.comm.callbacks.IExperimentsCallback;
import es.deusto.weblab.client.admin.comm.callbacks.IGroupsCallback;
import es.deusto.weblab.client.admin.comm.callbacks.IUsersCallback;
import es.deusto.weblab.client.comm.FakeWlCommonCommunication;
import es.deusto.weblab.client.comm.IWlCommonSerializer;
import es.deusto.weblab.client.dto.SessionID;

public class FakeWlAdminCommunication extends FakeWlCommonCommunication implements IWlAdminCommunication {

	public static final String GET_GROUPS          = "FakeWebLabCommunication::getGroups";
	public static final String GET_EXPERIMENTS     = "FakeWebLabCommunication::getExperiments";
	public static final String GET_EXPERIMENT_USES = "FakeWebLabCommunication::getExperimentUses";
	public static final String GET_USERS		   = "FakeWebLabCommunication::getUsers";
	
	@Override
	protected IWlCommonSerializer createSerializer() {
		return new FakeWlAdminSerializer();
	}

	@Override
	public void getGroups(SessionID sessionId, IGroupsCallback callback) {
		this.append(FakeWlAdminCommunication.GET_GROUPS, new Object[]{
				sessionId,
				callback
		});
	}
	
	@Override
	public void getUsers(SessionID sessionId, IUsersCallback callback) {
		this.append(FakeWlAdminCommunication.GET_USERS, new Object[] {
			sessionId,
			callback
		});
	}

	@Override
	public void getExperiments(SessionID sessionId, IExperimentsCallback callback) {
		this.append(FakeWlAdminCommunication.GET_EXPERIMENTS, new Object[]{
				sessionId,
				callback
		});
	}

	@Override
	public void getExperimentUses(SessionID sessionId, Date fromDate, Date toDate, int groupId, int experimentId, IExperimentUsesCallback callback) {
		this.append(FakeWlAdminCommunication.GET_EXPERIMENT_USES, new Object[]{
				sessionId,
				callback
		});
	}

}
