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
package es.deusto.weblab.client.lab.ui;

import es.deusto.weblab.client.dto.experiments.ExperimentAllowed;
import es.deusto.weblab.client.dto.experiments.ExperimentID;
import es.deusto.weblab.client.dto.reservations.WaitingConfirmationReservationStatus;
import es.deusto.weblab.client.dto.reservations.WaitingInstancesReservationStatus;
import es.deusto.weblab.client.dto.reservations.WaitingReservationStatus;
import es.deusto.weblab.client.dto.users.User;
import es.deusto.weblab.client.lab.experiments.ExperimentBase;
import es.deusto.weblab.client.lab.experiments.exceptions.ExperimentException;
import es.deusto.weblab.client.testing.util.WebLabFake;

public class FakeUIManager extends WebLabFake implements IUIManager {

    public static final String ON_INIT 			                    = "FakeUIManager::onInit";
    public static final String ON_LOGGED_IN 			            = "FakeUIManager::onLoggedIn";
    public static final String ON_ALLOWED_EXPERIMENTS_RETRIEVED     = "FakeUIManager::onAllowedExperimentsRetrieved";
    public static final String ON_EXPERIMENT_CHOSEN 		        = "FakeUIManager::onExperimentChoosen";
    public static final String ON_WAITING_RESERVATION 		        = "FakeUIManager::onWaitingReservation";
    public static final String ON_WAITING_RESERVATION_CONFIRMATION  = "FakeUIManager::onWaitingReservationConfirmation";
    public static final String ON_EXPERIMENT_RESERVED 		        = "FakeUIManager::onExperimentReserved";
    public static final String ON_RESERVATION_FINISHED 	            = "FakeUIManager::onReservationFinished";
    public static final String ON_CLEAN_RESERVATION 	            = "FakeUIManager::onCleanReservation";
    public static final String ON_LOGGED_OUT 			            = "FakeUIManager::onLoggedOut";
    
    public static final String ON_WRONG_LOGIN_OR_PASSWORD_GIVEN     = "FakeUIManager::onWrongLoginOrPasswordGiven";
    public static final String ON_WAITING_INSTANCES 		        = "FakeUIManager::onWaitingInstances";
    public static final String ON_ERROR 			                = "FakeUIManager::onError";
    public static final String ON_ERROR_AND_FINISH_RESERVATION      = "FakeUIManager::onErrorAndFinishReservation";
    public static final String ON_ERROR_AND_FINISH_SESSION 	        = "FakeUIManager::onErrorAndFinishSession";
    public static final String ON_MESSAGE 			                = "FakeUIManager::onMessage";

    /*
     * Happy path scenario
     */
    
    @Override
    public void onInit() {
	this.append(FakeUIManager.ON_INIT);
    }

    @Override
    public void onLoggedIn(User user) {
	this.append(FakeUIManager.ON_LOGGED_IN, new Object[]{user});
    }

    @Override
    public void setAllowedExperiments(ExperimentAllowed[] experimentsAllowed) {
    }    

    @Override
    public void onAllowedExperimentsRetrieved(ExperimentAllowed[] experimentsAllowed) {
    	this.append(FakeUIManager.ON_ALLOWED_EXPERIMENTS_RETRIEVED, new Object[]{experimentsAllowed});
    }    
    
    @Override
    public void onExperimentChosen(ExperimentAllowed experimentAllowed, ExperimentBase experimentBase, boolean reserved) {
    	experimentBase.initialize();
    	this.append(FakeUIManager.ON_EXPERIMENT_CHOSEN, new Object[] {experimentAllowed, experimentBase});
    }
    
    @Override
    public void onWaitingReservation(WaitingReservationStatus reservationStatus) {
	this.append(FakeUIManager.ON_WAITING_RESERVATION, new Object[] {reservationStatus});
    }

    @Override
    public void onWaitingReservationConfirmation(
	    WaitingConfirmationReservationStatus reservationStatus) {
	this.append(FakeUIManager.ON_WAITING_RESERVATION_CONFIRMATION, new Object[] {reservationStatus});
    }

    @Override
    public void onExperimentReserved(
	    ExperimentID experimentID, ExperimentBase experimentBase)
	    throws ExperimentException {
	this.append(FakeUIManager.ON_EXPERIMENT_RESERVED, new Object[] {experimentBase});
    }    
    
    @Override
    public void onCleanReservation() {
    	this.append(FakeUIManager.ON_CLEAN_RESERVATION);
    }    

    @Override
    public void onLoggedOut() {
	this.append(FakeUIManager.ON_LOGGED_OUT);
    }    
    
    /*
     * Alternative scenario
     */

    @Override
    public void onWrongLoginOrPasswordGiven() {
	this.append(FakeUIManager.ON_WRONG_LOGIN_OR_PASSWORD_GIVEN);
    }       
    
    @Override
    public void onWaitingInstances(
	    WaitingInstancesReservationStatus reservationStatus) {
	this.append(FakeUIManager.ON_WAITING_INSTANCES, new Object[] {reservationStatus});
    }    

    @Override
    public void onError(String message) {
	this.append(FakeUIManager.ON_ERROR, new Object[] {message});
    }

    @Override
    public void onErrorAndFinishReservation(String message) {
	this.append(FakeUIManager.ON_ERROR_AND_FINISH_RESERVATION, new Object[] {message});
    }

    @Override
    public void onErrorAndFinishSession(String message) {
	this.append(FakeUIManager.ON_ERROR_AND_FINISH_SESSION, new Object[] {message});
    }

    @Override
    public void onMessage(String message) {
	this.append(FakeUIManager.ON_MESSAGE, new Object[] {message});
    }

	@Override
	public void onExperimentInteractionFinished() {
	}

	@Override
	public void onRemoteExperimentReserved(String url,
			String remoteReservationId) {
		// TODO Auto-generated method stub
		
	}
}
