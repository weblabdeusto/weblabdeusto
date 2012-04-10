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
package es.deusto.weblab.client.experiments.submarine.ui;

import java.util.HashMap;
import java.util.Map;

import com.google.gwt.core.client.GWT;
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

public class SubmarineExperiment extends ExperimentBase {

	private static final String RIGHT_ON  = "RIGHT ON";
	private static final String RIGHT_OFF = "RIGHT OFF";

	private static final String LEFT_ON  = "LEFT ON";
	private static final String LEFT_OFF = "LEFT OFF";

	private static final String BACKWARD_ON  = "BACKWARD ON";
	private static final String BACKWARD_OFF = "BACKWARD OFF";

	private static final String FORWARD_ON  = "FORWARD ON";
	private static final String FORWARD_OFF = "FORWARD OFF";


	private static final String WEBCAM_REFRESH_TIME_PROPERTY   = "webcam.refresh.millis";
	private static final int    DEFAULT_WEBCAM_REFRESH_TIME    = 200;
	
	/******************
	 * UIBINDER RELATED
	 ******************/
	
	interface SubmarineBoardUiBinder extends UiBinder<Widget, SubmarineExperiment> {
	}
	
	private static final SubmarineBoardUiBinder uiBinder = GWT.create(SubmarineBoardUiBinder.class);
	
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
						SubmarineExperiment.this.upPressed = true;
						sendMove(FORWARD_ON);
						break;
					case KeyCodes.KEY_DOWN:
						SubmarineExperiment.this.downPressed = true;
						sendMove(BACKWARD_ON);
						break;
					case KeyCodes.KEY_LEFT:
						SubmarineExperiment.this.leftPressed = true;
						sendMove(LEFT_ON);
						break;
					case KeyCodes.KEY_RIGHT:
						SubmarineExperiment.this.rightPressed = true;
						sendMove(RIGHT_ON);
						break;
				}
			} else if(event.getTypeInt() == Event.ONKEYUP) {
				switch(event.getNativeEvent().getKeyCode()) {
					case KeyCodes.KEY_UP:
						SubmarineExperiment.this.upPressed = false;
						sendMove(FORWARD_OFF);
						break;
					case KeyCodes.KEY_DOWN:
						SubmarineExperiment.this.downPressed = false;
						sendMove(BACKWARD_OFF);
						break;
					case KeyCodes.KEY_LEFT:
						SubmarineExperiment.this.leftPressed = false;
						sendMove(LEFT_OFF);
						break;
					case KeyCodes.KEY_RIGHT:
						SubmarineExperiment.this.rightPressed = false;
						sendMove(RIGHT_OFF);
						break;
				}
			}
		}
	}
	
	private final InternalNativePreviewHandler nativeEventHandler;
	
	public SubmarineExperiment(IConfigurationRetriever configurationRetriever, IBoardBaseController commandSender) {
		super(configurationRetriever, commandSender);
		
		this.createProvidedWidgets();
		
		SubmarineExperiment.uiBinder.createAndBindUi(this);
		
		this.buttons = new HashMap<String, Image>();
		this.buttons.put(FORWARD_ON,    this.upButton);
		this.buttons.put(BACKWARD_ON,  this.downButton);
		this.buttons.put(LEFT_ON,  this.leftButton);
		this.buttons.put(RIGHT_ON, this.rightButton);
		
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
			    SubmarineExperiment.this.boardController.clean();
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
			SubmarineExperiment.WEBCAM_REFRESH_TIME_PROPERTY, 
			SubmarineExperiment.DEFAULT_WEBCAM_REFRESH_TIME
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

		this.inputWidgetsPanel.setVisible(true);
		this.messages.setText("You can now control the submarine");
		this.messages.stop();
		this.nativeEventHandler.activate();
	}

	private boolean parseWebcamConfig(String initialConfiguration) {
		final JSONValue initialConfigValue   = JSONParser.parseStrict(initialConfiguration);
	    final JSONObject initialConfigObject = initialConfigValue.isObject();
	    if(initialConfigObject == null) {
	    	Window.alert("Error parsing submarine configuration: not an object: " + initialConfiguration);
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
	public void onUpMouseDown(MouseDownEvent event) {
		sendMove(FORWARD_ON);
		this.upPressed = true;
	}

	
	@SuppressWarnings("unused")
	@UiHandler("downButton")
	public void onDownMouseDown(MouseDownEvent event) {
		sendMove(BACKWARD_ON);
		this.downPressed = true;
	}

	
	@SuppressWarnings("unused")
	@UiHandler("leftButton")
	public void onLeftMouseDown(MouseDownEvent event) {
		sendMove(LEFT_ON);
		this.leftPressed = true;
	}

	
	@SuppressWarnings("unused")
	@UiHandler("rightButton")
	public void onRightMouseDown(MouseDownEvent event) {
		sendMove(RIGHT_ON);
		this.rightPressed = true;
	}

	@SuppressWarnings("unused")
	@UiHandler("upButton")
	public void onUpMouseUp(MouseUpEvent event) {
		sendMove(FORWARD_OFF);
		this.upPressed = false;
	}

	
	@SuppressWarnings("unused")
	@UiHandler("downButton")
	public void onDownMouseUp(MouseUpEvent event) {
		sendMove(BACKWARD_OFF);
		this.downPressed = false;
	}

	
	@SuppressWarnings("unused")
	@UiHandler("leftButton")
	public void onLeftMouseUp(MouseUpEvent event) {
		sendMove(LEFT_OFF);
		this.leftPressed = false;
	}

	
	@SuppressWarnings("unused")
	@UiHandler("rightButton")
	public void onRightMouseUp(MouseUpEvent event) {
		sendMove(RIGHT_OFF);
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
//		if(!this.buttonsEnabled)
//			return;
		
//		disableButtons();
//		enableButton(s);
		this.buttonsEnabled = false;
		final int currentMove = ++this.moveNumber;
		
		this.boardController.sendCommand(s, new IResponseCommandCallback() {
			
			@Override
			public void onFailure(CommException e) {
				
			}
			
			@Override
			public void onSuccess(ResponseCommand responseCommand) {
				SubmarineExperiment.this.buttonsEnabled = true;
	//			if(currentMove == SubmarineExperiment.this.moveNumber){
	//				enableButtons();
	//			}else
	//				disableButton(s);
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
