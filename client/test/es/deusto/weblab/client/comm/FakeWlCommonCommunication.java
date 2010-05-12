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

package es.deusto.weblab.client.comm;

import es.deusto.weblab.client.comm.callbacks.ISessionIdCallback;
import es.deusto.weblab.client.testing.util.WlFake;

public abstract class FakeWlCommonCommunication extends WlFake implements IWlCommonCommunication {
	
	public static final String LOGIN                  = "FakeWebLabCommunication::login";
	
	@Override
	public void login(String username, String password, ISessionIdCallback callback) {
		this.append(FakeWlCommonCommunication.LOGIN, new Object[]{
				username,
				password,
				callback
		});
	}
	
	protected abstract IWlCommonSerializer createSerializer();
}
