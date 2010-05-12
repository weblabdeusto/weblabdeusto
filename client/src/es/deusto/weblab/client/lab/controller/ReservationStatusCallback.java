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
package es.deusto.weblab.client.lab.controller;

import es.deusto.weblab.client.comm.exceptions.WlCommException;
import es.deusto.weblab.client.configuration.IConfigurationManager;
import es.deusto.weblab.client.dto.SessionID;
import es.deusto.weblab.client.dto.experiments.ExperimentID;
import es.deusto.weblab.client.dto.reservations.ReservationStatus;
import es.deusto.weblab.client.lab.comm.IWlLabCommunication;
import es.deusto.weblab.client.lab.comm.callbacks.IReservationCallback;
import es.deusto.weblab.client.lab.controller.WlLabController.TimerCreator;
import es.deusto.weblab.client.lab.controller.exceptions.WlUnknownReservationException;
import es.deusto.weblab.client.lab.controller.reservations.ReservationStatusTransition;
import es.deusto.weblab.client.lab.controller.reservations.ReservationStatusTransitionFactory;
import es.deusto.weblab.client.lab.experiments.ExperimentBase;
import es.deusto.weblab.client.lab.ui.IUIManager;

public class ReservationStatusCallback implements IReservationCallback{
	private IUIManager            uimanager;
	private IConfigurationManager configurationManager;
	private IPollingHandler       pollingHandler;
	private TimerCreator          timerCreator;
	private IWlLabCommunication  communications;
	private SessionID             sessionID;
	private ExperimentID          experimentBeingReserved;
	private ExperimentBase        experimentBaseBeingReserved;
	private IWlLabController     controller;
	
	ReservationStatusCallback(){}
	
	public void onSuccess(ReservationStatus reservationStatus) {
		try {
			final ReservationStatusTransition reservationStatusTransition = ReservationStatusTransitionFactory.create(
							reservationStatus, 
							this
						);
			reservationStatusTransition.perform(reservationStatus);
		} catch (final WlUnknownReservationException e) {
			this.uimanager.onErrorAndFinishReservation("Error trying to process the reservation: " + e.getMessage());
			//TODO: how to tell the controller that this has finished?
		}
	}

	public void onFailure(WlCommException e) {
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

	public IWlLabCommunication getCommunications() {
		return this.communications;
	}

	public SessionID getSessionID() {
		return this.sessionID;
	}
	
	public ExperimentID getExperimentBeingReserved(){
		return this.experimentBeingReserved;
	}
	
	public IWlLabController getController(){
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

	void setCommunications(IWlLabCommunication communications) {
		this.communications = communications;
	}

	void setSessionID(SessionID sessionID) {
		this.sessionID = sessionID;
	}
	
	void setExperimentBeingReserved(ExperimentID experimentId){
		this.experimentBeingReserved = experimentId;
	}
	
	void setController(IWlLabController controller){
		this.controller = controller;
	}
	
	void setExperimentBaseBeingReserved(ExperimentBase experimentBaseBeingReserved){
	    this.experimentBaseBeingReserved = experimentBaseBeingReserved;
	}
}
