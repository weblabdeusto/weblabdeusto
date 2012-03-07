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
*
*/

package es.deusto.weblab.client.lab.ui.themes.es.deusto.weblab.defaultmobile;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.ui.Grid;
import com.google.gwt.user.client.ui.HasHorizontalAlignment;
import com.google.gwt.user.client.ui.Image;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.Widget;
import com.google.gwt.user.client.ui.HTMLTable.Cell;

import es.deusto.weblab.client.configuration.IConfigurationManager;
import es.deusto.weblab.client.dto.experiments.ExperimentAllowed;
import es.deusto.weblab.client.dto.experiments.ExperimentID;
import es.deusto.weblab.client.dto.users.User;
import es.deusto.weblab.client.lab.experiments.ExperimentFactory;
import es.deusto.weblab.client.lab.experiments.ExperimentFactory.MobileSupport;
import es.deusto.weblab.client.lab.ui.themes.es.deusto.weblab.defaultmobile.LoggedPanel.ILoggedPanelCallback;
import es.deusto.weblab.client.ui.widgets.WlWaitingLabel;

class AllowedExperimentsWindow extends BaseWindow {

	interface AllowedExperimentsWindowUiBinder extends UiBinder<Widget, AllowedExperimentsWindow> {}

	private final AllowedExperimentsWindowUiBinder uiBinder = GWT.create(AllowedExperimentsWindowUiBinder.class);
	 

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
		this.loggedPanel = new LoggedPanel(user, callback, configurationManager);
	    this.experimentsAllowed = experimentsAllowed;
		
		super.loadWidgets();
		this.mainPanel.add(this.loggedPanel);
		
		try{
			final Widget wid = this.uiBinder.createAndBindUi(this);
		
			this.loggedPanel.contentPanel.clear();
			this.loggedPanel.contentPanel.add(wid);
		
			this.loadExperiments();
		}catch(final Exception e){
			e.printStackTrace();
		}
	}

	private void loadExperiments() {
		
		this.experimentsTable.resize(this.experimentsAllowed.length, 3);
		
		for(int i = 0; i < this.experimentsAllowed.length; ++i){
	    	final ExperimentAllowed experimentAllowed = this.experimentsAllowed[i];
	    	
	    	final ExperimentID experimentID = experimentAllowed.getExperiment().getExperimentUniqueName();
	    	final MobileSupport mobileSupport = ExperimentFactory.retrieveMobileSupport(experimentID);
	    	
    		final Label name        = new Label(experimentAllowed.getExperiment().getName());
    		final Label category    = new Label(experimentAllowed.getExperiment().getCategory().getCategory());
    		
    		name.setWidth("100%");
    		name.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_LEFT);
    		category.setWidth("100%");
    		category.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_RIGHT);
	    	
	    	final String currentStyle;
	    	if(i % 2 == 0)
	    		currentStyle = "odd-row";
	    	else
	    		currentStyle = "even-row";
	    	
	    	
	    	final Image img;
	    	final Resources res = GWT.create(Resources.class);
	    	switch(mobileSupport){
	    		case disabled:
	    			img = new Image(res.redBall());
	    			break;
	    		case full:
	    			img = new Image(res.greenBall());
	    			break;
	    		default:
	    			img = new Image(res.yellowBall());
	    	}
	    	img.setWidth("20px");
	    	
	    	this.experimentsTable.setWidget(i, 0, img);
	    	this.experimentsTable.setWidget(i, 1, name);
	    	this.experimentsTable.setWidget(i, 2, category);
	    	
	    	this.experimentsTable.getRowFormatter().setStyleName(i, currentStyle);
	    }
	}

	@UiHandler("experimentsTable")
	void onExperimentsTableClicked(ClickEvent event){
		final Cell cell = this.experimentsTable.getCellForEvent(event);
		final ExperimentAllowed expAllowed = this.experimentsAllowed[cell.getRowIndex()];
		this.callback.onChooseExperimentButtonClicked(expAllowed);
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
