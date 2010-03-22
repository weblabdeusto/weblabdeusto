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
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.ui.Anchor;
import com.google.gwt.user.client.ui.HasHorizontalAlignment;
import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.Image;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;

import es.deusto.weblab.client.configuration.IConfigurationManager;
import es.deusto.weblab.client.dto.experiments.ExperimentAllowed;
import es.deusto.weblab.client.dto.experiments.ExperimentID;
import es.deusto.weblab.client.dto.users.User;
import es.deusto.weblab.client.experiments.ExperimentFactory;
import es.deusto.weblab.client.experiments.ExperimentFactory.MobileSupport;
import es.deusto.weblab.client.ui.themes.es.deusto.weblab.defaultmobile.LoggedPanel.ILoggedPanelCallback;
import es.deusto.weblab.client.ui.widgets.WlWaitingLabel;

class AllowedExperimentsWindow extends BaseWindow {

	interface AllowedExperimentsWindowUiBinder extends UiBinder<Widget, AllowedExperimentsWindow> {}

	private final AllowedExperimentsWindowUiBinder uiBinder = GWT.create(AllowedExperimentsWindowUiBinder.class);
	 

	@UiField Label contentTitleLabel;
	@UiField WlWaitingLabel waitingLabel;
	@UiField Label generalErrorLabel;
	@UiField VerticalPanel experimentsTable;
	
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
		for(int i = 0; i < this.experimentsAllowed.length; ++i){
	    	final ExperimentAllowed experimentAllowed = this.experimentsAllowed[i];
	    	
	    	final ExperimentID experimentID = experimentAllowed.getExperiment().getExperimentID();
	    	final MobileSupport mobileSupport = ExperimentFactory.retrieveMobileSupport(experimentID);
	    	
	    	final Widget name;
	    	final Widget category;
	    	
	    	if(mobileSupport == MobileSupport.disabled){
	    		final Label lname        = new Label(experimentAllowed.getExperiment().getName());
	    		final Label lcategory    = new Label(experimentAllowed.getExperiment().getCategory().getCategory());
	    		
	    		lname.setWidth("100%");
	    		lname.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_LEFT);
	    		lcategory.setWidth("100%");
	    		lcategory.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_RIGHT);
	    		
	    		name     = lname;
	    		category = lcategory;
	    	}else{
	    		final Anchor aname        = new Anchor(experimentAllowed.getExperiment().getName());
	    		final Anchor acategory    = new Anchor(experimentAllowed.getExperiment().getCategory().getCategory());
	    		
	    		aname.setWidth("100%");
	    		aname.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_LEFT);
	    		acategory.setWidth("100%");
	    		acategory.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_RIGHT);
	    		
	    		name     = aname;
	    		category = acategory;
	    		
	    		final ClickHandler clickHandler = new ClickHandler() {
					@Override
					public void onClick(ClickEvent event) {
						AllowedExperimentsWindow.this.callback.onChooseExperimentButtonClicked(experimentAllowed);
					}
				};
				
				aname.addClickHandler(clickHandler);
				acategory.addClickHandler(clickHandler);
	    	}
	    	
	    	final String currentStyle;
	    	if(i % 2 == 0)
	    		currentStyle = "odd-row";
	    	else
	    		currentStyle = "even-row";
	    	
	    	
	    	final HorizontalPanel row = new HorizontalPanel();
	    	row.setStyleName(currentStyle);
	    	row.setWidth("100%");
	    	row.setSpacing(10);
	    	row.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_LEFT);
	    	
	    	final Image img;
	    	
	    	switch(mobileSupport){
	    		case disabled:
	    			img = new Image(Resources.INSTANCE.redBall());
	    			break;
	    		case full:
	    			img = new Image(Resources.INSTANCE.greenBall());
	    			break;
	    		default:
	    			img = new Image(Resources.INSTANCE.yellowBall());
	    	}
	    	
	    	img.setWidth("100%");
	    	
	    	row.add(img);
	    	row.add(name);
	    	row.add(category);
	    	
	    	this.experimentsTable.add(row);
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
