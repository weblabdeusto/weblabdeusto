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

package es.deusto.weblab.client.admin.ui.themes.es.deusto.weblab.defaultweb;

import java.util.ArrayList;
import java.util.Date;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.i18n.client.DateTimeFormat;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.ui.Anchor;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.Grid;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.ListBox;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;
import com.google.gwt.user.datepicker.client.DateBox;
import com.google.gwt.user.datepicker.client.DateBox.DefaultFormat;

import es.deusto.weblab.client.configuration.IConfigurationManager;
import es.deusto.weblab.client.dto.experiments.Experiment;
import es.deusto.weblab.client.dto.experiments.ExperimentUse;
import es.deusto.weblab.client.dto.users.Group;
import es.deusto.weblab.client.dto.users.User;
import es.deusto.weblab.client.ui.widgets.WlUtil;
import es.deusto.weblab.client.ui.widgets.WlWaitingLabel;

public class AdminPanelWindow extends BaseWindow {
	
	interface MyUiBinder extends UiBinder<Widget, AdminPanelWindow> {}
	private static MyUiBinder uiBinder = GWT.create(MyUiBinder.class);	

	public interface IAdminPanelWindowCallback {
		public void onLogoutButtonClicked();
		public ArrayList<Group> getGroups();
		public ArrayList<Experiment> getExperiments();
		public ArrayList<ExperimentUse> onSearchButtonClicked(Date fromDate, Date toDate, Group group, Experiment experiment);
	}	
	
	// Widgets
	@UiField VerticalPanel containerPanel;
	@UiField Label userLabel;
	@UiField Anchor logoutLink;
	@UiField WlWaitingLabel waitingLabel;
	@UiField Label generalErrorLabel;
	@UiField DateBox fromDateBox;
	@UiField DateBox toDateBox;
	@UiField ListBox groupConditionListBox;
	@UiField ListBox experimentConditionListBox;
	@UiField Button searchButton;
	@UiField Grid experimentUsesGrid;
	//@UiField Button downloadButton; // Future functionality
	
	private Label startedHeader;
	private Label timeHeader;
	private Label usernameHeader;
	private Label fullnameHeader;
	private Label experimentHeader;
	
	// Callbacks
	private final IAdminPanelWindowCallback callback;
	
	// DTOs
	private final User user;
	private ArrayList<Group> groups;
	private ArrayList<Experiment> experiments;
	private ArrayList<ExperimentUse> experimentUses;

	public AdminPanelWindow(IConfigurationManager configurationManager, User user, IAdminPanelWindowCallback callback) {
	    super(configurationManager);
	    
	    this.user = user;
	    this.callback = callback;
	    
	    this.loadWidgets();
	}	
	
	private void loadWidgets() {
		AdminPanelWindow.uiBinder.createAndBindUi(this);

		this.userLabel.setText(WlUtil.escapeNotQuote(this.user.getFullName()));
		
		this.fromDateBox.setFormat(new DefaultFormat(DateTimeFormat.getMediumDateFormat()));
		this.toDateBox.setFormat(new DefaultFormat(DateTimeFormat.getMediumDateFormat()));
		
		this.groups = this.callback.getGroups();
		this.groupConditionListBox.addItem("(any)"); // #i18n
		for ( Group group: this.groups ) {
			this.groupConditionListBox.addItem(group.getFullName() );
		}
		
		this.experiments = this.callback.getExperiments();
		this.experimentConditionListBox.addItem("(any)"); // #i18n
		for ( Experiment experiment: this.experiments ) {
			this.experimentConditionListBox.addItem(experiment.getUniqueName());
		}
		
		/* Future functionality
		this.groupedByListBox.addItem("(don't group)");
		this.groupedByListBox.addItem("User");
		this.groupedByListBox.addItem("Group");
		this.groupedByListBox.addItem("Experiment");
		*/
		
		/*
		 * We need to create the Grid this way because its UiBinder support is too limited right now.
		 * We will improve it when GWT 2.1 is released, which will provide better data presentation components.
		 */
		
		// #i18n
    	this.startedHeader = new Label("Started");
    	this.startedHeader.setStyleName("web-admin-logged-accesses-grid-header");
    	
    	this.timeHeader = new Label("Time");
    	this.timeHeader.setStyleName("web-admin-logged-accesses-grid-header");
    	
    	this.usernameHeader = new Label("Username");
    	this.usernameHeader.setStyleName("web-admin-logged-accesses-grid-header");
    	
    	this.fullnameHeader = new Label("User's full name");
    	this.fullnameHeader.setStyleName("web-admin-logged-accesses-grid-header");
    	
    	this.experimentHeader = new Label("Experiment");
    	this.experimentHeader.setStyleName("web-admin-logged-accesses-grid-header");
	}

	@Override
	Widget getWidget() {
		return this.containerPanel;
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

    @UiHandler("logoutLink")
	void onLogoutClicked(@SuppressWarnings("unused") ClickEvent ev) {
		this.callback.onLogoutButtonClicked();
	}
    
    @UiHandler("searchButton")
    void onSearchButtonClicked(@SuppressWarnings("unused") ClickEvent ev) {
    	Date fromDate = this.fromDateBox.getValue();
    	
    	Date toDate = this.toDateBox.getValue();
    	if ( toDate != null ) {
    		// We force the end of the day, because DateBox with this format gets 00:00:00.
    		toDate = new Date(toDate.getTime()+86399999); 
    	}
    	
    	int groupIndex = this.groupConditionListBox.getSelectedIndex();
    	Group group;
    	if ( groupIndex == 0 ) {
    		group = null;
    	} else {
    		group = this.groups.get(groupIndex-1);
    	}

    	int experimentIndex = this.experimentConditionListBox.getSelectedIndex();
    	Experiment experiment;
    	if ( experimentIndex == 0 ) {
    		experiment = null;
    	} else {
    		experiment = this.experiments.get(experimentIndex-1);
    	}
    	
    	this.experimentUses = this.callback.onSearchButtonClicked(fromDate, toDate, group, experiment);

    	this.experimentUsesGrid.clear();
    	this.experimentUsesGrid.resize(this.experimentUses.size()+1, 5);
    	
    	this.experimentUsesGrid.setWidget(0, 0, this.startedHeader);
    	this.experimentUsesGrid.setWidget(0, 1, this.timeHeader);
    	this.experimentUsesGrid.setWidget(0, 2, this.usernameHeader);
    	this.experimentUsesGrid.setWidget(0, 3, this.fullnameHeader);
    	this.experimentUsesGrid.setWidget(0, 4, this.experimentHeader);

        for (int row = 0; row < this.experimentUses.size(); row++) {
        	ExperimentUse eu = this.experimentUses.get(row);
      		this.experimentUsesGrid.setWidget(row+1, 0, new Label(DateTimeFormat.getMediumDateTimeFormat().format(eu.getStartTimestamp())));
    		this.experimentUsesGrid.setWidget(row+1, 1, new Label((eu.getEndTimestamp().getTime()-eu.getStartTimestamp().getTime())/1000 + ""));
    		this.experimentUsesGrid.setWidget(row+1, 2, new Label(eu.getUser().getLogin()));
    		this.experimentUsesGrid.setWidget(row+1, 3, new Label(eu.getUser().getFullName()));
    		this.experimentUsesGrid.setWidget(row+1, 4, new Label(eu.getExperiment().getUniqueName()));
        }

    	// Future functionality:
    	//this.downloadButton.setVisible(this.experimentUses.size() > 0);
    }
}
