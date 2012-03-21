/*
* Copyright (C) 2005 onwards University of Deusto
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
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.Image;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;

import es.deusto.weblab.client.configuration.IConfigurationManager;
import es.deusto.weblab.client.dto.users.User;
import es.deusto.weblab.client.lab.ui.themes.es.deusto.weblab.defaultweb.DefaultTheme;
import es.deusto.weblab.client.ui.widgets.WlUtil;

class LoggedPanel extends Composite {
	
    interface ILoggedPanelCallback {
    	public void onLogoutButtonClicked();
    }
    
	interface LoggedPanelUiBinder extends UiBinder<Widget, LoggedPanel> {
	}

	private static LoggedPanelUiBinder uiBinder = GWT.create(LoggedPanelUiBinder.class);
    
	// Widgets
    @UiField VerticalPanel contentPanel;  
    @UiField Label userLabel;
	@UiField Anchor logoutLink;
	@UiField Image logoImage;
	
	// DTOs
	private final User user;
    private final ILoggedPanelCallback callback;
	
    LoggedPanel(User user, ILoggedPanelCallback callback, IConfigurationManager configurationManager) {
		this.user = user;
		this.callback = callback;
	
	    final Widget wid = LoggedPanel.uiBinder.createAndBindUi(this);
	    this.initWidget(wid);
	    
	    this.logoImage.setUrl(GWT.getModuleBaseURL() + configurationManager.getProperty(DefaultTheme.Configuration.HOST_ENTITY_MOBILE_IMAGE, ""));
	    if(this.user != null)
	    	this.userLabel.setText(WlUtil.escapeNotQuote(this.user.getFullName()));
	    else
	    	this.userLabel.setText("");
	}

	@UiHandler("logoutLink")
	void onLogoutClicked(@SuppressWarnings("unused") ClickEvent ev) {
		this.callback.onLogoutButtonClicked();
	}
	
}
