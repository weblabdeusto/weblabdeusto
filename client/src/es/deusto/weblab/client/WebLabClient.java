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
import com.google.gwt.core.client.RunAsyncCallback;
import com.google.gwt.user.client.Cookies;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.RootPanel;
import com.google.gwt.user.client.ui.Widget;

import es.deusto.weblab.client.admin.comm.IWlAdminCommunication;
import es.deusto.weblab.client.admin.comm.WlAdminCommunication;
import es.deusto.weblab.client.admin.controller.IWlAdminController;
import es.deusto.weblab.client.admin.controller.WlAdminController;
import es.deusto.weblab.client.admin.ui.WlAdminThemeFactory;
import es.deusto.weblab.client.admin.ui.WlAdminThemeFactory.IWlAdminThemeLoadedCallback;
import es.deusto.weblab.client.configuration.ConfigurationManager;
import es.deusto.weblab.client.configuration.IConfigurationLoadedCallback;
import es.deusto.weblab.client.dto.SessionID;
import es.deusto.weblab.client.lab.comm.IWlLabCommunication;
import es.deusto.weblab.client.lab.comm.WlLabCommunication;
import es.deusto.weblab.client.lab.controller.IWlLabController;
import es.deusto.weblab.client.lab.controller.PollingHandler;
import es.deusto.weblab.client.lab.controller.WlLabController;
import es.deusto.weblab.client.lab.experiments.ExperimentFactory;
import es.deusto.weblab.client.lab.ui.WlLabThemeBase;
import es.deusto.weblab.client.lab.ui.WlLabThemeFactory;
import es.deusto.weblab.client.lab.ui.WlLabThemeFactory.IWlLabThemeLoadedCallback;
import es.deusto.weblab.client.ui.widgets.WlWaitingLabel;

public class WebLabClient implements EntryPoint {
	
	private static final String MAIN_SLOT = "weblab_slot";
	private static final String SCRIPT_CONFIG_FILE = "configuration.js";
	private static final String SESSION_ID_URL_PARAM = "session_id";	
	private static final String MOBILE_URL_PARAM = "mobile";
	private static final String LOCALE_URL_PARAM = "locale";
	private static final String ADMIN_URL_PARAM = "admin";
	
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
		final String urlSaysIsMobile = Window.Location.getParameter(WebLabClient.MOBILE_URL_PARAM);
		return urlSaysIsMobile != null && (urlSaysIsMobile.toLowerCase().equals("yes") || urlSaysIsMobile.toLowerCase().equals("true")); 
	}
	
	private boolean wantsAdminApp(){
		final String urlSaysWantsAdminApp = Window.Location.getParameter(WebLabClient.ADMIN_URL_PARAM);
		return urlSaysWantsAdminApp != null && (urlSaysWantsAdminApp.toLowerCase().equals("yes") || urlSaysWantsAdminApp.toLowerCase().equals("true")); 
	}	
	
	private void selectLanguage(){
		final String weblabLocaleCookie = Cookies.getCookie(WebLabClient.LOCALE_COOKIE);
		if(weblabLocaleCookie != null && !this.localeConfigured()){
			WebLabClient.refresh(weblabLocaleCookie);
		}
	}

	public static void refresh(String locale){
		String newUrl = Window.Location.getPath() + "?";
		final Map<String, List<String>> parameters = Window.Location.getParameterMap();

		for(final String parameter : parameters.keySet())
		    if(!parameter.equals(WebLabClient.LOCALE_URL_PARAM)){
        		    String value = "";
        		    for(final String v : parameters.get(parameter))
        		    	value = v;
        		    newUrl += parameter + "=" + value + "&";
		    }
		    
		newUrl += WebLabClient.LOCALE_URL_PARAM + "=" + locale;
		Window.Location.replace(newUrl);
	}
	
	public void loadLabApp() {
		try{
			ExperimentFactory.loadExperiments(WebLabClient.this.configurationManager);
		}catch(final Exception e){
			WebLabClient.this.showError("Error checking experiments: " + e.getMessage());
			e.printStackTrace();
			return;
		}
		
		final IWlLabCommunication communications = new WlLabCommunication(
				WebLabClient.this.configurationManager
		);
		
		final PollingHandler pollingHandler = new PollingHandler(
				WebLabClient.this.configurationManager 
		);
		
		final boolean isUsingMobile = this.isMobile();
		
		final IWlLabController controller = new WlLabController(
				WebLabClient.this.configurationManager,
				communications,
				pollingHandler,
				isUsingMobile
		);
		
		pollingHandler.setController(controller);
		
		final IWlLabThemeLoadedCallback themeLoadedCallback = new IWlLabThemeLoadedCallback() {
			
			@Override
			public void onThemeLoaded(WlLabThemeBase theme) {
				controller.setUIManager(theme);
				try{
					final String sessionId = Window.Location.getParameter(WebLabClient.SESSION_ID_URL_PARAM);
					if(sessionId == null)
						theme.onInit();
					else
						controller.startLoggedIn(new SessionID(sessionId));
				}catch(final Exception e){
					WebLabClient.this.showError("Error initializing theme: " + e.getMessage());
					e.printStackTrace();
					return;
				}

				WebLabClient.this.putWidget(theme.getWidget());
			}
			
			@Override
			public void onFailure(Throwable e) {
				WebLabClient.this.showError("Error creating theme: " + e.getMessage() + "; " + e);
				return;
			}
		};
		
		try {
			WlLabThemeFactory.themeFactory(
					WebLabClient.this.configurationManager,
					controller, 
					WebLabClient.this.configurationManager.getProperty(
							WebLabClient.THEME_PROPERTY, 
							WebLabClient.DEFAULT_THEME
						),
					isUsingMobile,
					themeLoadedCallback
				);
		} catch (final Exception e){
			this.showError("Error creating theme: " + e.getMessage() + "; " + e);
			return;
		}	
	}

	
	public void loadAdminApp() {

		final IWlAdminCommunication communications = new WlAdminCommunication(
				WebLabClient.this.configurationManager
		);
		
		final IWlAdminController controller = new WlAdminController(
				WebLabClient.this.configurationManager,
				communications
		);
		
		final IWlAdminThemeLoadedCallback themeLoadedCallback = new IWlAdminThemeLoadedCallback() {
			
			@Override
			public void onThemeLoaded(es.deusto.weblab.client.admin.ui.WlAdminThemeBase theme) {
				controller.setUIManager(theme);
				try{
					final String sessionId = Window.Location.getParameter(WebLabClient.SESSION_ID_URL_PARAM);
					theme.onInit();
					if(sessionId != null)
						controller.startLoggedIn(new SessionID(sessionId));
				}catch(final Exception e){
					WebLabClient.this.showError("Error initializing theme: " + e.getMessage());
					e.printStackTrace();
					return;
				}

				WebLabClient.this.putWidget(theme.getWidget());
			}
			
			@Override
			public void onFailure(Throwable e) {
				WebLabClient.this.showError("Error creating theme: " + e.getMessage() + "; " + e);
				return;
			}
		};
		
		try {
			WlAdminThemeFactory.themeFactory(
					WebLabClient.this.configurationManager,
					controller, 
					WebLabClient.this.configurationManager.getProperty(
							WebLabClient.THEME_PROPERTY, 
							WebLabClient.DEFAULT_THEME
						),
					themeLoadedCallback
				);
		} catch (final Exception e){
			this.showError("Error creating theme: " + e.getMessage() + "; " + e);
			return;
		}
	}
	
	@Override
	public void onModuleLoad() {
		final WlWaitingLabel loadingLabel = new WlWaitingLabel("Loading WebLab-Deusto");
		loadingLabel.start();
		this.putWidget(loadingLabel.getWidget());
				
		this.selectLanguage();
		
		final String configFile = WebLabClient.SCRIPT_CONFIG_FILE;
		
		this.configurationManager = new ConfigurationManager(configFile, new IConfigurationLoadedCallback(){
			@Override
			public void onLoaded() {
				if ( WebLabClient.this.wantsAdminApp() ) {
					GWT.runAsync(new RunAsyncCallback() {
						@Override
						public void onSuccess() {
							WebLabClient.this.loadAdminApp();
						}
						@Override
						public void onFailure(Throwable reason) {}
					});
				} else {
					GWT.runAsync(new RunAsyncCallback() {
						@Override
						public void onSuccess() {
							WebLabClient.this.loadLabApp();	
						}
						@Override
						public void onFailure(Throwable reason) {}
					});			
				}
			}

			@Override
			public void onFailure(Throwable t) {
				WebLabClient.this.showError("Error loading configuration file: " + t.getMessage());
			}
		});
		this.configurationManager.start();
	}
}
