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
package es.deusto.weblab.client;

import java.util.List;
import java.util.Map;

import com.google.gwt.core.client.EntryPoint;
import com.google.gwt.core.client.GWT;
import com.google.gwt.user.client.Cookies;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.RootPanel;
import com.google.gwt.user.client.ui.Widget;

import es.deusto.weblab.client.comm.IWebLabCommunication;
import es.deusto.weblab.client.comm.WebLabCommunication;
import es.deusto.weblab.client.configuration.ConfigurationManager;
import es.deusto.weblab.client.configuration.IConfigurationLoadedCallback;
import es.deusto.weblab.client.dto.SessionID;
import es.deusto.weblab.client.lab.controller.IWebLabController;
import es.deusto.weblab.client.lab.controller.PollingHandler;
import es.deusto.weblab.client.lab.controller.WebLabController;
import es.deusto.weblab.client.lab.ui.ThemeBase;
import es.deusto.weblab.client.lab.ui.ThemeFactory;
import es.deusto.weblab.client.lab.ui.ThemeFactory.IThemeLoadedCallback;
import es.deusto.weblab.client.lab.ui.widgets.WlWaitingLabel;

public class WebLabClient implements EntryPoint {
	
	private static final String MAIN_SLOT = "weblab_slot";
	private static final String SCRIPT_CONFIG_FILE = "configuration.js";
	private static final String HOSTED_CONFIG_FILE = "debug_configuration.js";
	private static final String SESSION_ID_URL_PARAM = "session_id";	
	private static final String MOBILE_URL_PARAM = "mobile";
	private static final String LOCALE_URL_PARAM = "locale";
	
	public static final String LOCALE_COOKIE = "weblabdeusto.locale";

	private static final String THEME_PROPERTY = "theme";
	private static final String DEFAULT_THEME = "deusto";
	
	private ConfigurationManager configurationManager;
	
	private void putWidget(Widget widget){
		while(RootPanel.get(WebLabClient.MAIN_SLOT).getWidgetCount() > 0)
			RootPanel.get(WebLabClient.MAIN_SLOT).remove(0);
		RootPanel.get(WebLabClient.MAIN_SLOT).add(widget);
	}
	
	private void showError(String message){
		final Label errorMessage = new Label(message);
		this.putWidget(errorMessage);
	}
	
	private boolean localeConfigured(){
	    return Window.Location.getParameter(WebLabClient.LOCALE_URL_PARAM) != null;
	}
	
	private boolean isMobile(){
		final String urlSaysIsMobile = Window.Location.getParameter(MOBILE_URL_PARAM);
		return urlSaysIsMobile != null && (urlSaysIsMobile.toLowerCase().equals("yes") || urlSaysIsMobile.toLowerCase().equals("true")); 
	}
	
	private void selectLanguage(){
		final String weblabLocaleCookie = Cookies.getCookie(WebLabClient.LOCALE_COOKIE);
		if(weblabLocaleCookie != null && !this.localeConfigured()){
			WebLabClient.refresh(weblabLocaleCookie);
		}
	}

	public static void refresh(String locale){
		String newUrl = Window.Location.getPath() + "?";
		Map<String, List<String>> parameters = Window.Location.getParameterMap();

		for(String parameter : parameters.keySet())
		    if(!parameter.equals(WebLabClient.LOCALE_URL_PARAM)){
        		    String value = "";
        		    for(String v : parameters.get(parameter))
        		    	value = v;
        		    newUrl += parameter + "=" + value + "&";
		    }
		    
		newUrl += WebLabClient.LOCALE_URL_PARAM + "=" + locale;
		Window.Location.replace(newUrl);
	}
	
	public void mainWebLab(){
		final WlWaitingLabel loadingLabel = new WlWaitingLabel("Loading WebLab");
		loadingLabel.start();
		this.putWidget(loadingLabel.getWidget());
				
		this.selectLanguage();
		
		final String configFile = GWT.isScript() ? WebLabClient.SCRIPT_CONFIG_FILE : WebLabClient.HOSTED_CONFIG_FILE;
		
		this.configurationManager = new ConfigurationManager(configFile, new IConfigurationLoadedCallback(){
			public void onLoaded() {
				final IWebLabCommunication communications = new WebLabCommunication(
						WebLabClient.this.configurationManager
				);
				
				final PollingHandler pollingHandler = new PollingHandler(
						WebLabClient.this.configurationManager 
				);
				
				final boolean isUsingMobile = isMobile();
				
				final IWebLabController controller = new WebLabController(
						WebLabClient.this.configurationManager,
						communications,
						pollingHandler,
						isUsingMobile
				);
				
				pollingHandler.setController(controller);
				
				final IThemeLoadedCallback themeLoadedCallback = new IThemeLoadedCallback() {
					
					@Override
					public void onThemeLoaded(ThemeBase theme) {
						controller.setUIManager(theme);
						try{
							final String sessionId = Window.Location.getParameter(WebLabClient.SESSION_ID_URL_PARAM);
							if(sessionId == null)
								theme.onInit();
							else
								controller.startLoggedIn(new SessionID(sessionId));
						}catch(Exception e){
							WebLabClient.this.showError("Error initializing theme: " + e.getMessage());
							e.printStackTrace();
							return;
						}

						WebLabClient.this.putWidget(theme.getWidget());
					}
					
					@Override
					public void onFailure(Throwable e) {
						showError("Error creating theme: " + e.getMessage() + "; " + e);
						return;
					}
				};
				
				try {
					ThemeFactory.themeFactory(
							WebLabClient.this.configurationManager,
							controller, 
							WebLabClient.this.configurationManager.getProperty(
									WebLabClient.THEME_PROPERTY, 
									WebLabClient.DEFAULT_THEME
								),
							isUsingMobile,
							themeLoadedCallback
						);
				} catch (Exception e){
					showError("Error creating theme: " + e.getMessage() + "; " + e);
					return;
				}
			}

			public void onFailure(Throwable t) {
				WebLabClient.this.showError("Error loading configuration file: " + t.getMessage());
			}
		});
		this.configurationManager.start();
	}

	public void onModuleLoad() {
		this.mainWebLab();
	}
}
