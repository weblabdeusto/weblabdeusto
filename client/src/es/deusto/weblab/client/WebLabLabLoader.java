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

package es.deusto.weblab.client;

import com.google.gwt.user.client.Cookies;
import com.google.gwt.user.client.Window;

import es.deusto.weblab.client.configuration.ConfigurationManager;
import es.deusto.weblab.client.dto.SessionID;
import es.deusto.weblab.client.dto.experiments.Category;
import es.deusto.weblab.client.dto.experiments.ExperimentID;
import es.deusto.weblab.client.lab.comm.ILabCommunication;
import es.deusto.weblab.client.lab.comm.LabCommunication;
import es.deusto.weblab.client.lab.controller.ILabController;
import es.deusto.weblab.client.lab.controller.IValidSessionCallback;
import es.deusto.weblab.client.lab.controller.PollingHandler;
import es.deusto.weblab.client.lab.controller.LabController;
import es.deusto.weblab.client.lab.experiments.ExperimentFactory;
import es.deusto.weblab.client.lab.ui.LabThemeBase;
import es.deusto.weblab.client.lab.ui.LabThemeFactory;
import es.deusto.weblab.client.lab.ui.LabThemeFactory.IWlLabThemeLoadedCallback;
import es.deusto.weblab.client.ui.audio.AudioManager;


public class WebLabLabLoader {

	private static final String SESSION_ID_URL_PARAM     = "session_id";
	private static final String RESERVATION_ID_URL_PARAM = "reservation_id";
	public static final String WEBLAB_SESSION_ID_COOKIE = "weblabsessionid";
	public static final String LOGIN_WEBLAB_SESSION_ID_COOKIE = "loginweblabsessionid";
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
		
		WebLabClient.IS_MOBILE = isUsingMobile; 
		
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
			public void onThemeLoaded(final LabThemeBase theme) {
				controller.setUIManager(theme);
				boolean stillWaiting = false;
				try{
					String providedSessionId = Window.Location.getParameter(WebLabLabLoader.SESSION_ID_URL_PARAM);
					if(providedSessionId == null)
						providedSessionId = HistoryProperties.getValue(WebLabLabLoader.SESSION_ID_URL_PARAM);
					
					String providedReservationId = Window.Location.getParameter(WebLabLabLoader.RESERVATION_ID_URL_PARAM);
					if(providedReservationId == null)
						providedReservationId = HistoryProperties.getValue(WebLabLabLoader.RESERVATION_ID_URL_PARAM);
					
					ExperimentID experimentId = null;
					if(providedReservationId != null){
						final String selectedExperimentName     = HistoryProperties.getValue(HistoryProperties.EXPERIMENT_NAME);
						final String selectedExperimentCategory = HistoryProperties.getValue(HistoryProperties.EXPERIMENT_CATEGORY);
						
						experimentId = new ExperimentID(new Category(selectedExperimentCategory), selectedExperimentName);
					}
					
					if(providedReservationId != null && experimentId != null){
						final String reservationId;
						final int position = providedReservationId.indexOf(';');
						if(position >= 0){
							reservationId = providedReservationId.substring(0, position);
							final String cookie = providedReservationId.substring(position + 1);
							Cookies.setCookie(WebLabLabLoader.WEBLAB_SESSION_ID_COOKIE, cookie, null, null, WebLabClient.baseLocation + "/weblab/", false);
						}else
							reservationId = providedReservationId;
						controller.startReserved(new SessionID(reservationId), experimentId);
						
					}else if(providedSessionId != null){
						final String sessionId;
						final int position = providedSessionId.indexOf(';');
						if(position >= 0){
							sessionId = providedSessionId.substring(0, position);
							final String cookie = providedSessionId.substring(position + 1);
							Cookies.setCookie(WebLabLabLoader.WEBLAB_SESSION_ID_COOKIE, cookie, null, null, WebLabClient.baseLocation + "/weblab/", false);
						}else
							sessionId = providedSessionId;
						controller.startLoggedIn(new SessionID(sessionId), true);
					}else{
						final String possibleSessionId = Cookies.getCookie(WebLabLabLoader.WEBLAB_SESSION_ID_COOKIE);
						if(possibleSessionId == null) {
							theme.onInit(); // If it's still null...
						} else {
							final SessionID tentativeSessionId;
							if(possibleSessionId.contains("."))
								tentativeSessionId = new SessionID(possibleSessionId.substring(0, possibleSessionId.indexOf('.')));
							else
								tentativeSessionId = new SessionID(possibleSessionId);
							controller.checkSessionIdStillValid(tentativeSessionId, new IValidSessionCallback() {
								@Override
								public void sessionRejected() {
									theme.onInit();
									WebLabLabLoader.this.weblabClient.putWidget(theme.getWidget());
									theme.onLoaded();
								}
								
								@Override
								public void sessionConfirmed() {
									controller.startLoggedIn(tentativeSessionId, false);
								}
							});
						}
					}
				
				}catch(final Exception e){
					WebLabLabLoader.this.weblabClient.showError("Error initializing theme: " + e.getMessage());
					e.printStackTrace();
					return;
				}

				if(!stillWaiting) {
					WebLabLabLoader.this.weblabClient.putWidget(theme.getWidget());
					theme.onLoaded();
				}
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
