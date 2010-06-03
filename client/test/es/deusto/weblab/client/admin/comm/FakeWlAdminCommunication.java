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
import es.deusto.weblab.client.comm.FakeWlCommonCommunication;
import es.deusto.weblab.client.comm.IWlCommonSerializer;
import es.deusto.weblab.client.dto.SessionID;

public class FakeWlAdminCommunication extends FakeWlCommonCommunication implements IWlAdminCommunication {

	public static final String GET_GROUPS       = "FakeWebLabCommunication::getGroups";
	
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

}
