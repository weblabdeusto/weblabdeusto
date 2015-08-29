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
import com.google.gwt.user.client.ui.HasHorizontalAlignment;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;

import es.deusto.weblab.client.configuration.IConfigurationManager;
import es.deusto.weblab.client.i18n.IWebLabI18N;

public abstract class BaseWindow {
	
	protected final IConfigurationManager configurationManager;
	protected final IWebLabI18N i18nMessages;
	
	// Widgets
	protected VerticalPanel mainPanel;
	
	protected BaseWindow(IConfigurationManager configurationManager){
	    	this.configurationManager = configurationManager;
	    	this.i18nMessages = (IWebLabI18N)GWT.create(IWebLabI18N.class);
	}
	
	public Widget getWidget(){
		return this.mainPanel;
	}
	
	void loadWidgets() {
		this.mainPanel = new VerticalPanel();
		this.mainPanel.setStyleName("main-panel");
		this.mainPanel.setWidth("100%");
		this.mainPanel.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
	}
	
	abstract void showMessage(String message);
	abstract void showError(String message);
}
