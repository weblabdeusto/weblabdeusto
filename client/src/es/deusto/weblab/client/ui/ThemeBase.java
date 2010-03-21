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
package es.deusto.weblab.client.ui;

import com.google.gwt.core.client.GWT;
import com.google.gwt.user.client.ui.Widget;

import es.deusto.weblab.client.ui.IUIManager;
import es.deusto.weblab.client.ui.themes.es.deusto.weblab.defaultweb.i18n.IWebLabDeustoThemeMessages;

public abstract class ThemeBase implements IUIManager{

	protected final IWebLabDeustoThemeMessages i18nMessages;
	
	protected ThemeBase() {
	    this.i18nMessages = (IWebLabDeustoThemeMessages)GWT.create(IWebLabDeustoThemeMessages.class);
	}
	
	public abstract Widget getWidget();
}
