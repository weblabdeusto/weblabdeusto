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
*         Jaime Irurzun <jaime.irurzun@gmail.com>
*
*/

package es.deusto.weblab.client.admin.ui;

import es.deusto.weblab.client.dto.SessionID;
import es.deusto.weblab.client.dto.users.User;


public interface IUIManager {

	/*
	 * "Happy path" scenario
	 */
	public void onInit();
    public void onLoggedIn(User user, SessionID sessionId);
	public void onLoggedOut();
	
	/*
	 * Alternative scenarios
	 */
	public void onWrongLoginOrPasswordGiven();
	public void onNotAllowedToAccessAdminPanel();
	public void onErrorAndFinishSession(String message);
	public void onError(String message);
}
