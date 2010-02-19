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
import com.google.gwt.user.client.ui.HasHorizontalAlignment;
import com.google.gwt.user.client.ui.Widget;

import es.deusto.weblab.client.configuration.IConfigurationManager;
import es.deusto.weblab.client.ui.themes.es.deusto.weblab.defaulttheme.i18n.IWebLabDeustoThemeMessages;
import es.deusto.weblab.client.ui.widgets.WlVerticalPanel;

public abstract class BaseWindow {
	
	protected final IConfigurationManager configurationManager;
	protected final IWebLabDeustoThemeMessages i18nMessages;

	// Widgets
	protected WlVerticalPanel mainPanel;
	
	protected BaseWindow(IConfigurationManager configurationManager){
	    	this.configurationManager = configurationManager;
	    	this.i18nMessages = (IWebLabDeustoThemeMessages)GWT.create(IWebLabDeustoThemeMessages.class);
	}
	
	public Widget getWidget(){
		return this.mainPanel;
	}
	
	void loadWidgets() {
		this.mainPanel = new WlVerticalPanel();
		this.mainPanel.setStyleName("main-panel");
		this.mainPanel.setWidth("100%");
		this.mainPanel.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
	}
}
