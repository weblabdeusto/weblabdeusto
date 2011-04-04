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

import es.deusto.weblab.client.admin.comm.IWlAdminCommunication;
import es.deusto.weblab.client.admin.comm.WlAdminCommunication;
import es.deusto.weblab.client.admin.controller.IWlAdminController;
import es.deusto.weblab.client.admin.controller.WlAdminController;
import es.deusto.weblab.client.admin.ui.WlAdminThemeFactory;
import es.deusto.weblab.client.admin.ui.WlAdminThemeFactory.IWlAdminThemeLoadedCallback;
import es.deusto.weblab.client.configuration.ConfigurationManager;

public class WebLabAdminLoader {
	
	private ConfigurationManager configurationManager;
	private WebLabClient weblabClient;
	
	public WebLabAdminLoader(WebLabClient weblabClient, ConfigurationManager configurationManager){
		this.configurationManager = configurationManager;
		this.weblabClient = weblabClient;
	}
	

	public void loadAdminApp() {

		final IWlAdminCommunication communications = new WlAdminCommunication(
				this.configurationManager
		);
		
		final IWlAdminController controller = new WlAdminController(
				this.configurationManager,
				communications
		);
		
		final IWlAdminThemeLoadedCallback themeLoadedCallback = new IWlAdminThemeLoadedCallback() {
			
			@Override
			public void onThemeLoaded(es.deusto.weblab.client.admin.ui.WlAdminThemeBase theme) {
				controller.setUIManager(theme);
				try{
					theme.onInit();
				}catch(final Exception e){
					WebLabAdminLoader.this.weblabClient.showError("Error initializing theme: " + e.getMessage());
					e.printStackTrace();
					return;
				}

				WebLabAdminLoader.this.weblabClient.putWidget(theme.getWidget());
			}
			
			@Override
			public void onFailure(Throwable e) {
				WebLabAdminLoader.this.weblabClient.showError("Error creating theme: " + e.getMessage() + "; " + e);
				return;
			}
		};
		
		try {
			WlAdminThemeFactory.themeFactory(
					this.configurationManager,
					controller, 
					this.configurationManager.getProperty(
							WebLabClient.THEME_PROPERTY, 
							WebLabClient.DEFAULT_THEME
						),
					themeLoadedCallback
				);
		} catch (final Exception e){
			this.weblabClient.showError("Error creating theme: " + e.getMessage() + "; " + e);
			return;
		}
	}
}
