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
* Author: FILLME
*
*/

package es.deusto.weblab.client;

import com.google.gwt.core.client.GWT;
import com.google.gwt.core.client.RunAsyncCallback;
import com.google.gwt.user.client.Window;

public class WebLabClientLab extends WebLabClient {

	public static final String DEMO_AVAILABLE_PROPERTY = "demo.available";
	public static final boolean DEFAULT_DEMO_AVAILABLE = false;
	
	public static final String DEMO_USERNAME_PROPERTY = "demo.username";
	public static final String DEFAULT_DEMO_USERNAME = "demo";
	
	public static final String DEMO_PASSWORD_PROPERTY = "demo.password";
	public static final String DEFAULT_DEMO_PASSWORD = "demo";
	
	@Override
	public void loadApplication() {
		GWT.runAsync(new RunAsyncCallback() {
			@Override
			public void onSuccess() {
				final WebLabLabLoader labLoader = new WebLabLabLoader(WebLabClientLab.this, WebLabClientLab.this.configurationManager);
				labLoader.loadLabApp();	
			}
			@Override
			public void onFailure(Throwable reason) {
				Window.alert("Failed to load lab");
			}
		});
	}

}
