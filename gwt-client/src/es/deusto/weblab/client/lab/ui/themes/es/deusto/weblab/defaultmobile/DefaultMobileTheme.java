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

package es.deusto.weblab.client.lab.ui.themes.es.deusto.weblab.defaultmobile;

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
import es.deusto.weblab.client.lab.ui.themes.es.deusto.weblab.defaultmobile.AllowedExperimentsWindow.IAllowedExperimentsWindowCallback;
import es.deusto.weblab.client.lab.ui.themes.es.deusto.weblab.defaultmobile.ExperimentWindow.IExperimentWindowCallback;
import es.deusto.weblab.client.lab.ui.themes.es.deusto.weblab.defaultmobile.LoginWindow.ILoginWindowCallback;


public class DefaultMobileTheme extends LabThemeBase {

	private final VerticalPanel themePanel;	
	private final IConfigurationManager configurationManager;
	private final ILabController controller;
	
	private BaseWindow activeWindow = null; // Pointer to the window being used
	
	private LoginWindow loginWindow;
	private AllowedExperimentsWindow allowedExperimentsWindow;
	private ExperimentWindow experimentWindow;
	
	private User user;
	private ExperimentAllowed[] experimentsAllowed;
	private ExperimentAllowed experimentAllowed;
	private ExperimentBase experimentBase;
	
	public DefaultMobileTheme(IConfigurationManager configurationManager, ILabController controller){
		this.configurationManager = configurationManager;
		this.controller           = controller;
		
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
	public void onLoggedIn(User user) {
		this.user = user;
		this.controller.retrieveAllowedExperiments();
	}

	@Override
	public void setAllowedExperiments(ExperimentAllowed[] experimentsAllowed) {
		this.experimentsAllowed = experimentsAllowed;
	}
	
	@Override
	public void onAllowedExperimentsRetrieved(ExperimentAllowed[] experimentsAllowed) {
		this.loadAllowedExperimentsWindow();
	}

	@Override
	public void onExperimentChosen(ExperimentAllowed experimentAllowed, ExperimentBase experimentBase, boolean reserved) {
		this.experimentAllowed = experimentAllowed;
		this.experimentBase = experimentBase;

		// Important note: the calling order MUST be this or FileUpload will cause problems
		this.loadExperimentWindow();
		this.themePanel.add(this.experimentWindow.getWidget());    
		this.experimentWindow.loadExperimentReservationPanels(reserved);
		// end of Important note
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
	public void onRemoteExperimentReserved(String url, String remoteReservationId){
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
	}


	/*
	 * Alternative scenarios
	 */
	
	@Override
	public void onError(String message) {
		this.showError(message);
	}

	@Override
	public void onErrorAndFinishReservation(String message) {
		this.showError(message);
	}

	@Override
	public void onErrorAndFinishSession(String message) {
		this.loadLoginWindow();
		this.showError(message);
	}

	@Override
	public void onMessage(String message) {
		if(this.activeWindow != null)
			this.activeWindow.showMessage(message);
		else
			Window.alert(message);
	}

	@Override
	public void onWaitingInstances(
			WaitingInstancesReservationStatus reservationStatus) {
		this.experimentWindow.showWaitingInstances(reservationStatus.getPosition() + 1); // the first one in the queue is 0
	}

	@Override
	public void onWrongLoginOrPasswordGiven() {
		this.loginWindow.showWrongLoginOrPassword();
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
				DefaultMobileTheme.this.controller.login(username, password);
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
				DefaultMobileTheme.this.controller.chooseExperiment(experimentAllowed);
			}

			@Override
			public void onLogoutButtonClicked() {
				DefaultMobileTheme.this.controller.logout();
			}
		});
		this.activeWindow = this.allowedExperimentsWindow;

		this.themePanel.add(this.allowedExperimentsWindow.getWidget());	    
	}	
	
	private void loadExperimentWindow() {
		this.clearWindow();

		this.experimentWindow = new ExperimentWindow(this.configurationManager, this.user, this.experimentAllowed, this.experimentBase, new IExperimentWindowCallback(){
			@Override
			public void onReserveButtonClicked() {
				DefaultMobileTheme.this.controller.reserveExperiment(DefaultMobileTheme.this.experimentAllowed.getExperiment().getExperimentUniqueName());
			}

			@Override
			public void onBackButtonClicked() {
				DefaultMobileTheme.this.loadAllowedExperimentsWindow();
			}

			@Override
			public void onFinishButtonClicked() {
				DefaultMobileTheme.this.controller.finishReservation();
			}

			@Override
			public void onLogoutButtonClicked() {
				DefaultMobileTheme.this.controller.finishReservationAndLogout();
			}

			@Override
			public void disableFinishOnClose() {
				DefaultMobileTheme.this.controller.disableFinishOnClose();
			}
		});
		this.activeWindow = this.experimentWindow;
	}

	/*
	 * Auxiliar methods
	 */

	 private void clearWindow(){
		 this.loginWindow = null;
		 this.allowedExperimentsWindow = null;
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

	@Override
	public void onExperimentInteractionFinished() {
		this.experimentWindow.onExperimentInteractionFinished();
	}	

}
