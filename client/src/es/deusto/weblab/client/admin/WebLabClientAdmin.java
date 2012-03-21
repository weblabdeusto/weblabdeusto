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

package es.deusto.weblab.client.admin;

import com.google.gwt.core.client.GWT;
import com.google.gwt.core.client.RunAsyncCallback;

import es.deusto.weblab.client.WebLabClient;

public class WebLabClientAdmin extends WebLabClient {

	@Override
	public void loadApplication() {
		GWT.runAsync(new RunAsyncCallback() {
			@Override
			public void onSuccess() {
				final WebLabAdminLoader adminLoader = new WebLabAdminLoader(WebLabClientAdmin.this, WebLabClientAdmin.this.configurationManager);
				adminLoader.loadAdminApp();
			}
			@Override
			public void onFailure(Throwable reason) {}
		});
	}
}



