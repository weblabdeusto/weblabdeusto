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
import es.deusto.weblab.client.ui.widgets.EasyGrid;
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
	@UiField EasyGrid experimentUsesGrid;
	@UiField Button downloadButton;
	
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
    		toDate = new Date(this.toDateBox.getValue().getTime()+86399999); 
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
    	
    	this.showMessage("fromDate="+fromDate+", toDate="+toDate);
    	
    	this.experimentUses = this.callback.onSearchButtonClicked(fromDate, toDate, group, experiment);
    	this.experimentUsesGrid.clear();
    	/*for ( int i = 0; i < this.experimentUsesGrid.getRowCount(); i++ ) {
    		this.experimentUsesGrid.removeRow(i);
    	}*/
    	String debug = "";
    	for ( ExperimentUse eu: this.experimentUses ) {
    		this.experimentUsesGrid.add(new Label(DateTimeFormat.getMediumDateTimeFormat().format(eu.getStartTimestamp())));
    		this.experimentUsesGrid.add(new Label((eu.getEndTimestamp().getTime()-eu.getStartTimestamp().getTime())/1000 + ""));
    		this.experimentUsesGrid.add(new Label(eu.getUser().getLogin()));
    		this.experimentUsesGrid.add(new Label(eu.getUser().getFullName()));
    		this.experimentUsesGrid.add(new Label(eu.getExperiment().getUniqueName()));
    		debug += eu.getStartTimestamp()+"("+eu.getExperiment().getUniqueName()+")"+" | ";
    	}
    	this.showError(debug);
    	this.experimentUsesGrid.setRows(this.experimentUses.size()+1);
    	this.experimentUsesGrid.setCols(5);
    	
    	this.downloadButton.setVisible(this.experimentUses.size() > 0);
    }
}
