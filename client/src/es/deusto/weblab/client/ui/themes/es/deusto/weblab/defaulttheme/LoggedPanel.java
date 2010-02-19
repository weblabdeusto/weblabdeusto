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
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.uibinder.client.UiTemplate;
import com.google.gwt.user.client.ui.Anchor;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.HasHorizontalAlignment;
import com.google.gwt.user.client.ui.HasVerticalAlignment;
import com.google.gwt.user.client.ui.Image;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.Widget;

import es.deusto.weblab.client.configuration.IConfigurationManager;
import es.deusto.weblab.client.dto.users.User;
import es.deusto.weblab.client.ui.themes.es.deusto.weblab.defaulttheme.LoginWindow.MyUiBinder;
import es.deusto.weblab.client.ui.themes.es.deusto.weblab.defaulttheme.i18n.IWebLabDeustoThemeMessages;
import es.deusto.weblab.client.ui.widgets.WlHorizontalPanel;
import es.deusto.weblab.client.ui.widgets.WlUtil;
import es.deusto.weblab.client.ui.widgets.WlVerticalPanel;



/**
 *  Logged-in panel that is included in some windows.
 */
public class LoggedPanel extends Composite {
	
	
	/******************
	 * UIBINDER RELATED
	 ******************/
	
	interface LoggedPanelUiBinder extends UiBinder<Widget, LoggedPanel> {
	}

	private static LoggedPanelUiBinder uiBinder = GWT.create(LoggedPanelUiBinder.class);

	
    protected interface ILoggedPanelCallback {
    	public void onLogoutButtonClicked();
    }
    	
    protected ILoggedPanelCallback callback;
    
    // i18n
    private IWebLabDeustoThemeMessages i18nMessages = (IWebLabDeustoThemeMessages)
    	GWT.create(IWebLabDeustoThemeMessages.class);
    	
	// Widgets
    @UiField WlHorizontalPanel headerPanel;
    @UiField WlVerticalPanel contentPanel;  
    @UiField Image logo;
    @UiField Label userLabel;
    @UiField Label separatorLabel;
	@UiField Anchor logoutLink;
	
	// DTOs
	protected User user;

	
	LoggedPanel(User user, ILoggedPanelCallback callback){
	    	this.user = user;
	    	this.callback = callback;
	    	loadWidgets();
	}
	
	/**
	 * Function to be called after the widgets have been placed, to do those things
	 * that are not done from UiBinder.
	 */
	void setupWidgets() {
		logo.setUrl(GWT.getModuleBaseURL() + "img/logo-header.png");
		userLabel.setText(WlUtil.escapeNotQuote(this.user.getFullName()));
		logoutLink.setText(this.i18nMessages.logOut());
		
		this.headerPanel.setCellHorizontalAlignment(logo, HasHorizontalAlignment.ALIGN_LEFT);
		this.headerPanel.setCellHorizontalAlignment(userLabel, HasHorizontalAlignment.ALIGN_RIGHT);		
		this.headerPanel.setCellHorizontalAlignment(separatorLabel, HasHorizontalAlignment.ALIGN_CENTER);
		this.headerPanel.setCellHorizontalAlignment(logoutLink, HasHorizontalAlignment.ALIGN_LEFT);
		this.headerPanel.setCellWidth(separatorLabel, "20px");
	}
	
	/**
	 * Binded automatically by UiBinder. Will be called whenever the logout
	 * button is pressed. May also be called manually passing a null event.
	 * @param ev ClickEvent. May be null. 
	 */
	@UiHandler("logoutLink")
	void onLogoutClicked(ClickEvent ev) {
		System.out.println("Logout button clicked.");
		LoggedPanel.this.callback.onLogoutButtonClicked();
	}

	public void loadWidgets() {
	    final Widget wid = uiBinder.createAndBindUi(this);
	    this.initWidget(wid);
	    setupWidgets();
	}
}