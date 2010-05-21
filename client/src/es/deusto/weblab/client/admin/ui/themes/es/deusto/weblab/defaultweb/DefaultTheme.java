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

import java.util.ArrayList;
import java.util.Date;

import com.google.gwt.user.client.ui.HasHorizontalAlignment;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;

import es.deusto.weblab.client.admin.controller.IWlAdminController;
import es.deusto.weblab.client.admin.ui.WlAdminThemeBase;
import es.deusto.weblab.client.admin.ui.themes.es.deusto.weblab.defaultweb.AdminPanelWindow.IAdminPanelWindowCallback;
import es.deusto.weblab.client.admin.ui.themes.es.deusto.weblab.defaultweb.LoginWindow.ILoginWindowCallback;
import es.deusto.weblab.client.configuration.IConfigurationManager;
import es.deusto.weblab.client.dto.experiments.Experiment;
import es.deusto.weblab.client.dto.experiments.ExperimentUse;
import es.deusto.weblab.client.dto.users.Group;
import es.deusto.weblab.client.dto.users.User;

public class DefaultTheme extends WlAdminThemeBase {
	
	private final IConfigurationManager configurationManager;
	private final IWlAdminController controller;

	// DTOs
	private User user;
	
	// Window management
	private BaseWindow activeWindow = null; // Pointer to the window being used
	private final VerticalPanel themePanel;	
	private LoginWindow loginWindow;
	private AdminPanelWindow adminPanelWindow;
	
	public DefaultTheme(IConfigurationManager configurationManager, IWlAdminController controller) {
		this.configurationManager = configurationManager;
		this.controller = controller;
		
		this.themePanel = new VerticalPanel();
		this.themePanel.setWidth("100%");
		this.themePanel.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
	}

	@Override
	public Widget getWidget() {
		return this.themePanel;
	}

	/*
	 * "Happy path" scenario
	 */

	@Override
	public void onInit() {
		this.loadLoginWindow();
	}

	@Override
	public void onLoggedIn(User user) {
		this.user = user;
		// Feedback...?
		// TODO: controller.somethingToRetrieveNeededInformation (or just to paint)
		this.loadAdminPanelWindow();
	}

	@Override
	public void onLoggedOut() {
		this.clearSession();
		this.loadLoginWindow();
	}

	/*
	 * Alternative scenarios
	 */

	@Override
	public void onErrorAndFinishSession(String message) {
		this.loadLoginWindow();
		this.showError(message);
	}

	@Override
	public void onWrongLoginOrPasswordGiven() {
		this.loginWindow.showWrongLoginOrPassword();
	}

	@Override
	public void onError(String message) {
		this.showError(message);
	}	
	
	/*
	 * Window management
	 */

	private void loadLoginWindow()
	{
		this.clearWindow();

		this.loginWindow = new LoginWindow(this.configurationManager, new ILoginWindowCallback(){
			public void onLoginButtonClicked(String username, String password) {
				DefaultTheme.this.controller.login(username, password);
			}			
		});
		this.activeWindow = this.loginWindow;

		this.themePanel.add(this.loginWindow.getWidget());	    
	}

	private void loadAdminPanelWindow() {
		this.clearWindow();

		this.adminPanelWindow = new AdminPanelWindow(this.configurationManager, this.user, new IAdminPanelWindowCallback(){
			@Override
			public void onLogoutButtonClicked() {
				DefaultTheme.this.controller.logout();
			}

			@Override
			public ArrayList<Experiment> getExperiments() {
				return DefaultTheme.this.controller.getExperiments();
			}

			@Override
			public ArrayList<Group> getGroups() {
				return DefaultTheme.this.controller.getGroups();
			}

			@Override
			public ArrayList<ExperimentUse> onSearchButtonClicked(Date fromDate, Date toDate, Group group, Experiment experiment) {
				return DefaultTheme.this.controller.getExperimentUses(fromDate, toDate, group, experiment);
			}
		});
		this.activeWindow = this.adminPanelWindow;

		this.themePanel.add(this.adminPanelWindow.getWidget());	    
	}

	/*
	 * Auxiliar methods
	 */

	 private void clearWindow(){
		 this.loginWindow = null;
		 while(this.themePanel.getWidgetCount() > 0)
			 this.themePanel.remove(0);
	 }

	 private void clearSession() {
		 this.user = null;
	 }
	 
	 private void showError(String message) {
		 this.activeWindow.showError(message);
	 }
}
