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
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.i18n.client.DateTimeFormat;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.Command;
import com.google.gwt.user.client.ui.Anchor;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.FlexTable;
import com.google.gwt.user.client.ui.Grid;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.ListBox;
import com.google.gwt.user.client.ui.MenuItem;
import com.google.gwt.user.client.ui.TextBox;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;
import com.google.gwt.user.client.ui.HTMLTable.Cell;
import com.google.gwt.user.client.ui.HTMLTable.CellFormatter;
import com.google.gwt.user.datepicker.client.DateBox;
import com.google.gwt.user.datepicker.client.DateBox.DefaultFormat;

import es.deusto.weblab.client.configuration.IConfigurationManager;
import es.deusto.weblab.client.dto.experiments.Experiment;
import es.deusto.weblab.client.dto.experiments.ExperimentUse;
import es.deusto.weblab.client.dto.users.ExternalEntity;
import es.deusto.weblab.client.dto.users.Group;
import es.deusto.weblab.client.dto.users.User;
import es.deusto.weblab.client.ui.widgets.WlUtil;
import es.deusto.weblab.client.ui.widgets.WlWaitingLabel;

public class AdminPanelWindow extends BaseWindow {
	
	interface MyUiBinder extends UiBinder<Widget, AdminPanelWindow> {}
	private static MyUiBinder uiBinder = GWT.create(MyUiBinder.class);	

	public interface IAdminPanelWindowCallback {
		public void onLogoutButtonClicked();
		public void getGroups();
		public void getExperiments();
		public void getUsers();
		public void onSearchButtonClicked(Date fromDate, Date toDate, Group group, Experiment experiment);
	}
	
	private AdminPanelWindowHelper helper;
	
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
	
	// Panels
	@UiField VerticalPanel accessesSearchPanel;
	@UiField VerticalPanel usersUsersPanel;
	
	// Users panel related
	@UiField FlexTable usersListTable;
	private Cell selectedUserCell = null;
	private User selectedUser = null;
	private ArrayList<User> usersList;
	@UiField TextBox userDetailLogin;
	@UiField TextBox userDetailFullName;
	@UiField TextBox userDetailEmail;
	@UiField ListBox userDetailRolesList;
	
	// Menu items
	@UiField MenuItem accessesSearchMenuItem;
	@UiField MenuItem usersUsersMenuItem;
	
	private Label startedHeader;
	private Label timeHeader;
	private Label usernameHeader;
	private Label fullnameHeader;
	private Label experimentHeader;
	
	// Callbacks
	private final IAdminPanelWindowCallback callback;
	
	// DTOs
	private final User user;
	private ArrayList<Group> groupsList;
	private ArrayList<Experiment> experiments;
	private ArrayList<ExperimentUse> experimentUses;

	public AdminPanelWindow(IConfigurationManager configurationManager, User user, IAdminPanelWindowCallback callback) {
	    super(configurationManager);
	    
	    this.user = user;
	    this.callback = callback;

	    this.helper = new AdminPanelWindowHelper(); 
	    this.loadWidgets();
	}
	
	public void init() {
		this.callback.getExperiments();
		this.callback.getGroups();
	}
	
	private void loadWidgets() {
		AdminPanelWindow.uiBinder.createAndBindUi(this);
		
		// Show only one panel
		this.usersUsersPanel.setVisible(false);
		this.accessesSearchPanel.setVisible(true);
		
		this.registerMenuCallbacks();
		this.setupUsersPanel(); // TODO: Do this on-demand only.

		this.userLabel.setText(WlUtil.escapeNotQuote(this.user.getFullName()));
		
		this.fromDateBox.setFormat(new DefaultFormat(DateTimeFormat.getMediumDateFormat()));
		this.toDateBox.setFormat(new DefaultFormat(DateTimeFormat.getMediumDateFormat()));
		
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
	
	private void fillRolesList() {
		this.userDetailRolesList.addItem("student");
		this.userDetailRolesList.addItem("professor");
		this.userDetailRolesList.addItem("administrator");
	}

	private void setupUsersPanel() {
		
		final CellFormatter cellFormatter = AdminPanelWindow.this.usersListTable.getCellFormatter();
		
		// Column headers.
		this.usersListTable.setText(0, 0, "Login");
		this.usersListTable.setText(0, 1, "Full name");
		this.usersListTable.setCellSpacing(20);
		cellFormatter.setStylePrimaryName(0, 0, "web-admin-table-cell-header");
		cellFormatter.setStylePrimaryName(0, 1, "web-admin-table-cell-header");

		// Fill roles list
		fillRolesList();
		
		this.usersListTable.addClickHandler(new ClickHandler() {

			@Override
			public void onClick(ClickEvent event) {
				final FlexTable table = AdminPanelWindow.this.usersListTable;
				Cell cell = AdminPanelWindow.this.usersListTable.getCellForEvent(event);
				
				if(cell == null) // What was clicked isn't a cell.
					return;
				
				final int row = cell.getRowIndex();
				final CellFormatter cellFormatter = AdminPanelWindow.this.usersListTable.getCellFormatter();
				
				if(row == 0) // The header may not be selected.
					return;
				
				// Store the selected cell.
				AdminPanelWindow.this.selectedUserCell = cell;
				
				// Retrieve the user the selected cell corresponds to.
				if( AdminPanelWindow.this.usersList != null && AdminPanelWindow.this.usersList.size() > (row - 1) ) {
					final User user = AdminPanelWindow.this.usersList.get(row - 1);
					AdminPanelWindow.this.updateSelectedUser(user);
				} else {
					AdminPanelWindow.this.updateSelectedUser(null);
				}
				
				// Mark the cell as selected. (Eventually to be handled by some third party library).
				// Update every cell's style.
				for(int i = 1; i < table.getRowCount(); i++) {
					if( i == row) {
						cellFormatter.setStylePrimaryName(i, 0, "web-admin-table-cell-selected");
						cellFormatter.setStylePrimaryName(i, 1, "web-admin-table-cell-selected");	
					} else {
						cellFormatter.setStylePrimaryName(i, 0, "web-admin-table-cell-not-selected");
						cellFormatter.setStylePrimaryName(i, 1, "web-admin-table-cell-not-selected");
					}
				}
			}
			
		}
		);
		
	}

	/**
	 * Stores the specified user as the currently selected one and updates
	 * the selected user details panel. 
	 * @param user Selected user. May be null.
	 */
	private void updateSelectedUser(User user) {
		
		this.selectedUser = user;
		
		if(user == null) {
			this.userDetailLogin.setText("");
			this.userDetailFullName.setText("");
			this.userDetailEmail.setText("");
			this.userDetailRolesList.setSelectedIndex(0);
		} else {
			this.userDetailLogin.setText(user.getLogin());
			this.userDetailFullName.setText(user.getFullName());
			this.userDetailEmail.setText(user.getEmail());
			
			final String role = user.getRole().getName();
			if(role.equals("student"))
				this.userDetailRolesList.setSelectedIndex(0);
			else if(role.equals("professor"))
				this.userDetailRolesList.setSelectedIndex(1);
			else if(role.equals("administrator"))
				this.userDetailRolesList.setSelectedIndex(2);
			else {
				System.out.println("Unrecognized role: " + role);
			}
		}
	}

	private void registerMenuCallbacks() {
		
		this.accessesSearchMenuItem.setCommand(new Command() {
			@Override
			public void execute() {
				AdminPanelWindow.this.accessesSearchPanel.setVisible(true);
				AdminPanelWindow.this.usersUsersPanel.setVisible(false);
			}
		}
		);
		
		
		this.usersUsersMenuItem.setCommand(new Command() {
			@Override
			public void execute() {
				AdminPanelWindow.this.accessesSearchPanel.setVisible(false);
				AdminPanelWindow.this.usersUsersPanel.setVisible(true);
		    	AdminPanelWindow.this.callback.getUsers();
			}
		}
		);
		
	}

	public void fillExperimentsCombobox(ArrayList<Experiment> experiments) {
		this.experimentConditionListBox.addItem("(any)"); // #i18n
		this.experiments = experiments;
		for ( Experiment experiment: this.experiments ) {
			this.experimentConditionListBox.addItem(experiment.getUniqueName());
		}
	}
	
	public void fillGroupsCombobox(ArrayList<Group> groups) {
		this.groupConditionListBox.addItem("(any)"); // #i18n
		this.groupsList = this.helper.extractGroupsTreeToList(groups);
		for ( Group group: this.groupsList ) {
			this.groupConditionListBox.addItem(group.getFullName());
		}
	}

	public void fillExperimentUsesGrid(ArrayList<ExperimentUse> experimentUses) {
		this.experimentUses = experimentUses;

    	this.experimentUsesGrid.clear();
    	this.experimentUsesGrid.resize(this.experimentUses.size()+1, 5);
    	
    	this.experimentUsesGrid.setWidget(0, 0, this.startedHeader);
    	this.experimentUsesGrid.setWidget(0, 1, this.timeHeader);
    	this.experimentUsesGrid.setWidget(0, 2, this.usernameHeader);
    	this.experimentUsesGrid.setWidget(0, 3, this.fullnameHeader);
    	this.experimentUsesGrid.setWidget(0, 4, this.experimentHeader);

        for (int row = 0; row < this.experimentUses.size(); row++) {
        	ExperimentUse eu = this.experimentUses.get(row);
      		this.experimentUsesGrid.setWidget(row+1, 0, new Label(DateTimeFormat.getMediumDateTimeFormat().format(eu.getStartDate())));
    		this.experimentUsesGrid.setWidget(row+1, 1, new Label((eu.getEndDate().getTime()-eu.getStartDate().getTime())/1000 + ""));
    		if ( eu.getAgent() instanceof User ) {
        		this.experimentUsesGrid.setWidget(row+1, 2, new Label(((User)eu.getAgent()).getLogin()));
        		this.experimentUsesGrid.setWidget(row+1, 3, new Label(((User)eu.getAgent()).getFullName()));
    		} else if ( eu.getAgent() instanceof ExternalEntity ) {
        		this.experimentUsesGrid.setWidget(row+1, 2, new Label());
        		this.experimentUsesGrid.setWidget(row+1, 3, new Label(((ExternalEntity)eu.getAgent()).getName()));
    		}
    		this.experimentUsesGrid.setWidget(row+1, 4, new Label(eu.getExperiment().getUniqueName()));
        }

    	// Future functionality:
    	//this.downloadButton.setVisible(this.experimentUses.size() > 0);		
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
	
	
//	@UiHandler("usersMenuItem")
//	void onUsersMenuItemClicked(@SuppressWarnings("unused") ClickEvent ev) {
//		System.out.println("USERS MENU ITEM WAS CLICKED");
//	}

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
    		group = this.groupsList.get(groupIndex-1);
    	}

    	int experimentIndex = this.experimentConditionListBox.getSelectedIndex();
    	Experiment experiment;
    	if ( experimentIndex == 0 ) {
    		experiment = null;
    	} else {
    		experiment = this.experiments.get(experimentIndex-1);
    	}
    	
    	this.callback.onSearchButtonClicked(fromDate, toDate, group, experiment);
    }

    /**
     * Fills the user lists table with the specified list of users. Every user previously on the
     * table is removed. The headers of the table are not modified. It also stores the user list
     * for later use.
     * @param users List of the users to fill the table with.
     */
	public void fillUsersList(ArrayList<User> users) {
		
		// Store the user list to be able to access each user object easily later.
		this.usersList = users;
		
		// Remove old users before adding new ones.
		for(int i = 1; i < this.usersListTable.getRowCount(); i++) {
			this.usersListTable.removeRow(i);
		}
		
		// Add users to the list (being careful not to replace the table header).
		int insertrow = 1;
		for(User user : users) {
			this.usersListTable.setText(insertrow, 0, user.getLogin());
			this.usersListTable.setText(insertrow, 1, user.getFullName());
			insertrow++;
		}
	}
}
