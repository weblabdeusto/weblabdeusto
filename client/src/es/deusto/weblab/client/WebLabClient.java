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
import com.google.gwt.dom.client.Document;
import com.google.gwt.dom.client.Element;
import com.google.gwt.dom.client.ScriptElement;
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
import es.deusto.weblab.client.ui.audio.AudioManager;
import es.deusto.weblab.client.ui.widgets.WlWaitingLabel;

public class WebLabClient implements EntryPoint {
	
	private static final String WEBLAB_SESSION_ID_COOKIE = "weblabsessionid";
	public static final int MAX_FACEBOOK_WIDTH = 735;
	private static final String MAIN_SLOT = "weblab_slot";
	private static final String SCRIPT_CONFIG_FILE = GWT.getModuleBaseURL() + "configuration.js";
	private static final String SESSION_ID_URL_PARAM = "session_id";	
	public static final String MOBILE_URL_PARAM = "mobile";
	private static final String LOCALE_URL_PARAM = "locale";
	private static final String FACEBOOK_URL_PARAM = "facebook";
	private static final String ADMIN_URL_PARAM = "admin";
	
	public static final String LOCALE_COOKIE = "weblabdeusto.locale";
	public static final String MOBILE_COOKIE = "weblabdeusto.mobile";

	private static final String THEME_PROPERTY = "theme";
	private static final String DEFAULT_THEME = "deusto";
	private static final String GOOGLE_ANALYTICS_TRACKING_CODE = "google.analytics.tracking.code";
	private static final String SOUND_ENABLED = "sound.enabled";
	
	// These are the minimum width and height to choose the standard version over the
	// mobile one automatically. The choice can nonetheless be forced upon the client
	// by explicitly specifying the "mobile" GET variable.
	private static final int MIN_NON_MOBILE_WIDTH = 480;
	private static final int MIN_NON_MOBILE_HEIGHT = 350;
	private static final int MIN_NON_MOBILE_AREA = 350 * 300;
	
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
	
	private boolean isFacebook(){
	    final String urlSaysIsFacebook = Window.Location.getParameter(WebLabClient.FACEBOOK_URL_PARAM);
	    return urlSaysIsFacebook != null && (urlSaysIsFacebook.toLowerCase().equals("yes") || urlSaysIsFacebook.toLowerCase().equals("true"));
	}
	
	/**
	 * Check whether we must display the mobile or the standard version. If the "mobile" GET var is 
	 * specified, we will comply. If it is not, we will display the standard version if the browser
	 * resolution of the user is large enough, and the mobile one otherwise.
	 * 
	 * @return True if we should display the mobile version, false otherwise
	 */
	private boolean isMobile(){
		
		// If it was explicitly specified through the GET var, do what it says and set a cookie.
		final String urlSaysIsMobile = Window.Location.getParameter(WebLabClient.MOBILE_URL_PARAM);
		if(urlSaysIsMobile != null) {
			if(urlSaysIsMobile.toLowerCase().equals("yes") || 
					urlSaysIsMobile.toLowerCase().equals("true")) {
				Cookies.setCookie(MOBILE_COOKIE, "true");
				return true;
			} else if(urlSaysIsMobile.toLowerCase().equals("no") ||
					urlSaysIsMobile.toLowerCase().equals("false")) {
				Cookies.setCookie(MOBILE_COOKIE, "false");
				return false;
			} else {
				// We are receiving an unexpected value for the mobile parameter.
				// We will not make assumptions about this parameter, and we will
				// delete the mobile cookie. 
				Cookies.removeCookie(MOBILE_COOKIE);
			}
		}
		
		// It was not specified. Now, we will first try to find a cookie that tells us what to do.
		final String cookieSaysIsMobile = Cookies.getCookie(MOBILE_COOKIE);
		if(cookieSaysIsMobile != null) 
			return cookieSaysIsMobile.equals("true");
		
		
		// It was not specified, and we did not find a cookie, so we will choose the best option
		// depending on the user's browser resolution.
		final int width = Window.getClientWidth();
		final int height = Window.getClientHeight();
		final int area = width * height;

        // We check everything > 0 just in case there are issues with frames (such as facebook iframes)
		if ((width > 0 && width <= MIN_NON_MOBILE_WIDTH) || (height > 0 && height <= MIN_NON_MOBILE_HEIGHT) || (area > 0 && area <= MIN_NON_MOBILE_AREA))
			return true;
		return false;
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
	
	public static String getNewUrl(String parameterName, String parameterValue){
		String newUrl = Window.Location.getPath() + "?";
		final Map<String, List<String>> parameters = Window.Location.getParameterMap();

		for(final String parameter : parameters.keySet())
		    if(!parameter.equals(parameterName)){
        		    String value = "";
        		    for(final String v : parameters.get(parameter))
        		    	value = v;
        		    newUrl += parameter + "=" + value + "&";
		    }
		    
		newUrl += parameterName + "=" + parameterValue;
		return newUrl;
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
		
		// We need to initialize the AudioManager singleton
		AudioManager.initialize(this.configurationManager);
		
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
				isUsingMobile,
				isFacebook()
		);
		
		if(isFacebook())
			RootPanel.get(WebLabClient.MAIN_SLOT).setWidth(MAX_FACEBOOK_WIDTH + "px");
		
		pollingHandler.setController(controller);
		
		final IWlLabThemeLoadedCallback themeLoadedCallback = new IWlLabThemeLoadedCallback() {
			
			@Override
			public void onThemeLoaded(WlLabThemeBase theme) {
				controller.setUIManager(theme);
				try{
					final String providedCredentials = Window.Location.getParameter(WebLabClient.SESSION_ID_URL_PARAM);
					if(providedCredentials == null)
						theme.onInit();
					else{
						final String sessionId;
						final int position = providedCredentials.indexOf(';');
						if(position >= 0){
							sessionId = providedCredentials.substring(0, position);
							final String cookie = providedCredentials.substring(position + 1);
							Cookies.setCookie(WEBLAB_SESSION_ID_COOKIE, cookie, null, null, "/", false);
						}else
							sessionId = providedCredentials;
						controller.startLoggedIn(new SessionID(sessionId));
					}
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
				final String trackingCode = WebLabClient.this.configurationManager.getProperty(GOOGLE_ANALYTICS_TRACKING_CODE, null);
				if(trackingCode != null)
					loadGoogleAnalytics(trackingCode);
				
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
	
    private void loadGoogleAnalytics(String trackingCode) {
        final ScriptElement gaqScript = Document.get().createScriptElement(
            "var _gaq = _gaq || [];" + 
            "_gaq.push(['_setAccount', '" + trackingCode + "']);" + 
            "_gaq.push(['_trackPageview']);"
         );
        final Element s = Document.get().getElementsByTagName("script").getItem(0);
        s.getParentNode().insertBefore(gaqScript, s);

        final ScriptElement ga = Document.get().createScriptElement();
        ga.setSrc(("https:".equals(Window.Location.getProtocol()) ? "https://ssl" : "http://www") + ".google-analytics.com/ga.js");
        ga.setType("text/javascript");
        ga.setAttribute("async", "true");
        s.getParentNode().insertBefore(ga, s);
    }	
}
