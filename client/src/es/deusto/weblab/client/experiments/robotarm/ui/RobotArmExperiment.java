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
* Author: Luis Rodriguez <luis.rodriguez@opendeusto.es>
* 		  
*/ 
package es.deusto.weblab.client.experiments.robotarm.ui;

import java.util.HashMap;
import java.util.Map;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.KeyCodes;
import com.google.gwt.json.client.JSONObject;
import com.google.gwt.json.client.JSONParser;
import com.google.gwt.json.client.JSONValue;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.Event;
import com.google.gwt.user.client.Event.NativePreviewEvent;
import com.google.gwt.user.client.Event.NativePreviewHandler;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.Image;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;

import es.deusto.weblab.client.comm.exceptions.CommException;
import es.deusto.weblab.client.configuration.IConfigurationRetriever;
import es.deusto.weblab.client.dto.experiments.ResponseCommand;
import es.deusto.weblab.client.lab.comm.callbacks.IResponseCommandCallback;
import es.deusto.weblab.client.lab.experiments.ExperimentBase;
import es.deusto.weblab.client.lab.experiments.IBoardBaseController;
import es.deusto.weblab.client.ui.widgets.WlTimer;
import es.deusto.weblab.client.ui.widgets.WlTimer.IWlTimerFinishedCallback;
import es.deusto.weblab.client.ui.widgets.WlWaitingLabel;
import es.deusto.weblab.client.ui.widgets.WlWebcam;

public class RobotArmExperiment extends ExperimentBase {

	// TODO: Get rid of those 4.
	private static final String RIGHT = "RIGHT";
	private static final String LEFT = "LEFT";
	private static final String DOWN = "BACK";
	private static final String UP = "FORWARD";
	
	private static final String RAIL_RIGHT = "RAIL_RIGHT";
	private static final String RAIL_LEFT = "RAIL_LEFT";
	private static final String LOWERJOINT_LEFT = "LOWERJOINT_LEFT";
	private static final String LOWERJOINT_RIGHT = "LOWERJOINT_RIGHT";
	private static final String MEDIUMJOINT_LEFT = "MEDIUMJOINT_LEFT";
	private static final String MEDIUMJOINT_RIGHT = "MEDIUMJOINT_RIGHT";
	private static final String HIGHERJOINT_LEFT = "HIGHERJOINT_LEFT";
	private static final String HIGHERJOINT_RIGHT = "HIGHERJOINT_RIGHT";
	private static final String GRIP_OPEN = "GRIP_OPEN";
	private static final String GRIP_CLOSE = "GRIP_CLOSE";


	private static final String WEBCAM_REFRESH_TIME_PROPERTY   = "webcam.refresh.millis";
	private static final int    DEFAULT_WEBCAM_REFRESH_TIME    = 200;
	
	/******************
	 * UIBINDER RELATED
	 ******************/
	
	interface RobotArmBoardUiBinder extends UiBinder<Widget, RobotArmExperiment> {
	}
	
	private static final RobotArmBoardUiBinder uiBinder = GWT.create(RobotArmBoardUiBinder.class);
	
	public static class Style   {
		public static final String TIME_REMAINING          = "wl-time_remaining";
		public static final String CLOCK_ACTIVATION_PANEL  = "wl-clock_activation_panel"; 
	}
	
	// Root panel.
	@UiField VerticalPanel widget;
	
	@UiField VerticalPanel mainWidgetsPanel;
	@UiField HorizontalPanel inputWidgetsPanel;

	@UiField(provided = true) WlTimer timer;
	
	
	@UiField WlWaitingLabel messages;
	@UiField Image upButton;
	@UiField Image downButton;
	@UiField Image rightButton;
	@UiField Image leftButton;
	
	// The following fields are for the different buttons that control the robot arm.
	@UiField Image railRight;
	@UiField Image railLeft;
	@UiField Image lowerJointRight;
	@UiField Image lowerJointLeft;
	@UiField Image mediumJointRight;
	@UiField Image mediumJointLeft;
	@UiField Image higherJointRight;
	@UiField Image higherJointLeft;
	@UiField Image gripClose;
	@UiField Image gripOpen;
	
	private boolean upPressed = false;
	private boolean downPressed = false;
	private boolean leftPressed = false;
	private boolean rightPressed = false;
	
	private final Map<String, Image> buttons;
	private int moveNumber = 0;
	private boolean buttonsEnabled = true;
	
	@UiField(provided = true) WlWebcam webcam;
	
	private class InternalNativePreviewHandler implements NativePreviewHandler {
		
		private boolean active = false;
		
		void activate() {
			this.active = true;
		}

		void deactivate() {
			this.active = false;
		}
		
		@Override
		public void onPreviewNativeEvent(NativePreviewEvent event) {
			if(!this.active)
				return;
		
			if(event.getTypeInt() == Event.ONKEYDOWN) {
				switch(event.getNativeEvent().getKeyCode()) {
					case KeyCodes.KEY_UP:
						RobotArmExperiment.this.upPressed = true;
						sendMove(UP);
						event.cancel();
						break;
					case KeyCodes.KEY_DOWN:
						RobotArmExperiment.this.downPressed = true;
						sendMove(DOWN);
						event.cancel();
						break;
					case KeyCodes.KEY_LEFT:
						RobotArmExperiment.this.leftPressed = true;
						sendMove(LEFT);
						event.cancel();
						break;
					case KeyCodes.KEY_RIGHT:
						RobotArmExperiment.this.rightPressed = true;
						sendMove(RIGHT);
						event.cancel();
						break;
				}
			} else if(event.getTypeInt() == Event.ONKEYUP) {
				switch(event.getNativeEvent().getKeyCode()) {
					case KeyCodes.KEY_UP:
						RobotArmExperiment.this.upPressed = false;
						event.cancel();
						break;
					case KeyCodes.KEY_DOWN:
						RobotArmExperiment.this.downPressed = false;
						event.cancel();
						break;
					case KeyCodes.KEY_LEFT:
						RobotArmExperiment.this.leftPressed = false;
						event.cancel();
						break;
					case KeyCodes.KEY_RIGHT:
						RobotArmExperiment.this.rightPressed = false;
						event.cancel();
						break;
				}
			}
		}
	}
	
	private final InternalNativePreviewHandler nativeEventHandler;
	
	
	public RobotArmExperiment() {
		super(null, null);
		
		
		RobotArmExperiment.uiBinder.createAndBindUi(this);
		
		
		this.buttons = new HashMap<String, Image>();
		this.buttons.put(UP,    this.upButton);
		this.buttons.put(DOWN,  this.downButton);
		this.buttons.put(LEFT,  this.leftButton);
		this.buttons.put(RIGHT, this.rightButton);
		
		this.nativeEventHandler = new InternalNativePreviewHandler();
	}
	
	public RobotArmExperiment(IConfigurationRetriever configurationRetriever, IBoardBaseController commandSender) {
		super(configurationRetriever, commandSender);
		
		this.createProvidedWidgets();
		
		RobotArmExperiment.uiBinder.createAndBindUi(this);
		
		this.buttons = new HashMap<String, Image>();
		this.buttons.put(UP,    this.upButton);
		this.buttons.put(DOWN,  this.downButton);
		this.buttons.put(LEFT,  this.leftButton);
		this.buttons.put(RIGHT, this.rightButton);
		
		this.nativeEventHandler = new InternalNativePreviewHandler();
	}
	
	/**
	 * Setup certain widgets that require it after the experiment has been 
	 * started.
	 */
	private void setupWidgets() {
		this.timer.setTimerFinishedCallback(new IWlTimerFinishedCallback(){
			@Override
			public void onFinished() {
			    RobotArmExperiment.this.boardController.clean();
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
		
		this.webcam = GWT.create(WlWebcam.class);
		this.webcam.setTime(this.getWebcamRefreshingTime());
	}
	
	private int getWebcamRefreshingTime() {
		return this.configurationRetriever.getIntProperty(
			RobotArmExperiment.WEBCAM_REFRESH_TIME_PROPERTY, 
			RobotArmExperiment.DEFAULT_WEBCAM_REFRESH_TIME
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
		Event.addNativePreviewHandler(this.nativeEventHandler);
	    this.widget.setVisible(true);
	    
	    this.setupWidgets();
	    
	    if(parseWebcamConfig(initialConfiguration))
	    	return;
	    
	    this.webcam.setVisible(true);
	    this.webcam.start();

	    this.boardController.sendCommand("program:Interactive Demo", new IResponseCommandCallback() {

			@Override
			public void onFailure(CommException e) {
				e.printStackTrace();
				RobotArmExperiment.this.messages.setText("Failed: " + e.getMessage());
				RobotArmExperiment.this.messages.stop();
			}

			@Override
			public void onSuccess(ResponseCommand responseCommand) {
				RobotArmExperiment.this.inputWidgetsPanel.setVisible(true);
				RobotArmExperiment.this.messages.setText("You can now control the bot");
				RobotArmExperiment.this.messages.stop();
				RobotArmExperiment.this.nativeEventHandler.activate();
			}
	    });
	    
	    this.setMessage("Programming interactive demo");
	    this.messages.start();
	}

	private boolean parseWebcamConfig(String initialConfiguration) {
		final JSONValue initialConfigValue   = JSONParser.parseStrict(initialConfiguration);
	    final JSONObject initialConfigObject = initialConfigValue.isObject();
	    if(initialConfigObject == null) {
	    	Window.alert("Error parsing robot configuration: not an object: " + initialConfiguration);
	    	return true;
	    }
	    
	    final JSONValue webcamValue = initialConfigObject.get("webcam");
	    if(webcamValue != null) {
	    	final String urlWebcam = webcamValue.isString().stringValue();
	    	this.webcam.setUrl(urlWebcam);
	    }
	    
	    final JSONValue mjpegValue = initialConfigObject.get("mjpeg");
	    if(mjpegValue != null) {
	    	final String mjpeg = mjpegValue.isString().stringValue();
	    	int width = 320;
	    	int height = 240;
	    	if(initialConfigObject.get("mjpegWidth") != null) {
	    		final JSONValue mjpegWidth = initialConfigObject.get("mjpegWidth");
	    		if(mjpegWidth.isNumber() != null) {
	    			width = (int)mjpegWidth.isNumber().doubleValue();
	    		} else if(mjpegWidth.isString() != null) {
	    			width = Integer.parseInt(mjpegWidth.isString().stringValue());
	    		}
	    	}
	    	if(initialConfigObject.get("mjpegHeight") != null) {
	    		final JSONValue mjpegHeight = initialConfigObject.get("mjpegHeight");
	    		if(mjpegHeight.isNumber() != null) {
	    			height = (int)mjpegHeight.isNumber().doubleValue();
	    		} else if(mjpegHeight.isString() != null) {
	    			height = Integer.parseInt(mjpegHeight.isString().stringValue());
	    		}
	    	}
	    	this.webcam.setStreamingUrl(mjpeg, width, height);
	    }
	    return false;
	}
	
	// Note about these handlers: In the similar implementation in RobotMovement, there are more kinds of handler.
	// Click handlers seem to be enough. If they aren't, TODO, add others.
	
	@SuppressWarnings("unused")
	@UiHandler("railRight")
	public void onRailRightClick(ClickEvent event){
		sendMove(RAIL_RIGHT);
	}
	
	@SuppressWarnings("unused")
	@UiHandler("railLeft")
	public void onRailLeftClick(ClickEvent event){
		sendMove(RAIL_LEFT);
	}
	
	@SuppressWarnings("unused")
	@UiHandler("lowerJointRight")
	public void onLowerJointRightClick(ClickEvent event){
		sendMove(LOWERJOINT_RIGHT);
	}
	
	@SuppressWarnings("unused")
	@UiHandler("lowerJointLeft")
	public void onLowerJointLeftClick(ClickEvent event){
		sendMove(LOWERJOINT_LEFT);
	}
	
	@SuppressWarnings("unused")
	@UiHandler("mediumJointRight")
	public void onMediumJointRightClick(ClickEvent event){
		sendMove(MEDIUMJOINT_RIGHT);
	}
	
	@SuppressWarnings("unused")
	@UiHandler("mediumJointLeft")
	public void onMediumJointLeftClick(ClickEvent event){
		sendMove(MEDIUMJOINT_LEFT);
	}
	
	@SuppressWarnings("unused")
	@UiHandler("higherJointRight")
	public void onHigherJointRightClick(ClickEvent event){
		sendMove(HIGHERJOINT_RIGHT);
	}
	
	@SuppressWarnings("unused")
	@UiHandler("higherJointLeft")
	public void onHigherJointLeftClick(ClickEvent event){
		sendMove(HIGHERJOINT_LEFT);
	}
	
	@SuppressWarnings("unused")
	@UiHandler("gripClose")
	public void onGripCloseClick(ClickEvent event){
		sendMove(GRIP_CLOSE);
	}
	
	@SuppressWarnings("unused")
	@UiHandler("gripOpen")
	public void onGripOpenClick(ClickEvent event){
		sendMove(GRIP_OPEN);
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
			public void onFailure(CommException e) {
				
			}
			
			@Override
			public void onSuccess(ResponseCommand responseCommand) {
				RobotArmExperiment.this.buttonsEnabled = true;
				if(currentMove == RobotArmExperiment.this.moveNumber){
					enableButtons();
					if(RobotArmExperiment.this.upPressed) {
						sendMove(UP);
					} else if(RobotArmExperiment.this.downPressed) {
						sendMove(DOWN);
					} else if(RobotArmExperiment.this.rightPressed) {
						sendMove(RIGHT);
					} else if(RobotArmExperiment.this.leftPressed) {
						sendMove(LEFT);
					}
				}else
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
		this.nativeEventHandler.deactivate();
		
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
