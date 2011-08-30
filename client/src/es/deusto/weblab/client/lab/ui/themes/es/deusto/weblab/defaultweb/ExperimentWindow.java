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
*
*/ 
package es.deusto.weblab.client.lab.ui.themes.es.deusto.weblab.defaultweb;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.ui.AbsolutePanel;
import com.google.gwt.user.client.ui.Anchor;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.Grid;
import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;

import es.deusto.weblab.client.HistoryProperties;
import es.deusto.weblab.client.configuration.IConfigurationManager;
import es.deusto.weblab.client.dto.experiments.ExperimentAllowed;
import es.deusto.weblab.client.dto.users.User;
import es.deusto.weblab.client.lab.ui.BoardBase;
import es.deusto.weblab.client.ui.widgets.WlUtil;
import es.deusto.weblab.client.ui.widgets.WlWaitingLabel;



/**
 * Window that displays basic information about a selected experiment and 
 * lets the user Reserve it.
 */
class ExperimentWindow extends BaseWindow {
	
	interface MyUiBinder extends UiBinder<Widget, ExperimentWindow> {}
	private static MyUiBinder uiBinder = GWT.create(MyUiBinder.class);

	public interface IExperimentWindowCallback {
		public boolean startedLoggedIn();
		public void onLogoutButtonClicked();
		public void onBackButtonClicked();
		public void onReserveButtonClicked();
		public void onFinishButtonClicked();
	}

	// Widgets
	@UiField VerticalPanel containerPanel;
	@UiField Label userLabel;
	@UiField Anchor logoutLink;
	@UiField AbsolutePanel navigationPanel;
	@UiField Anchor backLink;
	@UiField VerticalPanel experimentAreaPanel;
	@UiField Label contentTitleLabel;
	@UiField Grid detailsGrid;
	@UiField Label experimentNameLabel;
	@UiField Label experimentCategoryLabel;
	@UiField Label timeAllowedLabel;
	@UiField Button reserveButton;
	@UiField Button finishButton;
	@UiField WlWaitingLabel waitingLabel;
	@UiField Label generalErrorLabel;
	@UiField Label separatorLabel;
	@UiField Label separatorLabel2;
	@UiField HorizontalPanel headerPanel;

	// Callbacks
	private final IExperimentWindowCallback callback;

	// Properties
	private static final String ADMIN_EMAIL_PROPERTY = "admin.email";
	private static final String DEFAULT_ADMIN_EMAIL = "<admin.email not set>";
    
	// DTOs
	private final User user;
	private final ExperimentAllowed experimentAllowed;
	private final BoardBase experimentBase;
    
	public ExperimentWindow(IConfigurationManager configurationManager, User user, ExperimentAllowed experimentAllowed, BoardBase experimentBase, IExperimentWindowCallback callback){
	    super(configurationManager);
	
	    this.user = user;
	    this.experimentAllowed = experimentAllowed;
	    this.experimentBase = experimentBase;	
	    this.callback = callback;
	    
	    this.loadWidgets();
	}

	@Override
	public Widget getWidget(){
		return this.containerPanel;
	}	
	
    @Override
	public void showError(String message){
		this.generalErrorLabel.setText(message);
	}

	public void loadWidgets(){		
		ExperimentWindow.uiBinder.createAndBindUi(this);
		
		final boolean visibleHeader = HistoryProperties.getBooleanValue(HistoryProperties.HEADER_VISIBLE, true);
	    this.headerPanel.setVisible(visibleHeader);
	    this.navigationPanel.setVisible(visibleHeader);
	    
		this.userLabel.setText(WlUtil.escapeNotQuote(this.user.getFullName()));
		
	    if(this.callback.startedLoggedIn()){
	    	this.logoutLink.setVisible(false);
	    	this.separatorLabel.setVisible(false);
	    	this.separatorLabel2.setVisible(false);
	    }
	}
	
	public void loadExperimentReservationPanels() {	    
		this.experimentNameLabel.setText(this.experimentAllowed.getExperiment().getName());
		this.experimentCategoryLabel.setText(this.experimentAllowed.getExperiment().getCategory().getCategory());
		this.timeAllowedLabel.setText(this.experimentAllowed.getTimeAllowed()+"");

		// Important note: this MUST be done here or FileUpload will cause problems
		this.experimentAreaPanel.add(this.experimentBase.getWidget());	
		this.experimentBase.initialize();
		// end of Important note
	}

	public void loadUsingExperimentPanels(int time, String initialConfiguration) {
	    this.contentTitleLabel.setText(this.experimentAllowed.getExperiment().getName());
	    this.detailsGrid.setVisible(false);
	    this.waitingLabel.stop();
	    this.waitingLabel.setText("");
	    this.reserveButton.setVisible(false);
		this.finishButton.setVisible(true);

	    // Important note: This can't be before adding the widget to the DOM tree 
		// If it's done, applets will not work 
		this.experimentBase.start(time, initialConfiguration);
		this.experimentBase.setTime(time);
		// end of Important note
	}	

	@UiHandler("backLink")
	void onBackLinkClicked(@SuppressWarnings("unused") ClickEvent ev) {
		this.callback.onBackButtonClicked();	
	}	
	
	@UiHandler("logoutLink")
	void onLogoutLinkClicked(@SuppressWarnings("unused") ClickEvent ev) {
		this.callback.onLogoutButtonClicked();
	}	

	@UiHandler("reserveButton")
	void onReserveButtonClicked(@SuppressWarnings("unused") ClickEvent ev) {
		this.reserveButton.setEnabled(false);
		this.backLink.setVisible(false);
		this.waitingLabel.setText(ExperimentWindow.this.i18nMessages.reserving());
		this.waitingLabel.start();
		this.callback.onReserveButtonClicked();	
	}	

	@UiHandler("finishButton")
	void onFinishButtonClicked(@SuppressWarnings("unused") ClickEvent ev) {
		this.callback.onFinishButtonClicked();		
	}	
	
    @Override
	public void showMessage(String message) {
		this.generalErrorLabel.setText(message);
	}

    public void showWaitingInstances(int position) {
    	this.waitingLabel.setText(
    			this.i18nMessages.waitingForAnInstancePosition(
    					this.configurationManager.getProperty(
    							ExperimentWindow.ADMIN_EMAIL_PROPERTY,
    							ExperimentWindow.DEFAULT_ADMIN_EMAIL
    					),
    					position
    			)
    	);
    }

	public void showWaitingReservation(int position) {
	    	this.waitingLabel.setText(this.i18nMessages.waitingInQueuePosition(position));
	}

	public void showWaitingReservationConfirmation() {
	    	this.waitingLabel.setText(this.i18nMessages.waitingForConfirmation());
	}
}
