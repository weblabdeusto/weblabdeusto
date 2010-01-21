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
import com.google.gwt.user.client.ui.Anchor;
import com.google.gwt.user.client.ui.HasHorizontalAlignment;
import com.google.gwt.user.client.ui.HasVerticalAlignment;
import com.google.gwt.user.client.ui.Image;
import com.google.gwt.user.client.ui.Label;

import es.deusto.weblab.client.configuration.IConfigurationManager;
import es.deusto.weblab.client.dto.users.User;
import es.deusto.weblab.client.ui.widgets.WlHorizontalPanel;
import es.deusto.weblab.client.ui.widgets.WlUtil;
import es.deusto.weblab.client.ui.widgets.WlVerticalPanel;

public abstract class LoggedBaseWindow extends BaseWindow {

    	protected interface ILoggedBaseWindowCallback {
    	    public void onLogoutButtonClicked();
    	}
    	
    	protected ILoggedBaseWindowCallback callback;
    	
	// Widgets
    	protected WlHorizontalPanel headerPanel;
    	protected WlVerticalPanel contentPanel;
	
	// DTOs
	protected User user;

	protected LoggedBaseWindow(IConfigurationManager configurationManager, User user, ILoggedBaseWindowCallback callback){
	    	super(configurationManager);
	    	this.user = user;
	    	this.callback = callback;
	}

	@Override
	protected void loadWidgets(){
	    super.loadWidgets();

		this.headerPanel = new WlHorizontalPanel();
		this.headerPanel.setWidth("100%");
		this.headerPanel.setStyleName("north-panel");
		this.headerPanel.setVerticalAlignment(HasVerticalAlignment.ALIGN_MIDDLE);
		this.headerPanel.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_RIGHT);
		this.headerPanel.setHeight("60px");
		
		final Image logo = new Image(GWT.getModuleBaseURL() + "img/logo-header.png");
		logo.setTitle("WebLab-Deusto");
		this.headerPanel.add(logo);
		
		final Label userLabel = new Label(WlUtil.escapeNotQuote(this.user.getFullName()));
		this.headerPanel.add(userLabel);
		
		final Label separatorLabel = new Label("|");
		this.headerPanel.add(separatorLabel);
		
		final Anchor logoutLink = new Anchor(this.i18nMessages.logOut());
		logoutLink.addClickHandler(new ClickHandler(){
			public void onClick(ClickEvent sender) {
				LoggedBaseWindow.this.callback.onLogoutButtonClicked();
			}
		});
		this.headerPanel.add(logoutLink);

		this.headerPanel.setCellHorizontalAlignment(logo, HasHorizontalAlignment.ALIGN_LEFT);
		this.headerPanel.setCellHorizontalAlignment(userLabel, HasHorizontalAlignment.ALIGN_RIGHT);		
		this.headerPanel.setCellHorizontalAlignment(separatorLabel, HasHorizontalAlignment.ALIGN_CENTER);
		this.headerPanel.setCellHorizontalAlignment(logoutLink, HasHorizontalAlignment.ALIGN_LEFT);
		this.headerPanel.setCellWidth(separatorLabel, "20px");
		
		this.mainPanel.add(this.headerPanel);
		
		this.contentPanel = new WlVerticalPanel();
		this.contentPanel.setWidth("100%");
		this.contentPanel.setStyleName("center-panel");
		this.contentPanel.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
		
		this.mainPanel.add(this.contentPanel);
	}
}