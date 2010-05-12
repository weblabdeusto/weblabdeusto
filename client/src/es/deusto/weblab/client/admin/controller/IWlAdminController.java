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

package es.deusto.weblab.client.admin.controller;

import es.deusto.weblab.client.admin.ui.WlAdminThemeBase;
import es.deusto.weblab.client.dto.SessionID;

public interface IWlAdminController {

	void setUIManager(WlAdminThemeBase theme);

	void startLoggedIn(SessionID sessionID);
}
