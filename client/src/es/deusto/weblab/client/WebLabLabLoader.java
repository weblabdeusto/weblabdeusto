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

import com.google.gwt.user.client.Cookies;
import com.google.gwt.user.client.Window;

import es.deusto.weblab.client.configuration.ConfigurationManager;
import es.deusto.weblab.client.dto.SessionID;
import es.deusto.weblab.client.lab.comm.ILabCommunication;
import es.deusto.weblab.client.lab.comm.LabCommunication;
import es.deusto.weblab.client.lab.controller.ILabController;
import es.deusto.weblab.client.lab.controller.PollingHandler;
import es.deusto.weblab.client.lab.controller.LabController;
import es.deusto.weblab.client.lab.experiments.ExperimentFactory;
import es.deusto.weblab.client.lab.ui.LabThemeBase;
import es.deusto.weblab.client.lab.ui.LabThemeFactory;
import es.deusto.weblab.client.lab.ui.LabThemeFactory.IWlLabThemeLoadedCallback;
import es.deusto.weblab.client.ui.audio.AudioManager;


public class WebLabLabLoader {

	private static final String SESSION_ID_URL_PARAM = "session_id";
	private static final String WEBLAB_SESSION_ID_COOKIE = "weblabsessionid";
	private static final String FACEBOOK_URL_PARAM = "facebook";
	
	private ConfigurationManager configurationManager;
	private WebLabClient weblabClient;
	
	public WebLabLabLoader(WebLabClient weblabClient, ConfigurationManager configurationManager){
		this.configurationManager = configurationManager;
		this.weblabClient = weblabClient;
	}
	
	public void loadLabApp() {
		
		// We need to initialize the AudioManager singleton
		AudioManager.initialize(this.configurationManager);
		
		try{
			ExperimentFactory.loadExperiments(this.configurationManager);
		}catch(final Exception e){
			this.weblabClient.showError("Error checking experiments: " + e.getMessage());
			e.printStackTrace();
			return;
		}
		
		final ILabCommunication communications = new LabCommunication(
				this.configurationManager
		);
		
		final PollingHandler pollingHandler = new PollingHandler(
				this.configurationManager 
		);
		
		final boolean isUsingMobile = this.weblabClient.isMobile();
		
		final ILabController controller = new LabController(
				this.configurationManager,
				communications,
				pollingHandler,
				isUsingMobile,
				this.isFacebook()
		);
		
		if(this.isFacebook())
			this.weblabClient.setMaxWidth(WebLabClient.MAX_FACEBOOK_WIDTH);
		
		pollingHandler.setController(controller);
		
		final IWlLabThemeLoadedCallback themeLoadedCallback = new IWlLabThemeLoadedCallback() {
			
			@Override
			public void onThemeLoaded(LabThemeBase theme) {
				controller.setUIManager(theme);
				try{
					String providedCredentials = Window.Location.getParameter(WebLabLabLoader.SESSION_ID_URL_PARAM);
					if(providedCredentials == null)
						providedCredentials = HistoryProperties.getValue(WebLabLabLoader.SESSION_ID_URL_PARAM);
					
					if(providedCredentials == null)
						theme.onInit(); // If it's still null...
					else{
						final String sessionId;
						final int position = providedCredentials.indexOf(';');
						if(position >= 0){
							sessionId = providedCredentials.substring(0, position);
							final String cookie = providedCredentials.substring(position + 1);
							Cookies.setCookie(WebLabLabLoader.WEBLAB_SESSION_ID_COOKIE, cookie, null, null, "/", false);
						}else
							sessionId = providedCredentials;
						controller.startLoggedIn(new SessionID(sessionId));
					}
				}catch(final Exception e){
					WebLabLabLoader.this.weblabClient.showError("Error initializing theme: " + e.getMessage());
					e.printStackTrace();
					return;
				}

				WebLabLabLoader.this.weblabClient.putWidget(theme.getWidget());
				theme.onLoaded();
			}
			
			@Override
			public void onFailure(Throwable e) {
				WebLabLabLoader.this.weblabClient.showError("Error creating theme: " + e.getMessage() + "; " + e);
				return;
			}
		};
		
		try {
			LabThemeFactory.themeFactory(
					this.configurationManager,
					controller, 
					this.configurationManager.getProperty(
							WebLabClient.THEME_PROPERTY, 
							WebLabClient.DEFAULT_THEME
						),
					isUsingMobile,
					themeLoadedCallback
				);
		} catch (final Exception e){
			this.weblabClient.showError("Error creating theme: " + e.getMessage() + "; " + e);
			return;
		}	
	}
	
	private boolean isFacebook(){
	    final String urlSaysIsFacebook = Window.Location.getParameter(WebLabLabLoader.FACEBOOK_URL_PARAM);
	    return urlSaysIsFacebook != null && (urlSaysIsFacebook.toLowerCase().equals("yes") || urlSaysIsFacebook.toLowerCase().equals("true"));
	}
}