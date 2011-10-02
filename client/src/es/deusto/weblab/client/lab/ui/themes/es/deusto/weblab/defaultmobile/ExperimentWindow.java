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

package es.deusto.weblab.client.lab.ui.themes.es.deusto.weblab.defaultmobile;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.ui.Anchor;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;

import es.deusto.weblab.client.configuration.IConfigurationManager;
import es.deusto.weblab.client.dto.experiments.ExperimentAllowed;
import es.deusto.weblab.client.dto.users.User;
import es.deusto.weblab.client.lab.experiments.ExperimentBase;
import es.deusto.weblab.client.lab.ui.themes.es.deusto.weblab.defaultmobile.LoggedPanel.ILoggedPanelCallback;
import es.deusto.weblab.client.ui.widgets.WlWaitingLabel;

class ExperimentWindow extends BaseWindow {

	public interface IExperimentWindowCallback extends ILoggedPanelCallback {
		public void onBackButtonClicked();
		public void onReserveButtonClicked();
		public void onFinishButtonClicked();
	}

	interface ExperimentWindowUiBinder extends UiBinder<Widget, ExperimentWindow> {
	}

	private final ExperimentWindowUiBinder uiBinder = GWT.create(ExperimentWindowUiBinder.class);
	
	private static final String ADMIN_EMAIL_PROPERTY = "admin.email";
	private static final String DEFAULT_ADMIN_EMAIL = "<admin.email not set>";
    
	@UiField VerticalPanel experimentArea;
	@UiField Anchor back;
	@UiField WlWaitingLabel waitingLabel;
	@UiField Button reserveButton;
	@UiField Label generalErrorLabel;
	
	@UiField Label reserveExperimentLabel;
	@UiField Label selectedExperimentLabel;
	
	@UiField Label experimentName;
	@UiField Label experimentCategory;
	@UiField Label timeAllowed;
	@UiField VerticalPanel upperSide;
	@UiField VerticalPanel reserveSide;
	@UiField VerticalPanel finishSide;
	
	// Logged panel
	private LoggedPanel loggedPanel;
	
	// DTOs
	private final ExperimentAllowed experimentAllowed;
	private final ExperimentBase experimentBase;
	private final User user;	
	
	// Callback
	private final IExperimentWindowCallback callback;
	
	public ExperimentWindow(IConfigurationManager configurationManager,
			User user, ExperimentAllowed experimentAllowed,
			ExperimentBase experimentBase,
			IExperimentWindowCallback callback) {
		super(configurationManager);

		this.experimentAllowed = experimentAllowed;
		this.experimentBase    = experimentBase;
		this.callback          = callback;
		this.user              = user;
		
		this.loadWidgets();
	}

	void loadExperimentReservationPanels(boolean reserved) {	    
		if(reserved){
			this.reserveButton.setVisible(false);
			this.waitingLabel.start();
			this.selectedExperimentLabel.setVisible(true);
			this.reserveExperimentLabel.setVisible(false);
		}else{
			this.selectedExperimentLabel.setVisible(false);
			this.reserveExperimentLabel.setVisible(true);
		}
		
		this.loggedPanel = new LoggedPanel(this.user, this.callback);
		this.mainPanel.add(this.loggedPanel);

		final Widget wid = this.uiBinder.createAndBindUi(this);
		this.loggedPanel.contentPanel.clear();
		this.loggedPanel.contentPanel.add(wid);
		
		this.experimentName.setText(this.experimentAllowed.getExperiment().getName());
		this.experimentCategory.setText(this.experimentAllowed.getExperiment().getCategory().getCategory());
		this.timeAllowed.setText("" + this.experimentAllowed.getTimeAllowed());
		
		// Important note: this order is important. Otherwise the FileUpload will cause problems
		this.experimentArea.clear();
		this.experimentArea.add(this.experimentBase.getWidget());	
		// end of Important note
	}
	
	@UiHandler("back")
	void onBackClicked(@SuppressWarnings("unused") ClickEvent event){
		ExperimentWindow.this.callback.onBackButtonClicked();
	}
	
	@UiHandler("reserveButton")
	void onReserveButtonClicked(@SuppressWarnings("unused") ClickEvent event){
    	this.reserveButton.setEnabled(false);
    	this.back.setVisible(false);
    	this.waitingLabel.setText(ExperimentWindow.this.i18nMessages.reserving());
    	this.waitingLabel.start();
    	this.callback.onReserveButtonClicked();
	}
	
	@Override
	void showError(String message) {
		this.generalErrorLabel.setText(message);
	}

	@Override
	void showMessage(String message) {
		this.generalErrorLabel.setText(message);
	}
	
	public void loadUsingExperimentPanels() {
		
		this.upperSide.setVisible(false);
		this.reserveSide.setVisible(false);
		this.finishSide.setVisible(true);
	    
	}
	
	@UiHandler("finishButton")
	void onFinishButtonClicked(@SuppressWarnings("unused") ClickEvent event){
		this.callback.onFinishButtonClicked();
	}
	
	void showWaitingInstances(int position) {
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
	
	void showWaitingReservation(int position) {
		this.waitingLabel.setText(this.i18nMessages.waitingInQueuePosition(position));
	}

	void showWaitingReservationConfirmation() {
		this.waitingLabel.setText(this.i18nMessages.waitingForConfirmation());
	}

	public void onExperimentInteractionFinished() {
		this.mainPanel.clear();
		this.mainPanel.add(new ExperimentFinishedWindow());
	}
}
