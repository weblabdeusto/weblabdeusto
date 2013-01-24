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
package es.deusto.weblab.client.experiments.robot_movement.ui;

import java.util.HashMap;
import java.util.Map;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.KeyCodes;
import com.google.gwt.event.dom.client.MouseDownEvent;
import com.google.gwt.event.dom.client.MouseUpEvent;
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
						RobotMovementExperiment.this.upPressed = true;
						sendMove(UP);
						event.cancel();
						break;
					case KeyCodes.KEY_DOWN:
						RobotMovementExperiment.this.downPressed = true;
						sendMove(DOWN);
						event.cancel();
						break;
					case KeyCodes.KEY_LEFT:
						RobotMovementExperiment.this.leftPressed = true;
						sendMove(LEFT);
						event.cancel();
						break;
					case KeyCodes.KEY_RIGHT:
						RobotMovementExperiment.this.rightPressed = true;
						sendMove(RIGHT);
						event.cancel();
						break;
				}
			} else if(event.getTypeInt() == Event.ONKEYUP) {
				switch(event.getNativeEvent().getKeyCode()) {
					case KeyCodes.KEY_UP:
						RobotMovementExperiment.this.upPressed = false;
						event.cancel();
						break;
					case KeyCodes.KEY_DOWN:
						RobotMovementExperiment.this.downPressed = false;
						event.cancel();
						break;
					case KeyCodes.KEY_LEFT:
						RobotMovementExperiment.this.leftPressed = false;
						event.cancel();
						break;
					case KeyCodes.KEY_RIGHT:
						RobotMovementExperiment.this.rightPressed = false;
						event.cancel();
						break;
				}
			}
		}
	}
	
	private final InternalNativePreviewHandler nativeEventHandler;
	
	public RobotMovementExperiment(IConfigurationRetriever configurationRetriever, IBoardBaseController commandSender) {
		super(configurationRetriever, commandSender);
		
		this.createProvidedWidgets();
		
		RobotMovementExperiment.uiBinder.createAndBindUi(this);
		
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
			    RobotMovementExperiment.this.boardController.clean();
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
				RobotMovementExperiment.this.messages.setText(i18n.failed(e.getMessage()));
				RobotMovementExperiment.this.messages.stop();
			}

			@Override
			public void onSuccess(ResponseCommand responseCommand) {
				if(responseCommand.getCommandString().startsWith("File send")) {
					RobotMovementExperiment.this.inputWidgetsPanel.setVisible(true);
					RobotMovementExperiment.this.messages.setText(i18n.youCanControlTheBot());
					RobotMovementExperiment.this.messages.stop();
					RobotMovementExperiment.this.nativeEventHandler.activate();
				} else {
					RobotMovementExperiment.this.messages.setText("Failed. This could mean that the microcontroller is old. You can contact the administrator, but first try again just in case. Reason: " + responseCommand.getCommandString());
					RobotMovementExperiment.this.messages.stop();
				}
			}
	    });
	    
	    this.setMessage(i18n.programmingInteractiveDemo());
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
	
	@SuppressWarnings("unused")
	@UiHandler("upButton")
	public void onUpMouseDown(MouseDownEvent event) {
		sendMove(UP);
		this.upPressed = true;
	}

	
	@SuppressWarnings("unused")
	@UiHandler("downButton")
	public void onDownMouseDown(MouseDownEvent event) {
		sendMove(DOWN);
		this.downPressed = true;
	}

	
	@SuppressWarnings("unused")
	@UiHandler("leftButton")
	public void onLeftMouseDown(MouseDownEvent event) {
		sendMove(LEFT);
		this.leftPressed = true;
	}

	
	@SuppressWarnings("unused")
	@UiHandler("rightButton")
	public void onRightMouseDown(MouseDownEvent event) {
		sendMove(RIGHT);
		this.rightPressed = true;
	}

	@SuppressWarnings("unused")
	@UiHandler("upButton")
	public void onUpMouseUp(MouseUpEvent event) {
		this.upPressed = false;
	}

	
	@SuppressWarnings("unused")
	@UiHandler("downButton")
	public void onDownMouseUp(MouseUpEvent event) {
		this.downPressed = false;
	}

	
	@SuppressWarnings("unused")
	@UiHandler("leftButton")
	public void onLeftMouseUp(MouseUpEvent event) {
		this.leftPressed = false;
	}

	
	@SuppressWarnings("unused")
	@UiHandler("rightButton")
	public void onRightMouseUp(MouseUpEvent event) {
		this.rightPressed = false;
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
				RobotMovementExperiment.this.buttonsEnabled = true;
				if(currentMove == RobotMovementExperiment.this.moveNumber){
					enableButtons();
					if(RobotMovementExperiment.this.upPressed) {
						sendMove(UP);
					} else if(RobotMovementExperiment.this.downPressed) {
						sendMove(DOWN);
					} else if(RobotMovementExperiment.this.rightPressed) {
						sendMove(RIGHT);
					} else if(RobotMovementExperiment.this.leftPressed) {
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
