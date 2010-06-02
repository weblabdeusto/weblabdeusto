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
* Author: FILLME
*
*/

package es.deusto.weblab.client.admin.comm;

import es.deusto.weblab.client.admin.comm.callbacks.IGroupsCallback;
import es.deusto.weblab.client.comm.IWlCommonCommunication;
import es.deusto.weblab.client.dto.SessionID;

public interface IWlAdminCommunication extends IWlCommonCommunication {

	void getGroups(SessionID currentSession, IGroupsCallback iGroupsCallback);

}
