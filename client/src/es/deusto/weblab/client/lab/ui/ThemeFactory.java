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
package es.deusto.weblab.client.lab.ui;

import com.google.gwt.core.client.GWT;
import com.google.gwt.core.client.RunAsyncCallback;

import es.deusto.weblab.client.configuration.IConfigurationManager;
import es.deusto.weblab.client.lab.controller.IWebLabController;
import es.deusto.weblab.client.lab.ui.exceptions.themes.ThemeNotFoundException;
import es.deusto.weblab.client.lab.ui.themes.es.deusto.weblab.defaultmobile.DefaultMobileTheme;
import es.deusto.weblab.client.lab.ui.themes.es.deusto.weblab.defaultweb.DefaultTheme;

public class ThemeFactory {
	
	public interface IThemeLoadedCallback{
		public void onThemeLoaded(ThemeBase theme);
		public void onFailure(Throwable reason);
	}
	
	public static void themeFactory(final IConfigurationManager configurationManager, final IWebLabController controller, String themeName, boolean mobile, final IThemeLoadedCallback callback){
		if(themeName.equals("deusto")){
			if(mobile){
				GWT.runAsync(new RunAsyncCallback() {
					@Override
					public void onSuccess() {
						final ThemeBase themeBase = new DefaultMobileTheme(configurationManager, controller);
						callback.onThemeLoaded(themeBase);
					}
					@Override
					public void onFailure(Throwable reason) {}
				});
			}else{
				GWT.runAsync(new RunAsyncCallback() {
					@Override
					public void onSuccess() {
						final ThemeBase themeBase = new DefaultTheme(configurationManager, controller);
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
