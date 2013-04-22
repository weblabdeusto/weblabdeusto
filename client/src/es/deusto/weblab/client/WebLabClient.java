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

import java.util.List;
import java.util.Map;

import com.google.gwt.core.client.EntryPoint;
import com.google.gwt.core.client.GWT;
import com.google.gwt.dom.client.Document;
import com.google.gwt.dom.client.Element;
import com.google.gwt.dom.client.ScriptElement;
import com.google.gwt.i18n.client.LocaleInfo;
import com.google.gwt.user.client.Cookies;
import com.google.gwt.user.client.History;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.RootPanel;
import com.google.gwt.user.client.ui.Widget;

import es.deusto.weblab.client.configuration.ConfigurationManager;
import es.deusto.weblab.client.configuration.IConfigurationLoadedCallback;
import es.deusto.weblab.client.ui.widgets.WlWaitingLabel;

public abstract class WebLabClient implements EntryPoint {
	
	public static final String BASE_LOCATION = "base.location";
	public static final String DEFAULT_BASE_LOCATION = "";

	
    public static String baseLocation;
    
	public static String PROFILE_URL;
	
    public static boolean IS_MOBILE = false;

	public static final int MAX_FACEBOOK_WIDTH = 735;
	private static final String MAIN_SLOT = "weblab_slot";
	private static final String SCRIPT_CONFIG_FILE = GWT.getModuleBaseURL() + "configuration.js";
	public static final String MOBILE_URL_PARAM = "mobile";
	private static final String LOCALE_URL_PARAM = "locale";
	
	public static final String LOCALE_COOKIE = "weblabdeusto.locale";
	public static final String MOBILE_COOKIE = "weblabdeusto.mobile";
	
	public static final String HOST_ENTITY_DEFAULT_LANGUAGE = "host.entity.default.language";
	public static final String DEFAULT_HOST_ENTITY_DEFAULT_LANGUAGE = "en";

	public static final String THEME_PROPERTY = "theme";
	public static final String DEFAULT_THEME = "deusto";
	private static final String GOOGLE_ANALYTICS_TRACKING_CODE = "google.analytics.tracking.code";
	
	// These are the minimum width and height to choose the standard version over the
	// mobile one automatically. The choice can nonetheless be forced upon the client
	// by explicitly specifying the "mobile" GET variable.
	private static final int MIN_NON_MOBILE_WIDTH = 480;
	private static final int MIN_NON_MOBILE_HEIGHT = 350;
	private static final int MIN_NON_MOBILE_AREA = 350 * 300;
	
	public ConfigurationManager configurationManager;
	private boolean languageDecisionPending = false;

	public void putWidget(Widget widget){
		while(RootPanel.get(WebLabClient.MAIN_SLOT).getWidgetCount() > 0)
			RootPanel.get(WebLabClient.MAIN_SLOT).remove(0);
		RootPanel.get(WebLabClient.MAIN_SLOT).add(widget);
	}
	
	public void showError(String message){
		final Label errorMessage = new Label(message);
		this.putWidget(errorMessage);
	}
	
	private boolean localeConfigured(){
	    return Window.Location.getParameter(WebLabClient.LOCALE_URL_PARAM) != null;
	}

    public static String getLocale() {
	    return Window.Location.getParameter(WebLabClient.LOCALE_URL_PARAM);
    }
	
	/**
	 * Check whether we must display the mobile or the standard version. If the "mobile" GET var is 
	 * specified, we will comply. If it is not, we will display the standard version if the browser
	 * resolution of the user is large enough, and the mobile one otherwise.
	 * 
	 * @return True if we should display the mobile version, false otherwise
	 */
	boolean isMobile(){
		
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
	
	private void selectLanguage(){		
		if(localeConfigured())
			return;
		
		final String weblabLocaleCookie = Cookies.getCookie(WebLabClient.LOCALE_COOKIE);
		if(weblabLocaleCookie != null){
			String currentLocaleName = LocaleInfo.getCurrentLocale().getLocaleName();
			if(currentLocaleName.equals("default"))
				currentLocaleName = "en";
			if(!currentLocaleName.equals(weblabLocaleCookie))
				WebLabClient.refresh(weblabLocaleCookie);
			return;
		} 
				
		// Else, check if there is a default language. If there is, show it
		this.languageDecisionPending = true;
	}
	
	public static native String getAcceptLanguageHeader() /*-{
		return $wnd.acceptLanguageHeader;
	}-*/;
	
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
		newUrl += "#" + History.getToken();
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
		newUrl += "#" + History.getToken();
		Window.Location.replace(newUrl);
	}
	
	public abstract void loadApplication();
	
	@Override
	public void onModuleLoad() {
		HistoryProperties.load();

		final WlWaitingLabel loadingLabel = new WlWaitingLabel("Loading WebLab-Deusto");
		loadingLabel.start();
		this.putWidget(loadingLabel.getWidget());
		
		this.selectLanguage();		
		
		final String configFile = WebLabClient.SCRIPT_CONFIG_FILE;
		
		this.configurationManager = new ConfigurationManager(configFile, new IConfigurationLoadedCallback(){
			@Override
			public void onLoaded() {
                WebLabClient.baseLocation = WebLabClient.this.configurationManager.getProperty(BASE_LOCATION, DEFAULT_BASE_LOCATION);
                WebLabClient.PROFILE_URL  = WebLabClient.baseLocation + "/weblab/administration/profile/";
                
                if(WebLabClient.this.languageDecisionPending) {
        			String currentLocaleName = LocaleInfo.getCurrentLocale().getLocaleName();
        			if(currentLocaleName.equals("default"))
        				currentLocaleName = "en";

	        		try{
	        			if(getAcceptLanguageHeader() != null) {
	        				final String firstLanguage = getAcceptLanguageHeader().split(";")[0].split(",")[0].split("-")[0];
	        				if(!currentLocaleName.equals(firstLanguage)) {
	        					WebLabClient.refresh(firstLanguage);
		        				return;
	        				}
	        			}
	        		} catch (Exception e) {
	        			e.printStackTrace();
	        		}
	        		
	                final String hostDefaultLanguage = WebLabClient.this.configurationManager.getProperty(HOST_ENTITY_DEFAULT_LANGUAGE, DEFAULT_HOST_ENTITY_DEFAULT_LANGUAGE);
					if(!hostDefaultLanguage.equals("en") && WebLabClient.this.languageDecisionPending)
						refresh(hostDefaultLanguage);
                }
                
				final String trackingCode = WebLabClient.this.configurationManager.getProperty(GOOGLE_ANALYTICS_TRACKING_CODE, null);
				if(trackingCode != null)
					loadGoogleAnalytics(trackingCode);
				
				loadApplication();
			}

			@Override
			public void onFailure(Throwable t) {
				WebLabClient.this.showError("Error loading configuration file: " + t.getMessage());
			}
		});
		this.configurationManager.start();
	}
	
	public void setMaxWidth(int width){
		RootPanel.get(WebLabClient.MAIN_SLOT).setWidth(width + "px");
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
