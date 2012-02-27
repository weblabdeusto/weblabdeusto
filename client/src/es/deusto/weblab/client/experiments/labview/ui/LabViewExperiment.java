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

package es.deusto.weblab.client.experiments.labview.ui;

import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.user.client.Timer;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;

import es.deusto.weblab.client.WebLabClient;
import es.deusto.weblab.client.comm.exceptions.CommException;
import es.deusto.weblab.client.configuration.IConfigurationRetriever;
import es.deusto.weblab.client.dto.experiments.ResponseCommand;
import es.deusto.weblab.client.lab.comm.UploadStructure;
import es.deusto.weblab.client.lab.comm.callbacks.IResponseCommandCallback;
import es.deusto.weblab.client.lab.experiments.ExperimentBase;
import es.deusto.weblab.client.lab.experiments.IBoardBaseController;
import es.deusto.weblab.client.ui.widgets.WlTimer;

public class LabViewExperiment extends ExperimentBase {

	private VerticalPanel panel = new VerticalPanel();
	private HTML html = new HTML(); 
	private Button openPopupButton = new Button("Click here to open the experiment");
	private WlTimer timer = new WlTimer(false);
	private final boolean sendFile;
	
	private HorizontalPanel uploadStructurePanel = new HorizontalPanel();
	private UploadStructure uploadStructure;

	public LabViewExperiment(IConfigurationRetriever configurationRetriever, IBoardBaseController boardController) {
		super(configurationRetriever, boardController);
		this.timer.setStyleName("wl-time_remaining");
		this.openPopupButton.setVisible(false);
		this.sendFile = this.configurationRetriever.getBoolProperty("send.file", false);
		this.uploadStructure = new UploadStructure();
		this.uploadStructure.setFileInfo("program");
	}

	@Override
	public void setTime(int time) {
		this.timer.updateTime(time);
	}

	private final IResponseCommandCallback isOpenCallback = new IResponseCommandCallback() {
		
		@Override
		public void onFailure(CommException e) {
			e.printStackTrace();
			LabViewExperiment.this.html.setText("Error checking the state of the experiment: " + e.getMessage());
		}
		
		@Override
		public void onSuccess(ResponseCommand responseCommand) {
			if(responseCommand.getCommandString().equals("yes")) {
				displayExperiment();
			} else {
				final Timer timer = new Timer() {
					
					@Override
					public void run() {
						LabViewExperiment.this.boardController.sendCommand("is_open", LabViewExperiment.this.isOpenCallback);
					}
				};
				timer.schedule(500);
			}
		}
	};
	
	private final IResponseCommandCallback isProgrammedCallback = new IResponseCommandCallback() {
		
		@Override
		public void onFailure(CommException e) {
			e.printStackTrace();
			LabViewExperiment.this.html.setText("Error checking the state of the experiment: " + e.getMessage());
		}
		
		@Override
		public void onSuccess(ResponseCommand responseCommand) {
			if(responseCommand.getCommandString().equals("yes")) {
				displayExperiment();
			} else {
				final Timer timer = new Timer() {
					
					@Override
					public void run() {
						LabViewExperiment.this.boardController.sendCommand("is_programmed", LabViewExperiment.this.isProgrammedCallback);
					}
				};
				timer.schedule(500);
			}
		}
	};
	
	private final IResponseCommandCallback readyToProgramFileCallback = new IResponseCommandCallback() {

		@Override
		public void onFailure(CommException e) {
			LabViewExperiment.this.html.setText("Error checking if it's ready to program a file: " + e.getMessage());
		}

		@Override
		public void onSuccess(ResponseCommand responseCommand) {
			if(responseCommand.getCommandString().equals("yes")){
				LabViewExperiment.this.uploadStructure.getFormPanel().setVisible(false);
				LabViewExperiment.this.boardController.sendFile(LabViewExperiment.this.uploadStructure, LabViewExperiment.this.sendFileCallback);
			}else if(responseCommand.getCommandString().equals("no")){
				final Timer timer = new Timer() {
					
					@Override
					public void run() {
						LabViewExperiment.this.boardController.sendCommand("is_ready_to_program", LabViewExperiment.this.readyToProgramFileCallback);
					}
				};
				timer.schedule(500);
			}else{
				LabViewExperiment.this.html.setText("Error checking if it's ready to program a file: got " + responseCommand.getCommandString());
			}
		}
		
	};
	
	private final IResponseCommandCallback sendFileCallback = new IResponseCommandCallback() {
		
		@Override
		public void onFailure(CommException e) {
			e.printStackTrace();
			LabViewExperiment.this.html.setText("Error sending file: " + e.getMessage());
		}
		
		@Override
		public void onSuccess(ResponseCommand responseCommand) {
			LabViewExperiment.this.boardController.sendCommand("is_programmed", LabViewExperiment.this.isProgrammedCallback);
		}
	};
	
	@Override
	public void initialize() {
		if(this.sendFile){
			this.panel.add(this.uploadStructurePanel);
			this.uploadStructurePanel.add(new Label("Select the bit file"));
			this.uploadStructurePanel.add(this.uploadStructure.getFormPanel());
		}
	}
	
	@Override
	public void start(int time, String initialConfiguration) {
		this.uploadStructure.getFormPanel().setVisible(false);
		this.panel.add(this.timer);
		this.timer.start();
		this.timer.setTimerFinishedCallback(new WlTimer.IWlTimerFinishedCallback() {
			@Override
			public void onFinished() {
				LabViewExperiment.this.boardController.clean();
			}
		});
		this.panel.add(this.html);
		this.panel.add(this.openPopupButton);
		this.html.setText("Waiting for experiment...");
		
		if(this.sendFile){
			this.boardController.sendCommand("is_ready_to_program", this.readyToProgramFileCallback);
		}else{
			this.boardController.sendCommand("is_open", this.isOpenCallback);
		}
	}
	
	

	private void displayExperiment() {
		this.boardController.sendCommand("get_url", new IResponseCommandCallback() {
			
			@Override
			public void onFailure(CommException e) {
				e.printStackTrace();
				LabViewExperiment.this.html.setText("Error getting url to show LabVIEW panel: " + e.getMessage());
			}
			
			@Override
			public void onSuccess(ResponseCommand responseCommand) {
				LabViewExperiment.this.html.setText("");
				LabViewExperiment.this.openPopupButton.setVisible(true);
				LabViewExperiment.this.openPopupButton.addClickHandler(new ClickHandler() {
					@Override
					public void onClick(ClickEvent event) {
						Window.open(WebLabClient.baseLocation + "/weblab/web/labview/?session_id=" + LabViewExperiment.this.boardController.getSessionId().getRealId(), "_blank", "resizable=yes,scrollbars=yes,dependent=yes,width=1000,height=800,top=0");
					}
				});
				/*
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
				*/
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
