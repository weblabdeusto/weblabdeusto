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
* Author: Luis Rodriguez <luis.rodriguez@opendeusto.es>
* 		  
*/ 
package es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.robot_standard.ui;

import com.google.gwt.core.client.GWT;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;

import es.deusto.weblab.client.comm.exceptions.WlCommException;
import es.deusto.weblab.client.configuration.IConfigurationRetriever;
import es.deusto.weblab.client.dto.experiments.Command;
import es.deusto.weblab.client.dto.experiments.ResponseCommand;
import es.deusto.weblab.client.lab.comm.UploadStructure;
import es.deusto.weblab.client.lab.comm.callbacks.IResponseCommandCallback;
import es.deusto.weblab.client.lab.experiments.commands.RequestWebcamCommand;
import es.deusto.weblab.client.lab.ui.BoardBase;
import es.deusto.weblab.client.ui.widgets.WlTimer;
import es.deusto.weblab.client.ui.widgets.WlWaitingLabel;
import es.deusto.weblab.client.ui.widgets.WlWebcam;
import es.deusto.weblab.client.ui.widgets.WlTimer.IWlTimerFinishedCallback;

public class RobotStandardBoard extends BoardBase {
	
	private static final String WEBCAM_REFRESH_TIME_PROPERTY   = "webcam.refresh.millis";
	private static final int    DEFAULT_WEBCAM_REFRESH_TIME    = 200;

	/******************
	 * UIBINDER RELATED
	 ******************/
	
	interface RobotStandardBoardUiBinder extends UiBinder<Widget, RobotStandardBoard> {
	}

	private static final RobotStandardBoardUiBinder uiBinder = GWT.create(RobotStandardBoardUiBinder.class);
	
	public static class Style   {
		public static final String TIME_REMAINING          = "wl-time_remaining";
		public static final String CLOCK_ACTIVATION_PANEL  = "wl-clock_activation_panel"; 
	}

	private final IConfigurationRetriever configurationRetriever;
	
	@UiField(provided=true) WlTimer timer;
	
	// Root panel.
	@UiField VerticalPanel widget;
	
	@UiField VerticalPanel mainWidgetsPanel;
	
	@UiField WlWaitingLabel messages;
	
	@UiField VerticalPanel uploadStructurePanel;
	
	@UiField(provided=true) WlWebcam webcam;
	
	private UploadStructure uploadStructure;
	
	public RobotStandardBoard(IConfigurationRetriever configurationRetriever, IBoardBaseController commandSender) {
		super(commandSender);
		
		this.configurationRetriever = configurationRetriever;
		
		this.createProvidedWidgets();
		
		RobotStandardBoard.uiBinder.createAndBindUi(this);
	}
	
	/**
	 * Setup certain widgets that require it after the experiment has been 
	 * started.
	 */
	private void setupWidgets() {
		this.timer.setTimerFinishedCallback(new IWlTimerFinishedCallback(){
			@Override
			public void onFinished() {
			    RobotStandardBoard.this.boardController.onClean();
			}
		});
		this.timer.start();
	}
	
	
	/* Creates those widgets that are placed through UiBinder but
	 * whose ctors need to take certain parameters and hence be
	 * instanced in code.
	 */
	private void createProvidedWidgets() {
		this.timer = new WlTimer(false);	
		
		// TODO: Add a default url to the webcam.
		this.webcam = new WlWebcam(this.getWebcamRefreshingTime());
		
		this.uploadStructure = new UploadStructure();
		this.uploadStructure.setFileInfo("program");
	}
	
	private int getWebcamRefreshingTime() {
		return this.configurationRetriever.getIntProperty(
			RobotStandardBoard.WEBCAM_REFRESH_TIME_PROPERTY, 
			RobotStandardBoard.DEFAULT_WEBCAM_REFRESH_TIME
		);
	}	
	

	/**
	 * The initialize function gets called on the "reserve" stage,
	 * before the experiment starts.
	 */
	@Override
	public void initialize(){
		this.uploadStructurePanel.add(this.uploadStructure.getFormPanel());
	}	
	
	
	/**
	 * This function gets called just when the actual experiment starts, after
	 * the reserve is done and the queue is over.
	 */
	@Override
	public void start() {
	    this.widget.setVisible(true);
	    
	    this.setupWidgets();
	    
	    RequestWebcamCommand.createAndSend(this.boardController, this.webcam, this.messages);
	    this.webcam.setVisible(true);
	    this.webcam.start();

	    this.uploadStructure.getFormPanel().setVisible(false);
		
		this.boardController.sendFile(this.uploadStructure, new IResponseCommandCallback() {
			
			@Override
			public void onFailure(WlCommException e) {
				RobotStandardBoard.this.uploadStructurePanel.setVisible(false);
				RobotStandardBoard.this.messages.stop();
				setMessage("Failed: " + e.getMessage());
			}
			
			@Override
			public void onSuccess(ResponseCommand responseCommand) {
				RobotStandardBoard.this.uploadStructurePanel.setVisible(false);
				RobotStandardBoard.this.messages.stop();
				if(responseCommand.getCommandString().toLowerCase().trim().equals("ok")){
					setMessage("The program is being executed in the bot");
				}else{
					setMessage("There was an error: <" + responseCommand.getCommandString() + ">");
				}
			}
		});
	    
	    this.setMessage("Sending program");
	    this.messages.start();
	    
	    this.sendGetConfigurationCommand();
	}	
	
	@Override
	public void setTime(int time) {
		this.timer.updateTime(time);
	}

	@Override
	public Widget getWidget() {
		return this.widget;
	}

	@Override
	public void end() {
		if(this.timer != null){
			this.timer.dispose();
			this.timer = null;
		}			
	}
	
	public void setMessage(String msg) {
		this.messages.setText(msg);
	}
	
	private void sendGetConfigurationCommand(){
		final Command command = new Command() {
			@Override
			public String getCommandString() {
				return "get_configuration";
			}
		};
		
		this.boardController.sendCommand(command, new IResponseCommandCallback() {
			@Override
			public void onFailure(WlCommException e) {
				RobotStandardBoard.this.setMessage("It was not possible to obtain the configuration");
			}
			@Override
			public void onSuccess(ResponseCommand responseCommand) {
			}
		});
	}
	
}
