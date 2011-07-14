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
* Author: Pablo Orduña <pablo.orduna@deusto.es>
*
*/

package es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.labview.ui;

import com.google.gwt.user.client.Timer;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;

import es.deusto.weblab.client.comm.exceptions.WlCommException;
import es.deusto.weblab.client.configuration.IConfigurationRetriever;
import es.deusto.weblab.client.dto.experiments.ResponseCommand;
import es.deusto.weblab.client.lab.comm.callbacks.IResponseCommandCallback;
import es.deusto.weblab.client.lab.ui.BoardBase;
import es.deusto.weblab.client.ui.widgets.WlTimer;

public class LabVIEWBoard extends BoardBase {

	@SuppressWarnings("unused")
	private IConfigurationRetriever configurationRetriever;
	private VerticalPanel panel = new VerticalPanel();
	private HTML html = new HTML(); 
	private WlTimer timer = new WlTimer(false);

	public LabVIEWBoard(IConfigurationRetriever configurationRetriever, IBoardBaseController boardController) {
		super(boardController);
		this.configurationRetriever = configurationRetriever;
		this.timer.setStyleName("wl-time_remaining");
	}

	@Override
	public void setTime(int time) {
		this.timer.updateTime(time);
	}

	final IResponseCommandCallback callback = new IResponseCommandCallback() {
		
		@Override
		public void onFailure(WlCommException e) {
			e.printStackTrace();
			LabVIEWBoard.this.html.setText("Error checking the state of the experiment: " + e.getMessage());
		}
		
		@Override
		public void onSuccess(ResponseCommand responseCommand) {
			if(responseCommand.getCommandString().equals("yes")) {
				displayExperiment();
			} else {
				final Timer timer = new Timer() {
					
					@Override
					public void run() {
						LabVIEWBoard.this.boardController.sendCommand("is_open", LabVIEWBoard.this.callback);
					}
				};
				timer.schedule(500);
			}
		}
	};
	
	@Override
	public void start() {
		this.panel.add(this.timer);
		this.timer.start();
		this.timer.setTimerFinishedCallback(new WlTimer.IWlTimerFinishedCallback() {
			@Override
			public void onFinished() {
				LabVIEWBoard.this.boardController.onClean();
			}
		});
		this.panel.add(this.html);
		this.html.setText("Waiting for experiment...");
		this.boardController.sendCommand("is_open", this.callback);
	}

	private void displayExperiment() {
		this.boardController.sendCommand("get_url", new IResponseCommandCallback() {
			
			@Override
			public void onFailure(WlCommException e) {
				e.printStackTrace();
				LabVIEWBoard.this.html.setText("Error getting url to show LabVIEW panel: " + e.getMessage());
			}
			
			@Override
			public void onSuccess(ResponseCommand responseCommand) {
				final String [] commands = responseCommand.getCommandString().split(";");
				if(commands.length < 5){
					LabVIEWBoard.this.html.setHTML("Invalid response: not enough arguments: " + responseCommand.getCommandString());
					return;
				}
				
				final int height         = Integer.parseInt(commands[0]);
				final int width          = Integer.parseInt(commands[1]);
				final String viName      = commands[2];
				final String server      = commands[3];
				final String version     = commands[4];
				
				final String htmlCode = LabViewObjectGenerator.generate(height, width, viName, server, version);
				LabVIEWBoard.this.html.setHTML(htmlCode);
			}
		});
	}

	@Override
	public void end() {
		if(this.timer != null)
			this.timer.dispose();
		if(this.html != null)
			this.html.setHTML("");
	}

	@Override
	public Widget getWidget() {
		return this.panel;
	}

}
