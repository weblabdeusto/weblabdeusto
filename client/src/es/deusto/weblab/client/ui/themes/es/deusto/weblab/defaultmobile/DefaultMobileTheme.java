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

package es.deusto.weblab.client.ui.themes.es.deusto.weblab.defaultmobile;

import com.google.gwt.user.client.ui.HasHorizontalAlignment;
import com.google.gwt.user.client.ui.Widget;

import es.deusto.weblab.client.configuration.IConfigurationManager;
import es.deusto.weblab.client.controller.IWebLabController;
import es.deusto.weblab.client.dto.experiments.ExperimentAllowed;
import es.deusto.weblab.client.dto.experiments.ExperimentID;
import es.deusto.weblab.client.dto.reservations.ConfirmedReservationStatus;
import es.deusto.weblab.client.dto.reservations.WaitingConfirmationReservationStatus;
import es.deusto.weblab.client.dto.reservations.WaitingInstancesReservationStatus;
import es.deusto.weblab.client.dto.reservations.WaitingReservationStatus;
import es.deusto.weblab.client.dto.users.User;
import es.deusto.weblab.client.exceptions.experiments.WlExperimentException;
import es.deusto.weblab.client.experiments.ExperimentBase;
import es.deusto.weblab.client.ui.ThemeBase;
import es.deusto.weblab.client.ui.themes.es.deusto.weblab.defaultmobile.LoginWindow.ILoginWindowCallback;
import es.deusto.weblab.client.ui.themes.es.deusto.weblab.defaultmobile.AllowedExperimentsWindow.IAllowedExperimentsWindowCallback;
import es.deusto.weblab.client.ui.widgets.WlVerticalPanel;

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
	public void onExperimentChosen(ExperimentAllowed experimentAllowed,
			ExperimentBase experimentBase) {
		// TODO Auto-generated method stub
		
	}

	@Override
	public void onWaitingReservation(WaitingReservationStatus reservationStatus) {
		// TODO Auto-generated method stub
		
	}

	@Override
	public void onWaitingReservationConfirmation(
			WaitingConfirmationReservationStatus reservationStatus) {
		// TODO Auto-generated method stub
		
	}

	@Override
	public void onExperimentReserved(
			ConfirmedReservationStatus reservationStatus,
			ExperimentID experimentID, ExperimentBase experimentBase)
			throws WlExperimentException {
		// TODO Auto-generated method stub
		
	}

	@Override
	public void onReservationFinished() {
		// TODO Auto-generated method stub
		
	}

	@Override
	public void onLoggedOut() {
		// TODO Auto-generated method stub
		
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
		// TODO Auto-generated method stub
		
	}

	@Override
	public void onWrongLoginOrPasswordGiven() {
		// TODO Auto-generated method stub
		
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

	 private void showError(String message) {
		 this.activeWindow.showError(message);
	 }	

}
