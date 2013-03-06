/*
* Copyright (C) 2012 onwards University of Deusto
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

package es.deusto.weblab.client.experiments.aquarium.ui;

import com.google.gwt.user.client.Timer;

import es.deusto.weblab.client.comm.exceptions.CommException;
import es.deusto.weblab.client.dto.experiments.ResponseCommand;
import es.deusto.weblab.client.lab.comm.callbacks.IResponseCommandCallback;
import es.deusto.weblab.client.lab.experiments.IBoardBaseController;
import es.deusto.weblab.client.ui.widgets.IWlDisposableWidget;

class StatusUpdater implements IWlDisposableWidget {

	private final Timer timer;
	
	StatusUpdater(int frequency, final IBoardBaseController controller, final AquariumExperiment experiment) {
		this.timer = new Timer() {

			@Override
			public void run() {
				controller.sendCommand("get-status", new IResponseCommandCallback() {
					
					@Override
					public void onFailure(CommException e) {
						experiment.setMessage("Error retrieving status: " + e.getMessage());
						e.printStackTrace();
					}
					
					@Override
					public void onSuccess(ResponseCommand responseCommand) {
						final Status status = new Status(responseCommand.getCommandString());
						experiment.updateStatus(status);
					}
				});
			}
		};
		this.timer.scheduleRepeating(frequency);
	}
	
	@Override
	public void dispose() {
		this.timer.cancel();
	}
}
