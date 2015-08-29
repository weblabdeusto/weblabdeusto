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
*
*/ 
package es.deusto.weblab.client.lab.controller;

import es.deusto.weblab.client.lab.controller.IPollingHandler;
import es.deusto.weblab.client.testing.util.WebLabFake;

public class FakePollingHandler extends WebLabFake implements IPollingHandler {

	public static final String START = "start";
	public static final String STOP  = "stop";
	
	@Override
	public void start() {
		this.append(FakePollingHandler.START);
	}

	@Override
	public void stop() {
		this.append(FakePollingHandler.STOP);
	}

}
