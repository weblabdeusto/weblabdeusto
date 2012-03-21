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

	private static String ADMIN_URL_PARAM = "admin";
	
	private boolean wantsAdminApp(){
		final String urlSaysWantsAdminApp = Window.Location.getParameter(WebLabClientLab.ADMIN_URL_PARAM);
		return urlSaysWantsAdminApp != null && (urlSaysWantsAdminApp.toLowerCase().equals("yes") || urlSaysWantsAdminApp.toLowerCase().equals("true")); 
	}
	
	@Override
	public void loadApplication() {
		if(wantsAdminApp())
			Window.Location.replace(INDEX_ADMIN_HTML);
			
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
