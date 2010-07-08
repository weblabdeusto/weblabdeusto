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
* Author: Jaime Irurzun <jaime.irurzun@gmail.com>
*
*/

package es.deusto.weblab.client.admin.comm;

import java.util.Date;

import es.deusto.weblab.client.admin.comm.callbacks.IExperimentUsesCallback;
import es.deusto.weblab.client.admin.comm.callbacks.IExperimentsCallback;
import es.deusto.weblab.client.admin.comm.callbacks.IGroupsCallback;
import es.deusto.weblab.client.admin.comm.callbacks.IUsersCallback;
import es.deusto.weblab.client.comm.IWlCommonCommunication;
import es.deusto.weblab.client.dto.SessionID;

public interface IWlAdminCommunication extends IWlCommonCommunication {

	void getExperiments(SessionID sessionId, IExperimentsCallback iExperimentsCallback);
	void getGroups(SessionID sessionId, IGroupsCallback iGroupsCallback);
	void getExperimentUses(SessionID sessionId, Date fromDate, Date toDate, int groupId, int experimentId, IExperimentUsesCallback callback);
	void getUsers(SessionID sessionId, IUsersCallback iUsersCallback);
}