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
package es.deusto.weblab.client.lab.ui.themes.es.deusto.weblab.defaultweb;

import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.HasHorizontalAlignment;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;

import es.deusto.weblab.client.HistoryProperties;
import es.deusto.weblab.client.configuration.IConfigurationManager;
import es.deusto.weblab.client.dto.experiments.ExperimentAllowed;
import es.deusto.weblab.client.dto.experiments.ExperimentID;
import es.deusto.weblab.client.dto.reservations.WaitingConfirmationReservationStatus;
import es.deusto.weblab.client.dto.reservations.WaitingInstancesReservationStatus;
import es.deusto.weblab.client.dto.reservations.WaitingReservationStatus;
import es.deusto.weblab.client.dto.users.User;
import es.deusto.weblab.client.lab.controller.ILabController;
import es.deusto.weblab.client.lab.experiments.ExperimentBase;
import es.deusto.weblab.client.lab.ui.LabThemeBase;
import es.deusto.weblab.client.lab.ui.themes.es.deusto.weblab.defaultweb.AllowedExperimentsWindow.IAllowedExperimentsWindowCallback;
import es.deusto.weblab.client.lab.ui.themes.es.deusto.weblab.defaultweb.ExperimentWindow.IExperimentWindowCallback;
import es.deusto.weblab.client.lab.ui.themes.es.deusto.weblab.defaultweb.LoginWindow.ILoginWindowCallback;

public class DefaultTheme extends LabThemeBase {

	public static class Configuration {
		public static final String HOST_ENTITY_IMAGE        = "host.entity.image";
		public static final String HOST_ENTITY_LOGIN_IMAGE  = "host.entity.image.login";
		public static final String HOST_ENTITY_MOBILE_IMAGE = "host.entity.image.mobile";
		public static final String HOST_ENTITY_LINK         = "host.entity.link";
	}
	
	public static class Style {
		public static final String ERROR_MESSAGE  = "wl-error_message";
		public static final String MAIN_TITLE     = "wl-main_title";
	}

	private final IConfigurationManager configurationManager;
	private final ILabController controller;
	

	// Window management
	private BaseWindow activeWindow = null; // Pointer to the window being used
	private final VerticalPanel themePanel;	
	private LoginWindow loginWindow;
	private AllowedExperimentsWindow allowedExperimentsWindow;
	private ExperimentWindow experimentWindow;

	// DTOs
	private User user;
	private ExperimentAllowed[] experimentsAllowed;
	private ExperimentAllowed experimentAllowed;
	private ExperimentBase experimentBase;

	public DefaultTheme(final IConfigurationManager configurationManager, final ILabController controller){
		this.configurationManager = configurationManager;
		this.controller = controller;
		
		this.themePanel = new VerticalPanel();
		this.themePanel.setWidth("100%");
		this.themePanel.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
	}

	@Override
	public Widget getWidget(){
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
	public void onLoaded(){
		if(this.user == null){
			if(this.loginWindow != null){
				this.loginWindow.setUsernameFocus();
			}
		}
	}

	@Override
	public void onLoggedIn(User user)
	{
		this.user = user;
		// feedback?
		this.controller.retrieveAllowedExperiments();
	}

	@Override
	public void onAllowedExperimentsRetrieved(ExperimentAllowed[] experimentsAllowed) {
		this.loadAllowedExperimentsWindow();
	}
	
	@Override
	public void setAllowedExperiments(ExperimentAllowed[] experimentsAllowed) {
		this.experimentsAllowed = experimentsAllowed;
	}

	@Override
	public void onExperimentChosen(final ExperimentAllowed experimentAllowed, ExperimentBase experimentBase, boolean reserved) {
		this.experimentAllowed = experimentAllowed;
		this.experimentBase = experimentBase;

		// Important note: the calling order MUST be this or FileUpload will cause problems
		this.loadExperimentWindow();
		this.themePanel.add(this.experimentWindow.getWidget());    
		this.experimentWindow.loadExperimentReservationPanels(reserved);
		// end of Important note
	}
	
	@Override
	public void onExperimentInteractionFinished(){
		this.experimentWindow.onExperimentInteractionFinished();
	}

	@Override
	public void onWaitingReservation(WaitingReservationStatus reservationStatus) {
		this.experimentWindow.showWaitingReservation(reservationStatus.getPosition());
	}

	@Override
	public void onWaitingReservationConfirmation(WaitingConfirmationReservationStatus reservationStatus) {
		this.experimentWindow.showWaitingReservationConfirmation();
	}	

	@Override
	public void onExperimentReserved(ExperimentID experimentID, ExperimentBase experimentBase){
		this.experimentBase = experimentBase;

		this.experimentWindow.loadUsingExperimentPanels();
	}
	
	@Override
	public void onRemoteExperimentReserved(String url, String remoteReservationId) {
		this.experimentWindow.loadRemoteExperimentPanel(url, remoteReservationId);
	}

	@Override
	public void onCleanReservation() {
		this.controller.cleanExperimentPanel();
	}	

	@Override
	public void onLoggedOut() {
		this.clearSession();
		this.loadLoginWindow();
		this.loginWindow.setLoginFocus();
	}

	/*
	 * Alternative scenarios
	 */

	@Override	
	public void onWrongLoginOrPasswordGiven(){
		if(this.loginWindow != null)
			this.loginWindow.showWrongLoginOrPassword();
	}

	@Override
	public void onWaitingInstances(WaitingInstancesReservationStatus reservationStatus) {
		this.experimentWindow.showWaitingInstances(reservationStatus.getPosition() + 1); // the first one in the queue is 0
	}	

	@Override
	public void onError(String message) {
		this.showError(message);
	}

	@Override
	public void onErrorAndFinishReservation(String message) {
		this.showError(message);
		//TODO It doesn't "FinishReservation"
	}

	@Override
	public void onErrorAndFinishSession(String message) {
		this.loadLoginWindow();
		this.showError(message);
	}	

	@Override
	public void onMessage(String message){
		if(this.activeWindow != null)
			this.activeWindow.showMessage(message);
		else
			Window.alert(message);
	}

	/*
	 * Window management
	 */

	private void loadLoginWindow()
	{
		this.clearWindow();

		this.loginWindow = new LoginWindow(this.configurationManager, new ILoginWindowCallback(){
			@Override
			public void onLoginButtonClicked(String username, String password) {
				DefaultTheme.this.controller.login(username, password);
			}			
		});
		this.activeWindow = this.loginWindow;

		this.themePanel.add(this.loginWindow.getWidget());	    
	}

	private void loadAllowedExperimentsWindow() {
		this.clearWindow();
		
		HistoryProperties.removeValuesWithoutUpdating(HistoryProperties.EXPERIMENT_CATEGORY, HistoryProperties.EXPERIMENT_NAME, HistoryProperties.PAGE);
		HistoryProperties.setValue(HistoryProperties.PAGE, HistoryProperties.HOME);

		this.allowedExperimentsWindow = new AllowedExperimentsWindow(this.configurationManager, this.user, this.experimentsAllowed, new IAllowedExperimentsWindowCallback(){
			@Override
			public void onChooseExperimentButtonClicked(
					ExperimentAllowed experimentAllowed) {
				DefaultTheme.this.controller.chooseExperiment(experimentAllowed);
			}

			@Override
			public void onLogoutButtonClicked() {
				DefaultTheme.this.controller.logout();
			}
			
			@Override
			public boolean startedLoggedIn(){
				return DefaultTheme.this.controller.startedLoggedIn();
			}			
		}
		);
		this.activeWindow = this.allowedExperimentsWindow;

		this.themePanel.add(this.allowedExperimentsWindow.getWidget());
		
		final ExperimentAllowed [] failedExperiments = this.allowedExperimentsWindow.getFailedLoadingExperiments();
		final StringBuilder builder = new StringBuilder("Due to a misconfiguration in configuration.js, the system could not load:");
		for(ExperimentAllowed experiment : failedExperiments)
			builder.append(" " + experiment + ",");
		if(failedExperiments.length > 0)
			showError(builder.toString());
	}	

	private void loadExperimentWindow()
	{
		this.clearWindow();

		this.experimentWindow = new ExperimentWindow(this.configurationManager, this.user, this.experimentAllowed, this.experimentBase, new IExperimentWindowCallback(){
			@Override
			public void disableFinishOnClose() {
				DefaultTheme.this.controller.disableFinishOnClose();
			}
			
			@Override
			public boolean startedLoggedIn(){
				return DefaultTheme.this.controller.startedLoggedIn();
			}
			
			@Override
			public boolean startedReserved(){
				return DefaultTheme.this.controller.startedReserved();
			}
			
			@Override
			public void onReserveButtonClicked() {
				DefaultTheme.this.controller.reserveExperiment(DefaultTheme.this.experimentAllowed.getExperiment().getExperimentUniqueName());
			}

			@Override
			public void onBackButtonClicked() {
				DefaultTheme.this.loadAllowedExperimentsWindow();
			}

			@Override
			public void onFinishButtonClicked() {
				DefaultTheme.this.controller.finishReservation();
			}

			@Override
			public void onLogoutButtonClicked() {
				DefaultTheme.this.controller.finishReservationAndLogout();
			}
		}
		);
		this.activeWindow = this.experimentWindow;
	}

	/*
	 * Auxiliar methods
	 */

	 private void clearWindow(){
		 this.loginWindow = null;
		 if(this.allowedExperimentsWindow != null) {
			 this.allowedExperimentsWindow.dispose();
			 this.allowedExperimentsWindow = null;
		 }
		 this.experimentWindow = null;
		 while(this.themePanel.getWidgetCount() > 0)
			 this.themePanel.remove(0);
	 }

	 private void clearSession() {
		 this.user = null;
		 this.experimentsAllowed = null;
		 this.experimentBase = null;
		 this.experimentAllowed = null;
	 }

	 private void showError(String message) {
		 if(this.activeWindow != null)
			 this.activeWindow.showError(message);
		 else
			 Window.alert(message);
	 }	
}
