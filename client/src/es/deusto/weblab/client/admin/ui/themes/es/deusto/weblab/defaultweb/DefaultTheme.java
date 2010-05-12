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

import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;

import es.deusto.weblab.client.admin.controller.IWlAdminController;
import es.deusto.weblab.client.admin.ui.WlAdminThemeBase;
import es.deusto.weblab.client.configuration.IConfigurationManager;

public class DefaultTheme extends WlAdminThemeBase {
	
	private final IConfigurationManager configurationManager;
	private final IWlAdminController controller;
	
	private VerticalPanel vp;
	
	public DefaultTheme(IConfigurationManager configurationManager, IWlAdminController controller) {
		this.configurationManager = configurationManager;
		this.controller = controller;
		
		this.vp = new VerticalPanel();
	}

	@Override
	public Widget getWidget() {
		return this.vp;
	}

	@Override
	public void onInit() {
		Label l = new Label("hello admin app!");
		this.vp.add(l);		
	}
}
