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

package es.deusto.weblab.client.ui.themes.es.deusto.weblab.defaultmobile;

import es.deusto.weblab.client.configuration.IConfigurationManager;

class LoginWindow extends BaseWindow {
	
	interface ILoginWindowCallback {
		public void onLoginButtonClicked(String username, String password);
	}


	LoginWindow(IConfigurationManager configurationManager, ILoginWindowCallback callback) {
		super(configurationManager);
	}

}
