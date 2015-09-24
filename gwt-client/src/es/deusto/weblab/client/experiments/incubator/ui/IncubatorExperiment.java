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
* Author: Pablo Orduña <pablo.orduna@deusto.es>
*
*/

package es.deusto.weblab.client.experiments.incubator.ui;

import com.google.gwt.json.client.JSONObject;
import com.google.gwt.json.client.JSONParser;
import com.google.gwt.user.client.Timer;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.Label;

import es.deusto.weblab.client.comm.exceptions.CommException;
import es.deusto.weblab.client.configuration.IConfigurationRetriever;
import es.deusto.weblab.client.dto.experiments.ResponseCommand;
import es.deusto.weblab.client.lab.comm.callbacks.IResponseCommandCallback;
import es.deusto.weblab.client.lab.experiments.IBoardBaseController;
import es.deusto.weblab.client.lab.experiments.UIExperimentBase;
import es.deusto.weblab.client.ui.widgets.IWlDisposableWidget;

public class IncubatorExperiment extends UIExperimentBase {

	private MainIncubatorPanel incubatorPanel = null;
	
	public IncubatorExperiment(IConfigurationRetriever configurationRetriever, IBoardBaseController boardController) {
		super(configurationRetriever, boardController);
		
		final String htmlCode = configurationRetriever.getProperty("html", "");
		putWidget(new HTML(htmlCode));
	}

	@Override
	public void start(int time, String initialConfiguration) {
		final JSONObject obj = JSONParser.parseStrict(initialConfiguration).isObject();
		
		final JSONObject jsonStatus = obj.get("status").isObject();
		
		final Status initialStatus = new Status(jsonStatus);
		
		this.incubatorPanel = new MainIncubatorPanel(this, initialStatus, obj, time);
		putWidget(this.incubatorPanel);
		
		for(IWlDisposableWidget disposableWidget : this.incubatorPanel.getDisposableWidgets())
			addDisposableWidgets(disposableWidget);
		
		this.timer.scheduleRepeating(5000);
	}
	
	@Override 
	public void end() {
		super.end();
		this.timer.cancel();
		this.incubatorPanel = null;
	}
	
	void turnLight(String pos, boolean value) {
		final String command = "turn:" + pos + ":" + (value?"on":"off");
		System.out.println(command);
		this.boardController.sendCommand(command, this.commandCallback);
	}

	void turnAllLights(boolean value) {
		final String command = "turn:all:" + (value?"on":"off");
		System.out.println(command);
		this.boardController.sendCommand(command, this.commandCallback);
	}
	
	void updateStatus(Status status) {
		if(this.incubatorPanel != null)
			this.incubatorPanel.update(status);
	}
	
	void showError(String message) {
		if(this.incubatorPanel == null)
			putWidget(new Label("Error: " + message));
		else 
			this.incubatorPanel.showError(message);
	}
	
	/*
	 * Auxiliar classes:
	 *  - Timer
	 *  - IResponseCallback
	 *  
	 */
	
	private final Timer timer = new Timer() {
		@Override
		public void run() {
			IncubatorExperiment.this.boardController.sendCommand("get_status", new IResponseCommandCallback() {
				
				@Override
				public void onFailure(CommException e) { }
				
				@Override
				public void onSuccess(ResponseCommand responseCommand) {
					try {
						final JSONObject statusJson = JSONParser.parseStrict(responseCommand.getCommandString()).isObject();
						final Status currentStatus = new Status(statusJson);
						updateStatus(currentStatus);
					} catch (Exception e) {
						System.out.println("Response: " + responseCommand + " failed.");
						e.printStackTrace();
					}
				}
			});
		}
	};

	
	private final IResponseCommandCallback commandCallback = new IResponseCommandCallback() {
		
		@Override
		public void onFailure(CommException e) {
			showError(e.getMessage());
		}
		
		@Override
		public void onSuccess(ResponseCommand responseCommand) {
			final String commandString = responseCommand.getCommandString();
			System.out.println("Got: " + commandString);
			if(commandString.startsWith("error:")) {
				showError(commandString.substring("error:".length()));
			} else {
				final Status status;
				try{
					status = new Status(JSONParser.parseStrict(commandString).isObject());
				} catch (Exception e) {
					e.printStackTrace();
					return;
				}
				updateStatus(status);
			}
		}
	};

	public void getHistoricData(String formattedDate, IResponseCommandCallback callback) {
		this.boardController.sendCommand("get_historic:" + formattedDate, callback);
	}
}
