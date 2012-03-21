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
package es.deusto.weblab.client.lab.ui;

import com.google.gwt.core.client.GWT;
import com.google.gwt.core.client.RunAsyncCallback;

import es.deusto.weblab.client.configuration.IConfigurationManager;
import es.deusto.weblab.client.lab.controller.ILabController;
import es.deusto.weblab.client.lab.ui.themes.es.deusto.weblab.defaultmobile.DefaultMobileTheme;
import es.deusto.weblab.client.lab.ui.themes.es.deusto.weblab.defaultweb.DefaultTheme;
import es.deusto.weblab.client.ui.exceptions.themes.ThemeNotFoundException;

public class LabThemeFactory {
	
	public interface IWlLabThemeLoadedCallback{
		public void onThemeLoaded(LabThemeBase theme);
		public void onFailure(Throwable reason);
	}
	
	public static void themeFactory(final IConfigurationManager configurationManager, final ILabController controller, String themeName, boolean mobile, final IWlLabThemeLoadedCallback callback){
		if(themeName.equals("deusto")){
			if(mobile){
				GWT.runAsync(new RunAsyncCallback() {
					@Override
					public void onSuccess() {
						final LabThemeBase themeBase = new DefaultMobileTheme(configurationManager, controller);
						callback.onThemeLoaded(themeBase);
					}
					@Override
					public void onFailure(Throwable reason) {}
				});
			}else{
				GWT.runAsync(new RunAsyncCallback() {
					@Override
					public void onSuccess() {
						final LabThemeBase themeBase = new DefaultTheme(configurationManager, controller);
						callback.onThemeLoaded(themeBase);
					}
					@Override
					public void onFailure(Throwable reason) {}
				});
			}
		}else
			callback.onFailure(new ThemeNotFoundException("Theme " + themeName + " not found"));
	}
}
