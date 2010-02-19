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
package es.deusto.weblab.client.ui.themes.es.deusto.weblab.defaulttheme;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiTemplate;
import com.google.gwt.user.client.ui.AbsolutePanel;
import com.google.gwt.user.client.ui.Anchor;
import com.google.gwt.user.client.ui.FlexTable;
import com.google.gwt.user.client.ui.Grid;
import com.google.gwt.user.client.ui.HasHorizontalAlignment;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.Widget;
import com.google.gwt.user.client.ui.HasHorizontalAlignment.HorizontalAlignmentConstant;

import es.deusto.weblab.client.configuration.IConfigurationManager;
import es.deusto.weblab.client.dto.experiments.ExperimentAllowed;
import es.deusto.weblab.client.dto.users.User;
import es.deusto.weblab.client.ui.themes.es.deusto.weblab.defaulttheme.LoggedPanel.ILoggedPanelCallback;
import es.deusto.weblab.client.ui.themes.es.deusto.weblab.defaulttheme.LoginWindow.MyUiBinder;
import es.deusto.weblab.client.ui.themes.es.deusto.weblab.defaulttheme.i18n.IWebLabDeustoThemeMessages;
import es.deusto.weblab.client.ui.widgets.WlHorizontalPanel;
import es.deusto.weblab.client.ui.widgets.WlVerticalPanel;
import es.deusto.weblab.client.ui.widgets.WlWaitingLabel;

public class AllowedExperimentsWindow extends BaseWindow {

	interface AllowedExperimentsWindowUiBinder extends 
		UiBinder<Widget, AllowedExperimentsWindow> {
	}

	private static AllowedExperimentsWindowUiBinder uiBinder = 
		GWT.create(AllowedExperimentsWindowUiBinder.class);
	
	
	public interface IAllowedExperimentsWindowCallback extends ILoggedPanelCallback {
		public void onChooseExperimentButtonClicked(ExperimentAllowed experimentAllowed);
	}
	
	// Widgets
	@UiField AbsolutePanel navigationPanel;
	@UiField Label contentTitleLabel;
	@UiField WlWaitingLabel waitingLabel;
	@UiField Label generalErrorLabel;
	@UiField WlVerticalPanel listExperimentsPanel;
	@UiField FlexTable experimentsTable;

	// DTOs
	private final ExperimentAllowed [] experimentsAllowed;
	
	// Logged panel
	private final LoggedPanel loggedPanel;
	private final WlVerticalPanel contentPanel;
	
	private final IAllowedExperimentsWindowCallback callback;

	
	public AllowedExperimentsWindow(IConfigurationManager configurationManager, User user, ExperimentAllowed[] experimentsAllowed, IAllowedExperimentsWindowCallback callback) {
	    super(configurationManager);
	    
	    this.callback = callback;
		loggedPanel = new LoggedPanel(user, callback);
		contentPanel = loggedPanel.contentPanel;
	    this.experimentsAllowed = experimentsAllowed;
	    
	    this.loadWidgets();	    
	}
	
	
	/**
	 * Dynamically generates the content of the experiments table, using
	 * the UiBinder-created experimentsTable FlexTable.
	 */
	protected void generateExperimentsTableContent() {
		
		final Label experimentCategoryHeader = new Label(this.i18nMessages.experimentCategory());
		experimentCategoryHeader.setStyleName("table-header");
		final Label experimentNameHeader = new Label(this.i18nMessages.experimentName());
		experimentNameHeader.setStyleName("table-header");
		experimentsTable.setWidget(0, 0, experimentCategoryHeader);
		experimentsTable.setWidget(0, 1, experimentNameHeader);
		experimentsTable.setWidget(0, 2, new Label(""));
		
		for(int i = 0; i < this.experimentsAllowed.length; ++i){
			final String category = this.experimentsAllowed[i].getExperiment().getCategory().getCategory();
			
			final Anchor nameLink = new Anchor(this.experimentsAllowed[i].getExperiment().getName());
			nameLink.addClickHandler(new ExperimentClickListener(i));

			experimentsTable.setWidget(i + 1, 0, new Label(category));
			experimentsTable.setWidget(i + 1, 1, nameLink);
		}
		
		while(listExperimentsPanel.getWidgetCount() > 0)
			listExperimentsPanel.remove(0);
		listExperimentsPanel.add(experimentsTable);
		
	}
	
	
	/**
	 * Do those widget initialization things that are not done from UiBinder.
	 */
	protected void setupWidgets()  {
		
		// TODO: Find out whether we can somehow call a two-parameters 
		// setter from UiBinder to replace this statement.
		navigationPanel.setSize("100%", "30px");
		
		contentTitleLabel.setText(this.i18nMessages.myExperiments());
		this.contentPanel.setCellHeight(contentTitleLabel, "40px");
		
		generateExperimentsTableContent();
	}

	protected void loadWidgets(){
		super.loadWidgets();
		
		this.mainPanel.add(loggedPanel);
		
		
		// Note: At the moment, the whole UiBinder UI of this window
		// goes into LoggedPanel's contentPanel.
	    final Widget wid = uiBinder.createAndBindUi(this);
	    this.contentPanel.add(wid);

	    this.setupWidgets();
	}
	
    public void showError(String message) {
        this.generalErrorLabel.setText(message);
        this.waitingLabel.stop();
        this.waitingLabel.setText("");
    }	
	
	public void showMessage(String message) {
		this.generalErrorLabel.setText(message);
	}
	
	private class ExperimentClickListener implements ClickHandler
	{
		private final int number;
		
		public ExperimentClickListener(int n) {
			this.number = n;
		}
		
		@Override
		public void onClick(ClickEvent event) {
			final ExperimentAllowed ea = AllowedExperimentsWindow.this.experimentsAllowed[this.number];
			callback.onChooseExperimentButtonClicked(ea);
		}
	}	
}
