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

import com.google.gwt.user.client.ui.Grid;
import com.google.gwt.user.client.ui.Label;

import es.deusto.weblab.client.configuration.IConfigurationManager;
import es.deusto.weblab.client.dto.experiments.ExperimentAllowed;
import es.deusto.weblab.client.dto.users.User;
import es.deusto.weblab.client.ui.themes.es.deusto.weblab.defaultmobile.LoggedPanel.ILoggedPanelCallback;
import es.deusto.weblab.client.ui.widgets.WlVerticalPanel;

class AllowedExperimentsWindow extends BaseWindow {

	// DTOs
	private final ExperimentAllowed [] experimentsAllowed;
	
	// Logged panel
	private final LoggedPanel loggedPanel;
	private final WlVerticalPanel contentPanel;
	
	private final IAllowedExperimentsWindowCallback callback;
	
	interface IAllowedExperimentsWindowCallback extends ILoggedPanelCallback {
		public void onChooseExperimentButtonClicked(ExperimentAllowed experimentAllowed);
	}
	
	public AllowedExperimentsWindow(IConfigurationManager configurationManager,
			User user, ExperimentAllowed[] experimentsAllowed,
			IAllowedExperimentsWindowCallback callback) {
		super(configurationManager);
		
	    this.callback = callback;
		this.loggedPanel = new LoggedPanel(user, callback);
		this.contentPanel = this.loggedPanel.contentPanel;
	    this.experimentsAllowed = experimentsAllowed;
		
		super.loadWidgets();
		this.mainPanel.add(this.loggedPanel);
		
		final Grid grid = new Grid(experimentsAllowed.length, 3);
		this.mainPanel.add(grid);
		
	    for(int i = 0; i < experimentsAllowed.length; ++i){
	    	final ExperimentAllowed experimentAllowed = experimentsAllowed[i];
	    	
	    	final Label name = new Label(experimentAllowed.getExperiment().getName());
	    	final Label category = new Label(experimentAllowed.getExperiment().getCategory().getCategory());
	    	grid.setWidget(i, 0, name);
	    	grid.setWidget(i, 1, category);
	    }
	}
	
	@Override
	void showError(String message) {
		// TODO Auto-generated method stub
		
	}
	
	@Override
	void showMessage(String message) {
		// TODO Auto-generated method stub
		
	}

}
