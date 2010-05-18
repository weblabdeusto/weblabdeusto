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
import com.google.gwt.user.datepicker.client.DateBox.Format;

import es.deusto.weblab.client.configuration.IConfigurationManager;
import es.deusto.weblab.client.dto.users.User;
import es.deusto.weblab.client.ui.widgets.WlUtil;
import es.deusto.weblab.client.ui.widgets.WlWaitingLabel;

public class AdminPanelWindow extends BaseWindow {
	
	interface MyUiBinder extends UiBinder<Widget, AdminPanelWindow> {}
	private static MyUiBinder uiBinder = GWT.create(MyUiBinder.class);	

	public interface IAdminPanelWindowCallback {
		public void onLogoutButtonClicked();
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
	
	// Callbacks
	private final IAdminPanelWindowCallback callback;
	
	// DTOs
	private final User user;

	public AdminPanelWindow(IConfigurationManager configurationManager, User user, IAdminPanelWindowCallback callback) {
	    super(configurationManager);
	    
	    this.user = user;
	    this.callback = callback;
	    
	    this.loadWidgets();	    
	}	
	
	private void loadWidgets() {
		AdminPanelWindow.uiBinder.createAndBindUi(this);

		this.userLabel.setText(WlUtil.escapeNotQuote(this.user.getFullName()));
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
