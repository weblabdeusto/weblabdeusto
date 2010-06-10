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

package es.deusto.weblab.client.admin.ui;

import java.util.ArrayList;

import es.deusto.weblab.client.dto.experiments.Experiment;
import es.deusto.weblab.client.dto.experiments.ExperimentUse;
import es.deusto.weblab.client.dto.users.Group;
import es.deusto.weblab.client.dto.users.User;


public interface IUIManager {

	/*
	 * "Happy path" scenario
	 */
	public void onInit();
    public void onLoggedIn(User user);
	public void onLoggedOut();
	
	public void onGroupsRetrieved(ArrayList<Group> groups);
	public void onExperimentsRetrieved(ArrayList<Experiment> experiments);
	public void onExperimentUsesRetrieved(ArrayList<ExperimentUse> experimentUses);
	
	
	/*
	 * Alternative scenarios
	 */
	public void onWrongLoginOrPasswordGiven();
	public void onErrorAndFinishSession(String message);
	public void onError(String message);
}
