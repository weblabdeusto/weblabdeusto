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
import es.deusto.weblab.client.ui.widgets.WlVerticalPanel;

public class DefaultMobileTheme extends ThemeBase {

	private final WlVerticalPanel themePanel;	
	private final IConfigurationManager configurationManager;
	private final IWebLabController controller;
	
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

	@Override
	public void onAllowedExperimentsRetrieved(
			ExperimentAllowed[] experimentsAllowed) {
		// TODO Auto-generated method stub
		
	}

	@Override
	public void onError(String message) {
		// TODO Auto-generated method stub
		
	}

	@Override
	public void onErrorAndFinishReservation(String message) {
		// TODO Auto-generated method stub
		
	}

	@Override
	public void onErrorAndFinishSession(String message) {
		// TODO Auto-generated method stub
		
	}

	@Override
	public void onExperimentChoosen(ExperimentAllowed experimentAllowed,
			ExperimentBase experimentBase) {
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
	public void onInit() {
		// TODO Auto-generated method stub
		
	}

	@Override
	public void onLoggedIn(User user) {
		// TODO Auto-generated method stub
		
	}

	@Override
	public void onLoggedOut() {
		// TODO Auto-generated method stub
		
	}

	@Override
	public void onMessage(String message) {
		// TODO Auto-generated method stub
		
	}

	@Override
	public void onReservationFinished() {
		// TODO Auto-generated method stub
		
	}

	@Override
	public void onWaitingInstances(
			WaitingInstancesReservationStatus reservationStatus) {
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
	public void onWrongLoginOrPasswordGiven() {
		// TODO Auto-generated method stub
		
	}
	
}
