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

import com.google.gwt.core.client.GWT;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.ui.Anchor;
import com.google.gwt.user.client.ui.FlexTable;
import com.google.gwt.user.client.ui.Grid;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.Widget;

import es.deusto.weblab.client.configuration.IConfigurationManager;
import es.deusto.weblab.client.dto.experiments.ExperimentAllowed;
import es.deusto.weblab.client.dto.users.User;
import es.deusto.weblab.client.ui.themes.es.deusto.weblab.defaultmobile.LoggedPanel.ILoggedPanelCallback;
import es.deusto.weblab.client.ui.widgets.WlVerticalPanel;
import es.deusto.weblab.client.ui.widgets.WlWaitingLabel;

class AllowedExperimentsWindow extends BaseWindow {

	interface AllowedExperimentsWindowUiBinder extends UiBinder<Widget, AllowedExperimentsWindow> {}

	private final AllowedExperimentsWindowUiBinder uiBinder = GWT.create(AllowedExperimentsWindowUiBinder.class);

	@UiField Label contentTitleLabel;
	@UiField WlWaitingLabel waitingLabel;
	@UiField Label generalErrorLabel;
	@UiField Grid experimentsTable;
	
	// DTOs
	private final ExperimentAllowed [] experimentsAllowed;
	
	// Logged panel
	private final LoggedPanel loggedPanel;
	
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
	    this.experimentsAllowed = experimentsAllowed;
		
		super.loadWidgets();
		this.mainPanel.add(this.loggedPanel);
		
		try{
			final Widget wid = this.uiBinder.createAndBindUi(this);
			this.contentTitleLabel.setText(this.i18nMessages.myExperiments());
		
			this.mainPanel.add(wid);
		
			loadExperiments();
		}catch(Exception e){
			e.printStackTrace();
		}
	}

	private void loadExperiments() {
    	this.experimentsTable.resize(this.experimentsAllowed.length, 2);
		
		for(int i = 0; i < this.experimentsAllowed.length; ++i){
	    	final ExperimentAllowed experimentAllowed = this.experimentsAllowed[i];
	    	
	    	final Label name        = new Label(experimentAllowed.getExperiment().getName());
	    	final Label category    = new Label(experimentAllowed.getExperiment().getCategory().getCategory());
	    	
	    	final String currentStyle;
	    	if(i % 2 == 0)
	    		currentStyle = "odd-row";
	    	else
	    		currentStyle = "even-row";
	    	
	    	name.setStylePrimaryName(currentStyle);
	    	category.setStylePrimaryName(currentStyle);
	    	
	    	this.experimentsTable.setWidget(i, 0, name);
	    	this.experimentsTable.setWidget(i, 1, category);
	    }
	}
	
	@Override
	void showError(String message) {
		this.generalErrorLabel.setText(message);
		this.waitingLabel.stop();
		this.waitingLabel.setText("");
	}
	
	@Override
	void showMessage(String message) {
		this.generalErrorLabel.setText(message);
	}

}
