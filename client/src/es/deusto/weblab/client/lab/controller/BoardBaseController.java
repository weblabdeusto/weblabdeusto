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
* Author: Pablo Orduña <pablo.orduna@deusto.es>
*
*/

package es.deusto.weblab.client.lab.controller;

import es.deusto.weblab.client.comm.exceptions.CommException;
import es.deusto.weblab.client.dto.SessionID;
import es.deusto.weblab.client.dto.experiments.Command;
import es.deusto.weblab.client.dto.experiments.ResponseCommand;
import es.deusto.weblab.client.lab.comm.UploadStructure;
import es.deusto.weblab.client.lab.comm.callbacks.IResponseCommandCallback;
import es.deusto.weblab.client.lab.experiments.IBoardBaseController;

final class BoardBaseController implements IBoardBaseController {
	
	private final LabController controller;
	
	BoardBaseController(LabController controller) {
		this.controller = controller;
	}
	
	@Override
	public void disableFinishOnClose() {
		this.controller.disableFinishOnClose();
	}
	
	@Override
	public boolean isFacebook(){
		return this.controller.isFacebook();
	}
	
	@Override
	public SessionID getSessionId(){
		return this.controller.getCurrentSession();		
	}
	
	@Override
	public void clean(){
		this.controller.cleanExperiment();
		this.controller.removeReservationId();
	}
	
	@Override
	public void finish(){
		this.controller.finishReservation();
	}
	
	// Ignore the callback
	@Override
	public void sendCommand(Command command){
	    this.controller.sendCommand(command, new IResponseCommandCallback(){
		@Override
		public void onSuccess(
			ResponseCommand responseCommand) {
		    // nothing
		}

		@Override
		public void onFailure(CommException e) {
		    BoardBaseController.this.controller.getUIManager().onError("Error sending command: " + e.getMessage());
		}
	    });
	}
	
	@Override
	public void sendCommand(final String command){
		sendCommand(new Command() {
			@Override
			public String getCommandString() {
				return command;
			}
		});
	}
	
	@Override
	public void sendCommand(final String command, IResponseCommandCallback callback){
		sendCommand(new Command() {
			@Override
			public String getCommandString() {
				return command;
			}
		}, callback);
	}
	
	@Override
	public void sendCommand(Command command, IResponseCommandCallback callback) {
	    this.controller.sendCommand(command, callback);
	}
	
	@Override
	public void sendFile(UploadStructure uploadStructure, IResponseCommandCallback callback) {
	    this.controller.sendFile(uploadStructure, callback);
	}
	
	@Override
	public void sendAsyncFile(UploadStructure uploadStructure, IResponseCommandCallback callback) {
		this.controller.sendAsyncFile(uploadStructure, callback);
	}
	
	@Override
	public void sendAsyncCommand(Command command) {
	    this.controller.sendAsyncCommand(command, new IResponseCommandCallback(){
    		@Override
			public void onSuccess(
    			ResponseCommand responseCommand) {
    		    // nothing
    		}

    		@Override
			public void onFailure(CommException e) {
    		    BoardBaseController.this.controller.getUIManager().onError("Error sending async command: " + e.getMessage());
    		}
	    });
	}
	
	@Override
	public void sendAsyncCommand(Command command,
			IResponseCommandCallback callback) {
		this.controller.sendAsyncCommand(command, callback);
	}
	
	@Override
	public void sendAsyncCommand(final String command) {
		sendAsyncCommand(new Command() {
			@Override
			public String getCommandString() {
				return command;
			}
		});
	}
	
	@Override
	public void sendAsyncCommand(final String command,
			IResponseCommandCallback callback) {
		sendCommand(new Command() {
			@Override
			public String getCommandString() {
				return command;
			}
		}, callback);
	}

	@Override
	public void stopPolling() {
		this.controller.stopPolling();
	}
}