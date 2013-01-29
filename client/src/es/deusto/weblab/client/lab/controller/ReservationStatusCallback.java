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
package es.deusto.weblab.client.lab.controller;

import es.deusto.weblab.client.comm.exceptions.CommException;
import es.deusto.weblab.client.comm.exceptions.core.SessionNotFoundException;
import es.deusto.weblab.client.configuration.IConfigurationManager;
import es.deusto.weblab.client.dto.experiments.ExperimentID;
import es.deusto.weblab.client.dto.reservations.ReservationStatus;
import es.deusto.weblab.client.lab.comm.ILabCommunication;
import es.deusto.weblab.client.lab.comm.callbacks.IReservationCallback;
import es.deusto.weblab.client.lab.controller.LabController.TimerCreator;
import es.deusto.weblab.client.lab.controller.exceptions.UnknownReservationException;
import es.deusto.weblab.client.lab.controller.reservations.ReservationStatusTransition;
import es.deusto.weblab.client.lab.controller.reservations.ReservationStatusTransitionFactory;
import es.deusto.weblab.client.lab.experiments.ExperimentBase;
import es.deusto.weblab.client.lab.ui.IUIManager;

public class ReservationStatusCallback implements IReservationCallback{
	private IUIManager            uimanager;
	private IConfigurationManager configurationManager;
	private IPollingHandler       pollingHandler;
	private TimerCreator          timerCreator;
	private ILabCommunication  communications;
	private ExperimentID          experimentBeingReserved;
	private ExperimentBase        experimentBaseBeingReserved;
	private ILabController     controller;
	
	ReservationStatusCallback(){}
	
	@Override
	public void onSuccess(ReservationStatus reservationStatus) {
		try {
			final ReservationStatusTransition reservationStatusTransition = ReservationStatusTransitionFactory.create(
							reservationStatus, 
							this
						);
			reservationStatusTransition.perform(reservationStatus);
		} catch (final UnknownReservationException e) {
			this.uimanager.onErrorAndFinishReservation("Error trying to process the reservation: " + e.getMessage());
			//TODO: how to tell the controller that this has finished?
		}
	}

	@Override
	public void onFailure(CommException e) {
		if(e instanceof SessionNotFoundException) {
			this.controller.logout();
			return;
		}
		this.uimanager.onErrorAndFinishReservation(e.getMessage());
		//TODO: how to tell the controller that this has finished?
	}

	// Getters
	public IUIManager getUimanager() {
		return this.uimanager;
	}

	public IConfigurationManager getConfigurationManager() {
		return this.configurationManager;
	}

	public IPollingHandler getPollingHandler() {
		return this.pollingHandler;
	}

	public TimerCreator getTimerCreator() {
		return this.timerCreator;
	}

	public ILabCommunication getCommunications() {
		return this.communications;
	}

	public ExperimentID getExperimentBeingReserved(){
		return this.experimentBeingReserved;
	}
	
	public ILabController getController(){
		return this.controller;
	}
	
	public ExperimentBase getExperimentBaseBeingReserved(){
	    	return this.experimentBaseBeingReserved;
	}

	void setUimanager(IUIManager uimanager) {
		this.uimanager = uimanager;
	}
	
	void setConfigurationManager(IConfigurationManager configurationManager) {
		this.configurationManager = configurationManager;
	}

	void setPollingHandler(IPollingHandler pollingHandler) {
		this.pollingHandler = pollingHandler;
	}

	void setTimerCreator(TimerCreator timerCreator) {
		this.timerCreator = timerCreator;
	}

	void setCommunications(ILabCommunication communications) {
		this.communications = communications;
	}

	void setExperimentBeingReserved(ExperimentID experimentId){
		this.experimentBeingReserved = experimentId;
	}
	
	void setController(ILabController controller){
		this.controller = controller;
	}
	
	void setExperimentBaseBeingReserved(ExperimentBase experimentBaseBeingReserved){
	    this.experimentBaseBeingReserved = experimentBaseBeingReserved;
	}
}
