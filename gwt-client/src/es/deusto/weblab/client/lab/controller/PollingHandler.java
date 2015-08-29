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

import com.google.gwt.user.client.Timer;

import es.deusto.weblab.client.configuration.IConfigurationManager;

//TODO this class shouldn't use petitionsManager. Instead, it should use directly the comm manager, and it should tell the controller that it has been disconnected as soon as it find it out
public class PollingHandler implements IPollingHandler {
	
	private final static String POLLING_TIME_PROPERTY = "polling.time";
	private final static int DEFAULT_POLLING_TIME = 5000; //5 seconds
	
	private Timer pollingTimer;
	private final IConfigurationManager configurationManager;
	private ILabController controller;
	
	public PollingHandler(IConfigurationManager configurationManager){
		this.configurationManager = configurationManager;
	}
	
	public void setController(ILabController controller){
		this.controller = controller;
	}
	
	@Override
	public void start(){
		if(this.pollingTimer != null)
			this.pollingTimer.cancel();
		
		this.pollingTimer = new Timer(){
			@Override
			public void run(){
				PollingHandler.this.controller.poll();
			}
		};
		
		final int pollingTime = this.configurationManager.getIntProperty(
							PollingHandler.POLLING_TIME_PROPERTY, 
							PollingHandler.DEFAULT_POLLING_TIME
					);
		this.pollingTimer.scheduleRepeating(pollingTime);
	}
	
	@Override
	public void stop(){
		if(this.pollingTimer != null){
			this.pollingTimer.cancel();
			this.pollingTimer = null;
		}
	}
}
