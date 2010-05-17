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

package es.deusto.weblab.client.admin.ui.themes.es.deusto.weblab.defaultweb.i18n;

import com.google.gwt.i18n.client.Messages;

public interface IWebLabDeustoThemeMessages extends Messages {
	
	public String [] LANGUAGES = {
			"english",
			"castellano",
			"euskara"
	};

	// Must use the same order
	public String [] LANGUAGE_CODES = {
			"en",
			"es",
			"eu"
	};

	public String username();
	public String password();
	public String logIn();
	public String invalidUsernameOrPassword();
	public String loggingIn();
	public String thisFieldCantBeEmpty(String field);
	public String administrationPanel();
	public String logOut();
	public String accesses();
}
