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
* Author: Pablo Orduña <pablo@ordunya.com>
*         Jaime Irurzun <jaime.irurzun@gmail.com>
*
*/

package es.deusto.weblab.client.admin.controller;

import es.deusto.weblab.client.admin.ui.IUIManager;
import es.deusto.weblab.client.dto.SessionID;

public interface IWlAdminController {
	
	void login(String username, String password);
	void startLoggedIn(SessionID sessionId);
	void logout();

	void setUIManager(IUIManager theme);
}
