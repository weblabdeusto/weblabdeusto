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
package es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.robot_movement.ui;

import java.util.HashMap;
import java.util.Map;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.Image;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;

import es.deusto.weblab.client.comm.exceptions.WlCommException;
import es.deusto.weblab.client.configuration.IConfigurationRetriever;
import es.deusto.weblab.client.dto.experiments.ResponseCommand;
import es.deusto.weblab.client.lab.comm.callbacks.IResponseCommandCallback;
import es.deusto.weblab.client.lab.experiments.ExperimentBase;
import es.deusto.weblab.client.lab.experiments.commands.RequestWebcamCommand;
import es.deusto.weblab.client.ui.widgets.WlTimer;
import es.deusto.weblab.client.ui.widgets.WlTimer.IWlTimerFinishedCallback;
import es.deusto.weblab.client.ui.widgets.WlWaitingLabel;
import es.deusto.weblab.client.ui.widgets.WlWebcam;

public class RobotMovementExperiment extends ExperimentBase {

	private static final String RIGHT = "RIGHT";

	private static final String LEFT = "LEFT";

	private static final String DOWN = "BACK";

	private static final String UP = "FORWARD";


	private static final String WEBCAM_REFRESH_TIME_PROPERTY   = "webcam.refresh.millis";
	private static final int    DEFAULT_WEBCAM_REFRESH_TIME    = 200;
	
	/******************
	 * UIBINDER RELATED
	 ******************/
	
	interface RobotMovementBoardUiBinder extends UiBinder<Widget, RobotMovementExperiment> {
	}
	
	private static final RobotMovementBoardUiBinder uiBinder = GWT.create(RobotMovementBoardUiBinder.class);
	
	public static class Style   {
		public static final String TIME_REMAINING          = "wl-time_remaining";
		public static final String CLOCK_ACTIVATION_PANEL  = "wl-clock_activation_panel"; 
	}

	private final IConfigurationRetriever configurationRetriever;
	
	@UiField(provided = true) WlTimer timer;
	
	// Root panel.
	@UiField VerticalPanel widget;
	
	@UiField VerticalPanel mainWidgetsPanel;
	@UiField HorizontalPanel inputWidgetsPanel;
	
	@UiField WlWaitingLabel messages;
	@UiField Image upButton;
	@UiField Image downButton;
	@UiField Image rightButton;
	@UiField Image leftButton;
	
	private final Map<String, Image> buttons;
	private int moveNumber = 0;
	private boolean buttonsEnabled = true;
	
	@UiField(provided = true) WlWebcam webcam;
	
	public RobotMovementExperiment(IConfigurationRetriever configurationRetriever, IBoardBaseController commandSender) {
		super(commandSender);
		
		this.configurationRetriever = configurationRetriever;
		
		this.createProvidedWidgets();
		
		RobotMovementExperiment.uiBinder.createAndBindUi(this);
		
		this.buttons = new HashMap<String, Image>();
		this.buttons.put(UP, this.upButton);
		this.buttons.put(DOWN, this.downButton);
		this.buttons.put(LEFT, this.leftButton);
		this.buttons.put(RIGHT, this.rightButton);
	}
	
	/**
	 * Setup certain widgets that require it after the experiment has been 
	 * started.
	 */
	private void setupWidgets() {
		this.timer.setTimerFinishedCallback(new IWlTimerFinishedCallback(){
			@Override
			public void onFinished() {
			    RobotMovementExperiment.this.boardController.onClean();
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
		return this.configurationRetriever.getIntProperty(
			RobotMovementExperiment.WEBCAM_REFRESH_TIME_PROPERTY, 
			RobotMovementExperiment.DEFAULT_WEBCAM_REFRESH_TIME
		);
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
	public void start(int time, String initialConfiguration) {
	    this.widget.setVisible(true);
	    
	    this.setupWidgets();
	    
	    RequestWebcamCommand.createAndSend(this.boardController, this.webcam, this.messages);
	    this.webcam.setVisible(true);
	    this.webcam.start();

	    this.boardController.sendCommand("program:Interactive Demo", new IResponseCommandCallback() {

			@Override
			public void onFailure(WlCommException e) {
				e.printStackTrace();
				RobotMovementExperiment.this.messages.setText("Failed: " + e.getMessage());
				RobotMovementExperiment.this.messages.stop();
			}

			@Override
			public void onSuccess(ResponseCommand responseCommand) {
				RobotMovementExperiment.this.inputWidgetsPanel.setVisible(true);
				RobotMovementExperiment.this.messages.setText("You can now control the bot");
				RobotMovementExperiment.this.messages.stop();
			}
	    });
	    
	    this.setMessage("Programming interactive demo");
	    this.messages.start();
	}
	
	@SuppressWarnings("unused")
	@UiHandler("upButton")
	public void onUpClick(ClickEvent event){
		sendMove(UP);
	}
	
	@SuppressWarnings("unused")
	@UiHandler("downButton")
	public void onDownClick(ClickEvent event){
		sendMove(DOWN);
	}
	
	@SuppressWarnings("unused")
	@UiHandler("leftButton")
	public void onLeftClick(ClickEvent event){
		sendMove(LEFT);
	}
	
	@SuppressWarnings("unused")
	@UiHandler("rightButton")
	public void onRightClick(ClickEvent event){
		sendMove(RIGHT);
	}
	
	private void enableButton(String button){
		this.buttons.get(button).setStyleName("wl-img-button");
	}
	
	private void disableButton(String button){
		this.buttons.get(button).setStyleName("wl-disabled-img-button");
	}
	
	private void enableButtons(){
		for(Image img : this.buttons.values())
			img.setStyleName("wl-img-button");
	}
	
	private void disableButtons(){
		for(Image img : this.buttons.values())
			img.setStyleName("wl-disabled-img-button");
	}

	private void sendMove(final String s){
		if(!this.buttonsEnabled)
			return;
		
		disableButtons();
		enableButton(s);
		this.buttonsEnabled = false;
		final int currentMove = ++this.moveNumber;
		
		this.boardController.sendCommand("move:" + s, new IResponseCommandCallback() {
			
			@Override
			public void onFailure(WlCommException e) {
				
			}
			
			@Override
			public void onSuccess(ResponseCommand responseCommand) {
				RobotMovementExperiment.this.buttonsEnabled = true;
				if(currentMove == RobotMovementExperiment.this.moveNumber)
					enableButtons();
				else
					disableButton(s);
			}
		});
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
		if(this.messages != null){
			this.messages.stop();
		}
		if(this.webcam != null){
			this.webcam.dispose();
		}
	}
	
	public void setMessage(String msg) {
		this.messages.setText(msg);
	}	
}
