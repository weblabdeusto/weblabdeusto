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
*         Jaime Irurzun <jaime.irurzun@gmail.com>
*
*/

package es.deusto.weblab.client.comm;

import es.deusto.weblab.client.comm.callbacks.ISessionIdCallback;
import es.deusto.weblab.client.comm.callbacks.IUserInformationCallback;
import es.deusto.weblab.client.comm.callbacks.IVoidCallback;
import es.deusto.weblab.client.dto.SessionID;
import es.deusto.weblab.client.testing.util.WebLabFake;

public abstract class FakeCommonCommunication extends WebLabFake implements ICommonCommunication {
	
	public static final String LOGIN                  = "FakeWebLabCommunication::login";
	public static final String LOGOUT                 = "FakeWebLabCommunication::logout";
	public static final String GET_USER_INFORMATION   = "FakeWebLabCommunication::getUserInformation";
	
	@Override
	public void login(String username, String password, ISessionIdCallback callback) {
		this.append(FakeCommonCommunication.LOGIN, new Object[]{
				username,
				password,
				callback
		});
	}

	@Override
	public void logout(SessionID sessionId, IVoidCallback callback) {
		this.append(FakeCommonCommunication.LOGOUT, new Object[]{
				sessionId,
				callback
		});
	}

	@Override
	public void getUserInformation(SessionID sessionId, IUserInformationCallback callback) {
		this.append(FakeCommonCommunication.GET_USER_INFORMATION, new Object[]{
				sessionId,
				callback
		});
	}
	
	protected abstract ICommonSerializer createSerializer();
}
