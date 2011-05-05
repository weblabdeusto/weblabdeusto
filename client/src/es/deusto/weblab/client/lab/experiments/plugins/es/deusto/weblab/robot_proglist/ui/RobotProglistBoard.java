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
package es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.robot_proglist.ui;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.Timer;
import com.google.gwt.user.client.ui.Anchor;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;

import es.deusto.weblab.client.comm.exceptions.WlCommException;
import es.deusto.weblab.client.configuration.IConfigurationRetriever;
import es.deusto.weblab.client.dto.experiments.Command;
import es.deusto.weblab.client.dto.experiments.ResponseCommand;
import es.deusto.weblab.client.lab.comm.callbacks.IResponseCommandCallback;
import es.deusto.weblab.client.lab.ui.BoardBase;
import es.deusto.weblab.client.ui.widgets.WlPredictiveProgressBar;
import es.deusto.weblab.client.ui.widgets.WlWebcam;
import es.deusto.weblab.client.ui.widgets.WlPredictiveProgressBar.IProgressBarListener;
import es.deusto.weblab.client.ui.widgets.WlPredictiveProgressBar.IProgressBarTextUpdater;
import es.deusto.weblab.client.ui.widgets.WlPredictiveProgressBar.TextProgressBarTextUpdater;
import es.deusto.weblab.client.ui.widgets.WlTimer;
import es.deusto.weblab.client.ui.widgets.WlTimer.IWlTimerFinishedCallback;
import es.deusto.weblab.client.ui.widgets.WlWaitingLabel;

public class RobotProglistBoard extends BoardBase {

	/******************
	 * UIBINDER RELATED
	 ******************/
	
	interface RobotProglistBoardUiBinder extends UiBinder<Widget, RobotProglistBoard> {
	}

	private static final RobotProglistBoardUiBinder uiBinder = GWT.create(RobotProglistBoardUiBinder.class);
	
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
	
	@UiField(provided=true) WlWebcam webcam;
	
	public RobotProglistBoard(IConfigurationRetriever configurationRetriever, IBoardBaseController commandSender) {
		super(commandSender);
		
		this.configurationRetriever = configurationRetriever;
		
		this.createProvidedWidgets();
		
		RobotProglistBoard.uiBinder.createAndBindUi(this);
	}
	
	/**
	 * Setup certain widgets that require it after the experiment has been 
	 * started.
	 */
	private void setupWidgets() {
		this.timer.setTimerFinishedCallback(new IWlTimerFinishedCallback(){
			@Override
			public void onFinished() {
			    RobotProglistBoard.this.boardController.onClean();
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
	}
	
	private int getWebcamRefreshingTime() {
		// TODO: Replace by the code below.
		return 5;
//		return this.configurationRetriever.getIntProperty(
//			WlDeustoPicBasedBoard.PIC_WEBCAM_REFRESH_TIME_PROPERTY, 
//			WlDeustoPicBasedBoard.DEFAULT_PIC_WEBCAM_REFRESH_TIME
//			);
	}	
	

	/**
	 * The initialize function gets called on the "reserve" stage,
	 * before the experiment starts.
	 */
	@Override
	public void initialize(){
	}	
	
	
	/**
	 * This function gets called just when the actual experiment starts, after
	 * the reserve is done and the queue is over.
	 */
	@Override
	public void start() {
	    this.widget.setVisible(true);
	    
	    this.setupWidgets();
	    
	    this.setMessage("Starting robot_movement experiment...");
	    
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
				RobotProglistBoard.this.setMessage("It was not possible to obtain the configuration");
			}
			@Override
			public void onSuccess(ResponseCommand responseCommand) {
			}
		});
	}
	
}
