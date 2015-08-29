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
package es.deusto.weblab.client.lab.ui.themes.es.deusto.weblab.defaultweb;

import com.google.gwt.core.client.GWT;
import com.google.gwt.user.client.ui.Widget;

import es.deusto.weblab.client.configuration.IConfigurationManager;
import es.deusto.weblab.client.i18n.IWebLabI18N;

abstract class BaseWindow extends Widget {
	
	protected final IConfigurationManager configurationManager;
	protected final IWebLabI18N i18nMessages;
	
	protected BaseWindow(IConfigurationManager configurationManager){
	    	this.configurationManager = configurationManager;
	    	this.i18nMessages = (IWebLabI18N)GWT.create(IWebLabI18N.class);
	}

	abstract Widget getWidget();
	abstract void showMessage(String message);
	abstract void showError(String message);
}
