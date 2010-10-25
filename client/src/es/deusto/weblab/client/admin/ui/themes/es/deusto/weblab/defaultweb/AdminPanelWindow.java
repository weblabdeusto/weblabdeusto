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
 * Author: Jaime Irurzun <jaime.irurzun@gmail.com>
 *         Luis Rodriguez <luis.rodriguez@opendeusto.es>
 *
 */

package es.deusto.weblab.client.admin.ui.themes.es.deusto.weblab.defaultweb;

import java.util.Date;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.ui.Anchor;
import com.google.gwt.user.client.ui.HasHorizontalAlignment;
import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;
import com.smartgwt.client.data.Criteria;
import com.smartgwt.client.data.Record;
import com.smartgwt.client.types.Alignment;
import com.smartgwt.client.types.DateDisplayFormat;
import com.smartgwt.client.types.DragDataAction;
import com.smartgwt.client.types.OperatorId;
import com.smartgwt.client.types.Side;
import com.smartgwt.client.types.VerticalAlignment;
import com.smartgwt.client.widgets.Button;
import com.smartgwt.client.widgets.Img;
import com.smartgwt.client.widgets.TransferImgButton;
import com.smartgwt.client.widgets.form.DynamicForm;
import com.smartgwt.client.widgets.form.FormItemValueFormatter;
import com.smartgwt.client.widgets.form.events.ItemChangedEvent;
import com.smartgwt.client.widgets.form.events.ItemChangedHandler;
import com.smartgwt.client.widgets.form.fields.ButtonItem;
import com.smartgwt.client.widgets.form.fields.DateTimeItem;
import com.smartgwt.client.widgets.form.fields.FormItem;
import com.smartgwt.client.widgets.form.fields.IPickTreeItem;
import com.smartgwt.client.widgets.form.fields.SelectItem;
import com.smartgwt.client.widgets.form.fields.TextItem;
import com.smartgwt.client.widgets.form.fields.events.ChangeEvent;
import com.smartgwt.client.widgets.form.fields.events.ChangeHandler;
import com.smartgwt.client.widgets.form.fields.events.ClickHandler;
import com.smartgwt.client.widgets.form.validator.MatchesFieldValidator;
import com.smartgwt.client.widgets.form.validator.RegExpValidator;
import com.smartgwt.client.widgets.grid.CellFormatter;
import com.smartgwt.client.widgets.grid.ListGrid;
import com.smartgwt.client.widgets.grid.ListGridField;
import com.smartgwt.client.widgets.grid.ListGridRecord;
import com.smartgwt.client.widgets.grid.SummaryFunction;
import com.smartgwt.client.widgets.grid.events.RecordClickEvent;
import com.smartgwt.client.widgets.grid.events.RecordClickHandler;
import com.smartgwt.client.widgets.layout.HLayout;
import com.smartgwt.client.widgets.layout.VLayout;
import com.smartgwt.client.widgets.tab.Tab;
import com.smartgwt.client.widgets.tab.TabSet;
import com.smartgwt.client.widgets.tree.TreeGrid;

import es.deusto.weblab.client.admin.comm.datasources.AuthsDataSource;
import es.deusto.weblab.client.admin.comm.datasources.ExperimentUsesDataSource;
import es.deusto.weblab.client.admin.comm.datasources.ExperimentsDataSource;
import es.deusto.weblab.client.admin.comm.datasources.GroupsDataSource;
import es.deusto.weblab.client.admin.comm.datasources.RolesDataSource;
import es.deusto.weblab.client.admin.comm.datasources.UsersDataSource;
import es.deusto.weblab.client.admin.comm.datasources.WebLabRestDataSource;
import es.deusto.weblab.client.admin.dto.ExperimentRecord;
import es.deusto.weblab.client.admin.dto.ExperimentUseRecord;
import es.deusto.weblab.client.configuration.IConfigurationManager;
import es.deusto.weblab.client.dto.SessionID;
import es.deusto.weblab.client.dto.users.User;
import es.deusto.weblab.client.ui.widgets.WlUtil;
import es.deusto.weblab.client.ui.widgets.WlWaitingLabel;

public class AdminPanelWindow extends BaseWindow {

	interface MyUiBinder extends UiBinder<Widget, AdminPanelWindow> {
	}
	private static MyUiBinder uiBinder = GWT.create(MyUiBinder.class);

	public interface IAdminPanelWindowCallback {
		public void onLogoutButtonClicked();
	}
	
	
	private static boolean DEVELOPMENT = false;
	
	// DataSources
	private WebLabRestDataSource experimentUsesDS;
	private WebLabRestDataSource experimentsDS;
	private WebLabRestDataSource groupsDS;
	private WebLabRestDataSource rolesDS;
	private WebLabRestDataSource usersDS;
	private WebLabRestDataSource authsDS;

	// Widgets
	@UiField VerticalPanel containerPanel;
	@UiField HorizontalPanel headerProfilePanel;
	@UiField Label userLabel;
	@UiField Anchor logoutLink;
	@UiField WlWaitingLabel waitingLabel;
	@UiField Label generalErrorLabel;
	@UiField VLayout smartGWTLayout;
	private TabSet tabSet;
	private Tab accessesTab;
	@SuppressWarnings("unused")
	private Tab usersTab;
	private VLayout accessesLayout;
	private DynamicForm accessesExperimentUsesFilterForm;
	private ListGrid accessesExperimentUsesGrid;
	private VLayout usersLayout;
	private VLayout usersUsersLayout;
	private ListGrid usersUsersGrid;
	private VLayout usersRolesLayout;
	private ListGrid usersRolesGrid;

	// Callbacks
	private final IAdminPanelWindowCallback callback;

	// DTOs
	private final User user;
	private TabSet usersTabSet;
	private Tab usersUsersTab;
	private Tab usersRolesTab;

	public AdminPanelWindow(IConfigurationManager configurationManager, User user, SessionID sessionId, IAdminPanelWindowCallback callback) {
		super(configurationManager);

		this.user = user;
		this.callback = callback;

		// Create the data sources that the panel will use

		this.experimentUsesDS = new ExperimentUsesDataSource(sessionId);
		this.experimentUsesDS.initialize();

		this.groupsDS = new GroupsDataSource(sessionId);
		this.groupsDS.initialize();

		this.experimentsDS = new ExperimentsDataSource(sessionId);
		this.experimentsDS.initialize();

		this.rolesDS = new RolesDataSource(sessionId);
		this.rolesDS.initialize();

		this.usersDS = new UsersDataSource(sessionId);
		this.usersDS.initialize();
		
		this.authsDS = new AuthsDataSource(sessionId);
		this.authsDS.initialize();

		this.loadWidgets();
	}

	public void init() {
	}

	private void loadWidgets() {
		AdminPanelWindow.uiBinder.createAndBindUi(this);
		
		for ( int i = 0; i < this.headerProfilePanel.getWidgetCount(); ++i) {
			this.headerProfilePanel.setCellHorizontalAlignment(this.headerProfilePanel.getWidget(i), HasHorizontalAlignment.ALIGN_RIGHT);	
		}
		this.headerProfilePanel.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_RIGHT);
		this.userLabel.setText(WlUtil.escapeNotQuote(this.user.getFullName()));
				
		this.tabSet = new TabSet();
		this.tabSet.setTabBarPosition(Side.TOP);
		this.tabSet.setTabBarAlign(Side.LEFT);
		this.tabSet.setWidth(1024);
		this.tabSet.setHeight(600);
		this.tabSet.setPadding(40);
		
		this.accessesTab = new Tab("Accesses");				
		this.accessesLayout = new VLayout();
		this.accessesLayout.setWidth100();
		this.accessesLayout.setHeight100();		
		this.accessesLayout.setPadding(10);
		this.accessesLayout.setMembersMargin(15);		
		this.accessesTab.setPane(this.accessesLayout);
		this.tabSet.addTab(this.accessesTab);
		this.buildAccessesLayout();
		
		
		if(DEVELOPMENT)
		{
			/* Under development: uncommented to hide it in the production version */
			this.usersTab = new Tab("Users");				
			this.usersLayout = new VLayout();
			this.usersLayout.setWidth100();
			this.usersLayout.setHeight100();		
			this.usersLayout.setPadding(10);
			this.usersLayout.setMembersMargin(15);		
			this.usersTab.setPane(this.usersLayout);
			this.tabSet.addTab(this.usersTab);
			this.buildUsersLayout();
		}
		
		this.smartGWTLayout.addMember(this.tabSet);	
	}
	
	private void buildAccessesLayout() {

		/*
		 * Filter form
		 */

		this.accessesExperimentUsesFilterForm = new DynamicForm();
		this.accessesExperimentUsesFilterForm.setIsGroup(true);
		this.accessesExperimentUsesFilterForm.setGroupTitle("Filter"); // i18n
		this.accessesExperimentUsesFilterForm.setNumCols(14);
		this.accessesExperimentUsesFilterForm.setDataSource(this.experimentsDS);
		this.accessesExperimentUsesFilterForm.setAutoFocus(false);
		this.accessesExperimentUsesFilterForm.setPadding(15);
		this.accessesExperimentUsesFilterForm.setWidth(950);

		final DateTimeItem startDateItem = new DateTimeItem(ExperimentUseRecord.START_DATE, "From");
		startDateItem.setCriteriaField(ExperimentUseRecord.START_DATE);
		startDateItem.setOperator(OperatorId.GREATER_OR_EQUAL);
		startDateItem.setRequired(false);
		startDateItem.setDisplayFormat(DateDisplayFormat.TOEUROPEANSHORTDATE);

		final DateTimeItem endDateItem = new DateTimeItem(ExperimentUseRecord.END_DATE, "To");
		endDateItem.setCriteriaField(ExperimentUseRecord.START_DATE);
		endDateItem.setOperator(OperatorId.LESS_OR_EQUAL);
		endDateItem.setRequired(false);
		endDateItem.setDisplayFormat(DateDisplayFormat.TOEUROPEANSHORTDATE);
		endDateItem.addChangeHandler(new ChangeHandler() {
			@Override
			public void onChange(ChangeEvent event) {
				final Date date = (Date) event.getValue();
				if (date != null) {
					final long base = date.getTime();
					event.getItem().setValue(new Date(base + 86399000)); // 86399000 == 23*60*60*1000 + 59*60*1000 + 59*1000;
				}
			}
		});

		final IPickTreeItem groupItem = new IPickTreeItem(ExperimentUseRecord.GROUP_ID, "Group"); // i18n
		groupItem.setOperator(OperatorId.EQUALS);
		groupItem.setDataSource(this.groupsDS);
		groupItem.setOptionDataSource(this.groupsDS);
		groupItem.setCanSelectParentItems(true);
		groupItem.setRequired(false);
		groupItem.setWidth(140);

		final SelectItem experimentItem = new SelectItem(ExperimentUseRecord.EXPERIMENT_ID, "Experiment");
		experimentItem.setOperator(OperatorId.EQUALS);
		experimentItem.setWidth(240);
		experimentItem.setPickListWidth(240);
		experimentItem.setPickListFields(new ListGridField(ExperimentRecord.NAME, "Experiment"),
										 new ListGridField(ExperimentRecord.CATEGORY, "Category"));
		experimentItem.setDisplayField(ExperimentRecord.NAME);
		experimentItem.setValueFormatter(new FormItemValueFormatter() {
	
			@Override
			public String formatValue(Object value, Record record, DynamicForm form, FormItem item) {
				ListGridRecord r = item.getSelectedRecord();
				if ( r != null ) {
					String name = r.getAttributeAsString("name");
					if ( name != null )
						return name + "@" + r.getAttributeAsString("category");
				}
				return " ";
			}
		});
		experimentItem.setAllowEmptyValue(true);
		experimentItem.setOptionDataSource(this.experimentsDS);
		experimentItem.setValueField(ExperimentRecord.ID);

		this.accessesExperimentUsesFilterForm.setFields(startDateItem, endDateItem, groupItem, experimentItem);

		this.accessesExperimentUsesFilterForm.addItemChangedHandler(new ItemChangedHandler() {
					@Override
					public void onItemChanged(ItemChangedEvent event) {
						// Use to temporally force SmartGWT to make requests to the server for every fetch:
						AdminPanelWindow.this.accessesExperimentUsesGrid.invalidateCache();
						AdminPanelWindow.this.accessesExperimentUsesGrid.fetchData(AdminPanelWindow.this.accessesExperimentUsesFilterForm.getValuesAsCriteria());
					}
				});
		this.accessesLayout.addMember(this.accessesExperimentUsesFilterForm);

		/*
		 * Clear button
		 */

		final com.smartgwt.client.widgets.Button clearButton = new com.smartgwt.client.widgets.Button("Clear Filter"); // i18n
		clearButton.addClickHandler(new com.smartgwt.client.widgets.events.ClickHandler() {
					@Override
					public void onClick(com.smartgwt.client.widgets.events.ClickEvent event) {
						AdminPanelWindow.this.accessesExperimentUsesFilterForm.clearValues();
						AdminPanelWindow.this.accessesExperimentUsesGrid.filterData();
					}
				});
		this.accessesLayout.addMember(clearButton);

		/*
		 * ListGrid
		 */

		final ListGridField idField = new ListGridField(ExperimentUseRecord.ID, "#");
		idField.setSummaryFunction(new SummaryFunction() {
			@Override
			public Object getSummaryValue(Record[] records, ListGridField field) {
				return records.length + " matched uses";
			}
		});
		idField.setShowGridSummary(true);

		final ListGridField dateField = new ListGridField(ExperimentUseRecord.START_DATE, "Date");

		final ListGridField timeField = new ListGridField(ExperimentUseRecord.TIME, "Time");
		timeField.setCellFormatter(new CellFormatter() {
			@SuppressWarnings("deprecation")
			@Override
			public String format(Object value, ListGridRecord record, int row, int column) {
				Date startDate = record.getAttributeAsDate(ExperimentUseRecord.START_DATE);
				return "" + startDate.getHours() + ":" + startDate.getMinutes();
			}
		});

		final ListGridField agentLoginField = new ListGridField(ExperimentUseRecord.AGENT_LOGIN, "User Login"); // i18n
		final ListGridField agentFullNameField = new ListGridField(ExperimentUseRecord.AGENT_NAME, "User Name"); // i18n
		final ListGridField experimentNameField = new ListGridField(ExperimentUseRecord.EXPERIMENT_NAME, "Experiment Name"); // i18n
		final ListGridField experimentCategoryField = new ListGridField(ExperimentUseRecord.EXPERIMENT_CATEGORY, "Experiment Category"); // i18n

		final ListGridField durationField = new ListGridField(ExperimentUseRecord.DURATION, "Duration"); // i18n
		durationField.setCellFormatter(new CellFormatter() {
			@Override
			public String format(Object value, ListGridRecord record, int row, int column) {
				Date startDate = record.getAttributeAsDate(ExperimentUseRecord.START_DATE);
				Date endDate = record.getAttributeAsDate(ExperimentUseRecord.END_DATE);
				return "" + (endDate.getTime() - startDate.getTime()) / 1000 + " sec."; // i18n
			}
		});
		
		this.accessesExperimentUsesGrid = new ListGrid();
		this.accessesExperimentUsesGrid.setWidth(950);
		this.accessesExperimentUsesGrid.setHeight(400);
		this.accessesExperimentUsesGrid.setShowGridSummary(true);
		this.accessesExperimentUsesGrid.setDataSource(this.experimentUsesDS);
		this.accessesExperimentUsesGrid.setDataPageSize(50);
		this.accessesExperimentUsesGrid.setAutoFetchData(true);
		this.accessesExperimentUsesGrid.setFields(idField, dateField, timeField, agentLoginField, agentFullNameField, experimentNameField, experimentCategoryField, durationField);
		this.accessesExperimentUsesGrid.setSortField(1);
		this.accessesLayout.addMember(this.accessesExperimentUsesGrid);		
	}
	
	@SuppressWarnings("unused")
	private void buildUsersLayout() {			
		
		this.usersTabSet = new TabSet();
		this.usersTabSet.setTabBarPosition(Side.TOP);
		this.usersTabSet.setTabBarAlign(Side.RIGHT);
		this.usersTabSet.setWidth100();
		this.usersTabSet.setHeight100();
		this.usersTabSet.setPadding(40);
		this.usersLayout.addMember(this.usersTabSet);
		
		this.usersUsersTab = new Tab("Users");				
		this.usersUsersLayout = new VLayout();
		this.usersUsersLayout.setWidth100();
		this.usersUsersLayout.setHeight100();		
		this.usersUsersLayout.setPadding(10);
		this.usersUsersLayout.setMembersMargin(15);		
		this.usersUsersTab.setPane(this.usersUsersLayout);
		this.usersTabSet.addTab(this.usersUsersTab);
		this.buildUsersUsersPanel();
		
		this.usersRolesTab = new Tab("Roles");				
		this.usersRolesLayout = new VLayout();
		this.usersRolesLayout.setWidth100();
		this.usersRolesLayout.setHeight100();		
		this.usersRolesLayout.setPadding(10);
		this.usersRolesLayout.setMembersMargin(15);		
		this.usersRolesTab.setPane(this.usersRolesLayout);
		this.usersTabSet.addTab(this.usersRolesTab);
		this.buildUsersRolesPanel();		
	}

	/**
	 * Builds the Users/Users panel.
	 */
	private void buildUsersUsersPanel() {
		
		// *********
		// Create and link the layouts that we will use to arrange the many controls
		// *********
		
		// Create horizontal panel to hold the user grid and the tab set
		final HLayout mainLayout = new HLayout();
		mainLayout.setMembersMargin(20);
		
		// Create a vertical layout for the users grid and the add/remove buttons.
		final VLayout gridAndButtonsVLayout = new VLayout();
		
		// Create a vertical layout for the tabset and the save changes button.
        final VLayout tabsetAndButtonsVLayout = new VLayout();
		
        // Link them
		this.usersUsersLayout.addMember(mainLayout);        
        mainLayout.addMember(gridAndButtonsVLayout);
        mainLayout.addMember(tabsetAndButtonsVLayout);
		
        
        
        // *********
        // Create users grid part, which is made of a grid to display and select the users 
        // and a dynamic form with add and remove buttons.
        // *********
		
		// Create users grid fields
		final ListGridField loginField = new ListGridField("login", "Login");
		final ListGridField fullNameField = new ListGridField("full_name", "Full Name");
				
		// Create users list grid, and add the fields to it.
		this.usersUsersGrid = new ListGrid();
		this.usersUsersGrid.setWidth(300);
		this.usersUsersGrid.setHeight(400);
		this.usersUsersGrid.setAutoFetchData(true);
		this.usersUsersGrid.setDataSource(this.usersDS);
		this.usersUsersGrid.setDataPageSize(50);
		this.usersUsersGrid.setFields(loginField, fullNameField);
		this.usersUsersGrid.setSortField(1);
		
		
		// Create forms for the add and for the remove buttons.
		// Note: I'd normally place both buttons on a single form. However,
		// I have not been able to get it to work properly, as the buttons
		// overlap each other. 
		final DynamicForm addForm = new DynamicForm();
		final ButtonItem addIt = new ButtonItem("add", "Add");
		addIt.setWidth(70);
		addForm.setFields(addIt);
		addForm.setWidth(80);
		
		final DynamicForm remForm = new DynamicForm();
		remForm.setAlign(Alignment.RIGHT);
		final ButtonItem remIt = new ButtonItem("remove", "Remove");
		remIt.setWidth(70);
		remForm.setFields(remIt);
		remForm.setWidth(80);
		
		final HLayout addRemoveLayout = new HLayout();
		addRemoveLayout.addMember(addForm);
		addRemoveLayout.addMember(remForm);
		addRemoveLayout.setWidth(170);
		addRemoveLayout.setAlign(Alignment.RIGHT);
		addRemoveLayout.setLayoutMargin(10);
		
		// Link everything
		gridAndButtonsVLayout.addMember(this.usersUsersGrid);
		gridAndButtonsVLayout.addMember(addRemoveLayout);

		
		
        // *********
        // Create the tabset part, which is made of a tabset with several
		// different user-related tabs, and a "save changes" button.
        // *********
		
		//
		// Create the tabset (along with its tabs), and link it to the
		// layout. The actual controls within each tab will be created
		// later.
		//
		
		// Create the tabset itself
		final TabSet tabSet = new TabSet();
        tabSet.setTabBarPosition(Side.TOP);  
        tabSet.setWidth(500);  
        tabSet.setHeight(400);  
        
        // Create each tab
        final Tab profileTab = new Tab("Profile", "pieces/16/pawn_blue.png");  
        final Tab groupsTab = new Tab("Groups", "pieces/16/pawn_green.png");  
        final Tab permissionsTab = new Tab("Permissions", "...");
        final Tab authTab = new Tab("Authentication", "...");
        

        // Add every tab to the tabset
        tabSet.addTab(profileTab);  
        tabSet.addTab(groupsTab);  
        tabSet.addTab(permissionsTab);
        tabSet.addTab(authTab);
        
        // Link it
        tabsetAndButtonsVLayout.addMember(tabSet);
        
        
        
        // 
        // Create the Save Changes form and link it to the layout.
        //
        final HLayout saveChangesLayout = new HLayout();
        saveChangesLayout.setLayoutMargin(10);
        saveChangesLayout.setLayoutAlign(Alignment.RIGHT);
        final DynamicForm saveChangesForm = new DynamicForm();
        saveChangesForm.setLayoutAlign(Alignment.RIGHT);
        saveChangesForm.setNumCols(1);
        final ButtonItem saveChangesIt = new ButtonItem("saveChanges", "Save Changes");
        saveChangesIt.setAlign(Alignment.RIGHT);
        saveChangesIt.setAutoFit(false);
        
        // If we don't set the value for the width, for some reason the button
        // appers in half, displaced to the left.
        saveChangesIt.setWidth(100);
        
        saveChangesForm.setFields(saveChangesIt);
        
        saveChangesLayout.addMember(saveChangesForm);
        tabsetAndButtonsVLayout.addMember(saveChangesLayout);
        
        
        //
        // Create the Profile tab
        //
        
        // Create the form that this tab is made of
        // We will manually create some of its items, but we will
        // rely on the default items for other datasource elements
        final DynamicForm profileForm = new DynamicForm();
        profileForm.setWidth("100%");
        //profileForm.setBorder("2px solid gold");
        
        // We use quite a few layouts, because otherwise the avatar
        // weirdly overlaps the dynamic form.
        final HLayout profileTabHLayout = new HLayout();
        profileTabHLayout.setPadding(20);
        //profileTabHLayout.setBorder("2px solid silver");
        final HLayout profileAvatarHLayout = new HLayout();
        final HLayout profileFormHLayout = new HLayout();
        
        profileForm.setUseAllDataSourceFields(false);
        
        // Seems to be ignored, done on a per-item basis either way.
        // profileForm.setValidateOnExit(true);
        
        final TextItem loginIt = new TextItem("login", "Username");
        loginIt.setRequired(true);
        loginIt.setValidateOnExit(true);
        final TextItem fullNameIt = new TextItem("full_name", "Name");
        fullNameIt.setRequired(true);
        fullNameIt.setValidateOnExit(true);
        final TextItem emailIt = new TextItem("email", "Email");
        emailIt.setRequired(true);
        emailIt.setValidateOnExit(true);
        final TextItem passwordIt = new TextItem("password", "New password");
        final TextItem passwordRepIt = new TextItem("password_rep", "Password again");
        passwordRepIt.setValidateOnExit(true);
        
        // Create a validator to make sure that both passwords match and complain otherwise.
        final MatchesFieldValidator pwdMatchesValidator = new MatchesFieldValidator();  
        pwdMatchesValidator.setOtherField("password");  
        pwdMatchesValidator.setErrorMessage("Passwords do not match");          
        passwordRepIt.setValidators(pwdMatchesValidator);  
        
        final RegExpValidator emailValidator = new RegExpValidator("\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,4}\\b");
        emailIt.setValidators(emailValidator);
        
        // TODO: Try to set up users to receive a role id rather than a role string.
        final SelectItem roleIt = new SelectItem("role", "Role");
        roleIt.setRequired(true);
        roleIt.setOptionDataSource(this.rolesDS);
        roleIt.setValidateOnExit(true);
        
        profileForm.setFields(loginIt, fullNameIt, emailIt, passwordIt, passwordRepIt, roleIt);
        
        // The form uses the Users data source.
        // However, it is linked to the users grid, which uses the same
        // data source, and whose selected User is the one this form
        // really displays. Hence, we do not call fetchData (at a later point,
        // we use editRecord instead).
        profileForm.setDataSource(this.usersDS);
        
             
        // Create the image for the avatar
        final Img avatarImg = new Img("", 100, 100);
        avatarImg.setBackgroundColor("#F5F5F5");
        avatarImg.setBorder("2px solid black");
        
        // Link layouts and tab
        profileAvatarHLayout.addMember(avatarImg);
        profileAvatarHLayout.setSize("65%", "100%");
        profileFormHLayout.addMember(profileForm);
        profileFormHLayout.setSize("100%", "100%");
        profileTabHLayout.addMember(profileFormHLayout);
        profileTabHLayout.addMember(profileAvatarHLayout);
        //profileAvatarHLayout.setBorder("2px solid blue");
        //profileFormHLayout.setBorder("2px solid green");
        profileTab.setPane(profileTabHLayout);
        
        
        //
        // Create the Groups tab
        //
        final TreeGrid groupsTree = new TreeGrid();
        groupsTree.setDataSource(this.groupsDS);
        final VLayout groupsLayout = new VLayout();
        groupsLayout.addMember(groupsTree);
        groupsTab.setPane(groupsLayout);
        
        
        // 
        // Create the Permissions tab
        //
        final HLayout permissionsLayout = new HLayout();
        final VLayout permissionsListAndButtonsLayout = new VLayout();
        final VLayout permissionDetailsLayout = new VLayout();
        final VLayout permissionsListLayout = new VLayout();
        final HLayout permissionsAddRemoveLayout = new HLayout();
        final HLayout permissionAddButtonLayout = new HLayout();
        final HLayout permissionRemoveButtonLayout = new HLayout();
        
        final ListGrid permissionsListGrid = new ListGrid();
        final Button permissionAddButton = new Button("Add");
        final Button permissionRemoveButton = new Button("Remove");
        
        final DynamicForm permissionForm = new DynamicForm();
        final TextItem permIdIt = new TextItem("permIdIt");
        permissionForm.setFields(permIdIt);
        
        permissionsAddRemoveLayout.setLayoutMargin(10);
        //permissionsAddRemoveLayout.setBorder("2px solid navy");
        permissionAddButton.setSize("65", "20");
        permissionRemoveButton.setSize("65", "20");
        permissionsAddRemoveLayout.setSize("100%", "10%");
        permissionAddButtonLayout.setSize("40%", "100%");
        //permissionAddButtonLayout.setBorder("1px solid gold");
        //permissionRemoveButtonLayout.setBorder("1px solid silver");
        
        permissionDetailsLayout.setGroupTitle("Permission");
        permissionDetailsLayout.setIsGroup(true);
        
        permissionDetailsLayout.setSize("90%", "100%");
        permissionsListAndButtonsLayout.setSize("90%", "100%");
        
        
        permissionsTab.setPane(permissionsLayout);
        	permissionsLayout.addMember(permissionsListAndButtonsLayout);
        		permissionsListAndButtonsLayout.addMember(permissionsListLayout);
        			permissionsListLayout.addMember(permissionsListGrid);
        		permissionsListAndButtonsLayout.addMember(permissionsAddRemoveLayout);
        			permissionsAddRemoveLayout.addMember(permissionAddButtonLayout);
        				permissionAddButtonLayout.addMember(permissionAddButton);
        			permissionsAddRemoveLayout.addMember(permissionRemoveButtonLayout);
        				permissionRemoveButtonLayout.addMember(permissionRemoveButton);
        permissionsLayout.addMember(permissionDetailsLayout);
        	permissionDetailsLayout.addMember(permissionForm);
        
        
        //
        // Create the Authentication tab
        //
        final HLayout authTabLayout = new HLayout();
        final VLayout allowedLayout = new VLayout();
        allowedLayout.setSize("47%", "100%");
        final VLayout notAllowedLayout = new VLayout();
        notAllowedLayout.setSize("47%", "100%");
        final VLayout authButtonsLayout = new VLayout();
        authButtonsLayout.setSize("5%", "100%");
        //authButtonsLayout.setBorder("2px solid black");
        final VLayout toLeftLayout = new VLayout();
        final VLayout toRightLayout = new VLayout();
        toRightLayout.setAlign(VerticalAlignment.BOTTOM);
        toRightLayout.setLayoutMargin(20);
        toLeftLayout.setLayoutMargin(20);
        
        final ListGridField allowedField = new ListGridField("name", "Allowed");
        final ListGrid allowedList = new ListGrid();
        allowedList.setCanDragRecordsOut(true);
        allowedList.setCanAcceptDroppedRecords(true);
        allowedList.setCanReorderFields(true);
        allowedList.setDragDataAction(DragDataAction.MOVE);
        allowedList.setTitle("Allowed");
        allowedList.setShowHeader(true);
        allowedList.setShowEmptyMessage(false);
        allowedList.setFields(allowedField);
        allowedList.setDataSource(this.authsDS);
        allowedList.fetchData();
        
        System.out.println(allowedList.getDataAsRecordList().getLength());
        
        final ListGridField notAllowedField = new ListGridField("name", "Not allowed");
        final ListGrid notAllowedList = new ListGrid();
        notAllowedList.setCanDragRecordsOut(true);
        notAllowedList.setCanAcceptDroppedRecords(true);
        notAllowedList.setCanReorderFields(true);
        notAllowedList.setDragDataAction(DragDataAction.MOVE);
        notAllowedList.setShowHeader(true);
        notAllowedList.setShowEmptyMessage(false);
        notAllowedList.setFields(notAllowedField);
        notAllowedList.setDataSource(this.authsDS);
        notAllowedList.fetchData();
        
        //final Button allowButton = new Button("->");
        final TransferImgButton allowButton = new TransferImgButton(TransferImgButton.RIGHT);
        allowButton.setSize("50", "20");
        allowButton.setValign(VerticalAlignment.BOTTOM);
        final TransferImgButton disallowButton = new TransferImgButton(TransferImgButton.LEFT);
        disallowButton.setSize("50", "20");
        toRightLayout.addMember(allowButton);
        toLeftLayout.addMember(disallowButton);
        authButtonsLayout.addMember(toRightLayout);
        authButtonsLayout.addMember(toLeftLayout);
        
        allowedLayout.addMember(allowedList);
        notAllowedLayout.addMember(notAllowedList);
        
        authTabLayout.addMember(allowedLayout);
        authTabLayout.addMember(authButtonsLayout);
        authTabLayout.addMember(notAllowedLayout);
        authTab.setPane(authTabLayout);
        
        
        //
        // Add callbacks
        // 
        
        // Switch the user we display whenever we select a different one on the users grid.
		this.usersUsersGrid.addRecordClickHandler(new RecordClickHandler() {
	        @Override
			public void onRecordClick(RecordClickEvent event) {
	        	
	        	// Modify the user displayed on Profile
	        	profileForm.clearErrors(true);
	        	profileForm.editRecord(event.getRecord());
	        	//saveButton.enable();
	        	
	        	// Modify the groups
	        	final Record userRec = AdminPanelWindow.this.usersUsersGrid.getSelectedRecord();
	        	if(userRec != null) {
		        	final String userId = userRec.getAttributeAsString("id");
		            final Criteria crit = new Criteria("user_id", userId);
		            groupsTree.filterData(crit);
	        	} 
	        	
	        	// Modify the avatar
	        	if(userRec != null) {
	        		String url = userRec.getAttributeAsString("avatar");
	        		avatarImg.setSrc(url);
	        		avatarImg.redraw();
	        	} else {
	        		avatarImg.setSrc("");
	        		avatarImg.redraw();
	        	}
	        }
		});
		
		// Handle User/Auths allowed and disallowed auths transfer
		allowButton.addClickHandler(new com.smartgwt.client.widgets.events.ClickHandler()
		{
			@Override
			public void onClick(
					com.smartgwt.client.widgets.events.ClickEvent event) {
				ListGridRecord record = allowedList.getSelectedRecord();
				System.out.println(record);
				System.out.println(record.getAttributeAsString("name"));
				allowedList.invalidateCache();
				allowedList.transferSelectedData(notAllowedList);
			}
		});
		
		disallowButton.addClickHandler(new com.smartgwt.client.widgets.events.ClickHandler()
		{
			@Override
			public void onClick(
					com.smartgwt.client.widgets.events.ClickEvent event) {
				notAllowedList.invalidateCache();
				notAllowedList.transferSelectedData(allowedList);
			}
		
		});
		
		
		
		// Handle new user addition
		addIt.addClickHandler(new ClickHandler() {
			@Override
			public void onClick(
					com.smartgwt.client.widgets.form.fields.events.ClickEvent event) {
				Record newRec = new Record();
				newRec.setAttribute("login", "Unnamed");
				AdminPanelWindow.this.usersUsersGrid.addData(newRec);
			}
		});

		// Handle selected user removal
		remIt.addClickHandler(new ClickHandler() {
			@Override
			public void onClick(
					com.smartgwt.client.widgets.form.fields.events.ClickEvent event) {
				AdminPanelWindow.this.usersUsersGrid.removeSelectedData();
			}
		});
		
		// Send an UPDATE query whenever we hit the Save Changes button.
        saveChangesIt.addClickHandler(new ClickHandler(){
			@Override
			public void onClick(
					com.smartgwt.client.widgets.form.fields.events.ClickEvent event) {
				
				// Validate the data before saving
				final boolean valid = profileForm.validate();
				if(valid)
					profileForm.saveData();
			}
			});
	}

	/**
	 * Builds the users/roles panel, creating and attaching the necessary
	 * SmartGWT controls to the UiBinder-defined panel.
	 */
	private void buildUsersRolesPanel() {

		// Create the fields for the left roles grid
		final ListGridField idField = new ListGridField("id", "#", 50);
		final ListGridField nameField = new ListGridField("name", "Name");

		// Create and attach the grid control itself, using the fields above
		this.usersRolesGrid = new ListGrid();
		this.usersRolesGrid.setWidth(300);
		this.usersRolesGrid.setHeight(400);
		this.usersRolesGrid.setAutoFetchData(true);
		this.usersRolesGrid.setDataSource(this.rolesDS);
		this.usersRolesGrid.setDataPageSize(50);
		this.usersRolesGrid.setFields(idField, nameField);
		this.usersRolesGrid.setSortField(1);

		this.usersRolesLayout.addMember(this.usersRolesGrid);
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
}
