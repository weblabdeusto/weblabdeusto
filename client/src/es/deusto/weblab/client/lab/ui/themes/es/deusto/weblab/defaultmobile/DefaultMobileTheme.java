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

package es.deusto.weblab.client.lab.ui.themes.es.deusto.weblab.defaultmobile;

import com.google.gwt.user.client.ui.HasHorizontalAlignment;
import com.google.gwt.user.client.ui.Widget;

import es.deusto.weblab.client.configuration.IConfigurationManager;
import es.deusto.weblab.client.dto.experiments.ExperimentAllowed;
import es.deusto.weblab.client.dto.experiments.ExperimentID;
import es.deusto.weblab.client.dto.reservations.ConfirmedReservationStatus;
import es.deusto.weblab.client.dto.reservations.WaitingConfirmationReservationStatus;
import es.deusto.weblab.client.dto.reservations.WaitingInstancesReservationStatus;
import es.deusto.weblab.client.dto.reservations.WaitingReservationStatus;
import es.deusto.weblab.client.dto.users.User;
import es.deusto.weblab.client.lab.controller.IWebLabController;
import es.deusto.weblab.client.lab.experiments.ExperimentBase;
import es.deusto.weblab.client.lab.ui.ThemeBase;
import es.deusto.weblab.client.lab.ui.themes.es.deusto.weblab.defaultmobile.AllowedExperimentsWindow.IAllowedExperimentsWindowCallback;
import es.deusto.weblab.client.lab.ui.themes.es.deusto.weblab.defaultmobile.ExperimentWindow.IExperimentWindowCallback;
import es.deusto.weblab.client.lab.ui.themes.es.deusto.weblab.defaultmobile.LoginWindow.ILoginWindowCallback;
import es.deusto.weblab.client.lab.ui.widgets.WlVerticalPanel;

public class DefaultMobileTheme extends ThemeBase {

	private final WlVerticalPanel themePanel;	
	private final IConfigurationManager configurationManager;
	private final IWebLabController controller;
	
	private BaseWindow activeWindow = null; // Pointer to the window being used
	
	private LoginWindow loginWindow;
	private AllowedExperimentsWindow allowedExperimentsWindow;
	private ExperimentWindow experimentWindow;
	
	private User user;
	private ExperimentAllowed[] experimentsAllowed;
	private ExperimentAllowed experimentAllowed;
	private ExperimentBase experimentBase;
	
	public DefaultMobileTheme(IConfigurationManager configurationManager, IWebLabController controller){
		this.configurationManager = configurationManager;
		this.controller           = controller;
		
		this.themePanel = new WlVerticalPanel();
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
	public void onAllowedExperimentsRetrieved(
			ExperimentAllowed[] experimentsAllowed) {
		this.experimentsAllowed = experimentsAllowed;
		this.loadAllowedExperimentsWindow();
	}

	@Override
	public void onExperimentChosen(ExperimentAllowed experimentAllowed, ExperimentBase experimentBase) {
		this.experimentAllowed = experimentAllowed;
		this.experimentBase = experimentBase;

		// Important note: the calling order MUST be this or FileUpload will cause problems
		this.loadExperimentWindow();
		this.themePanel.add(this.experimentWindow.getWidget());    
		this.experimentWindow.loadExperimentReservationPanels();
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
	public void onExperimentReserved(ConfirmedReservationStatus reservationStatus, ExperimentID experimentID, ExperimentBase experimentBase){
		this.experimentBase = experimentBase;

		// Important note: the calling order MUST be this or FileUpload will cause problems
		this.experimentWindow.loadUsingExperimentPanels(reservationStatus.getTime());
		// end of Important note
	}

	@Override
	public void onReservationFinished() {
		this.experimentBase.getUI().end(); // Critical: Everything (i.e: timers) must be disposed.
		this.loadAllowedExperimentsWindow();	    
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
		this.activeWindow.showMessage(message);
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
			public void onLoginButtonClicked(String username, String password) {
				DefaultMobileTheme.this.controller.login(username, password);
			}			
		});
		this.activeWindow = this.loginWindow;

		this.themePanel.add(this.loginWindow.getWidget());	    
	}

	private void loadAllowedExperimentsWindow() {
		this.clearWindow();

		this.allowedExperimentsWindow = new AllowedExperimentsWindow(this.configurationManager, this.user, this.experimentsAllowed, new IAllowedExperimentsWindowCallback(){
			public void onChooseExperimentButtonClicked(
					ExperimentAllowed experimentAllowed) {
				DefaultMobileTheme.this.controller.chooseExperiment(experimentAllowed);
			}

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
			public void onReserveButtonClicked() {
				DefaultMobileTheme.this.controller.reserveExperiment(DefaultMobileTheme.this.experimentAllowed.getExperiment().getExperimentID());
			}

			public void onBackButtonClicked() {
				DefaultMobileTheme.this.loadAllowedExperimentsWindow();
			}

			public void onFinishButtonClicked() {
				DefaultMobileTheme.this.controller.finishReservation();
			}

			public void onLogoutButtonClicked() {
				DefaultMobileTheme.this.controller.finishReservationAndLogout();
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
		 this.activeWindow.showError(message);
	 }	

}
