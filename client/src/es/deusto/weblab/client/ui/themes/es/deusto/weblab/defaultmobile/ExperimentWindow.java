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
import es.deusto.weblab.client.experiments.ExperimentBase;
import es.deusto.weblab.client.ui.BoardBase;
import es.deusto.weblab.client.ui.themes.es.deusto.weblab.defaultmobile.LoggedPanel.ILoggedPanelCallback;
import es.deusto.weblab.client.ui.themes.es.deusto.weblab.defaultmobile.widgets.EasyGrid;
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
	@UiField EasyGrid grid;
	@UiField WlWaitingLabel waitingLabel;
	@UiField Button reserveButton;
	@UiField Label generalErrorLabel;
	
	@UiField Label experimentName;
	@UiField Label experimentCategory;
	@UiField Label timeAllowed;
	
	// Logged panel
	private LoggedPanel loggedPanel;
	
	// DTOs
	private final ExperimentAllowed experimentAllowed;
	private final ExperimentBase experimentBase;
	private final BoardBase boardBase;
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
		this.boardBase         = experimentBase.getUI();
		this.callback          = callback;
		this.user              = user;
		
		this.loadWidgets();
	}

	void loadExperimentReservationPanels() {	    
		
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
		this.experimentArea.add(this.boardBase.getWidget());	
		this.boardBase.initialize();
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
	
	public void loadUsingExperimentPanels(int time) {
		/*
	    while ( this.preExperimentAreaPanel.getWidgetCount() > 0)
		this.preExperimentAreaPanel.remove(0);
	    while ( this.postExperimentAreaPanel.getWidgetCount() > 0)
		this.postExperimentAreaPanel.remove(0);
	    
		AbsolutePanel navigationPanel = new AbsolutePanel();
		navigationPanel.setSize("100%", "30px");
		this.preExperimentAreaPanel.add(navigationPanel);
		
		final Label contentTitleLabel = new Label(this.experimentAllowed.getExperiment().getName());
		contentTitleLabel.setStyleName("title-label");				
		this.preExperimentAreaPanel.add(contentTitleLabel);

		// This can't be before adding the widget to the DOM tree 
		// If it's done, applets will not work 
		this.experimentBase.getUI().start();
		this.experimentBase.getUI().setTime(time);
		
		this.postExperimentAreaPanel.add(new HTML("&nbsp;"));
		
		this.finishButton = new Button(this.i18nMessages.finish());		
		this.finishButton.addClickHandler(new ClickHandler() {
		    @Override
		    public void onClick(ClickEvent sender) {
			ExperimentWindow.this.callback.onFinishButtonClicked();			
		    }
		});
		this.postExperimentAreaPanel.add(this.finishButton);
		this.postExperimentAreaPanel.setCellHorizontalAlignment(this.finishButton, HasHorizontalAlignment.ALIGN_CENTER);
		*/
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
}
