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
* 		  Pablo Orduña <pablo.orduna@deusto.es>
* 		  
*/ 
package es.deusto.weblab.client.experiments.submarine.ui;

import java.util.HashMap;
import java.util.Map;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.KeyCodes;
import com.google.gwt.event.dom.client.MouseDownEvent;
import com.google.gwt.event.dom.client.MouseUpEvent;
import com.google.gwt.json.client.JSONBoolean;
import com.google.gwt.json.client.JSONObject;
import com.google.gwt.json.client.JSONParser;
import com.google.gwt.json.client.JSONValue;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.Event;
import com.google.gwt.user.client.Event.NativePreviewEvent;
import com.google.gwt.user.client.Event.NativePreviewHandler;
import com.google.gwt.user.client.Timer;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.Image;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;

import es.deusto.weblab.client.HistoryProperties;
import es.deusto.weblab.client.comm.exceptions.CommException;
import es.deusto.weblab.client.configuration.IConfigurationRetriever;
import es.deusto.weblab.client.dto.experiments.ResponseCommand;
import es.deusto.weblab.client.lab.comm.callbacks.IResponseCommandCallback;
import es.deusto.weblab.client.lab.experiments.ExperimentBase;
import es.deusto.weblab.client.lab.experiments.IBoardBaseController;
import es.deusto.weblab.client.ui.widgets.IWlActionListener;
import es.deusto.weblab.client.ui.widgets.IWlWidget;
import es.deusto.weblab.client.ui.widgets.WlButton;
import es.deusto.weblab.client.ui.widgets.WlSwitch;
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

	private static final String UP_ON  = "UP ON";
	private static final String UP_OFF = "UP OFF";

	private static final String DOWN_ON  = "DOWN ON";
	private static final String DOWN_OFF = "DOWN OFF";


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
	@UiField Image forwardButton;
	@UiField Image backwardButton;
	@UiField Image upButton;
	@UiField Image downButton;
	@UiField Image rightButton;
	@UiField Image leftButton;
	@UiField Image lightImage;
	@UiField WlButton foodButton;
	@UiField WlSwitch lightSwitch;
	
	@UiField Image thermometer;
	@UiField HTML temperature;
	
	@UiField Widget submarineGrid;
	@UiField Widget submarinePanel;
	@UiField Widget activateSubmarinePanel;
	@UiField Widget activateSubmarinePanel2;
	
	@UiField Image lookHereImage;
	
	private boolean forwardPressed = false;
	private boolean backwardPressed = false;
	private boolean upPressed = false;
	private boolean downPressed = false;
	private boolean leftPressed = false;
	private boolean rightPressed = false;
	
	private final Map<String, Image> buttons;
	
	@UiField(provided = true) WlWebcam webcam1;
	@UiField(provided = true) WlWebcam webcam2;
	
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
					case ' ':
						onDownPressed();
						event.cancel();
						break;
					case KeyCodes.KEY_BACKSPACE:
						onUpPressed();
						event.cancel();
						break;
					case KeyCodes.KEY_UP:
						onForwardPressed();
						event.cancel();
						break;
					case KeyCodes.KEY_DOWN:
						onBackwardPressed();
						event.cancel();
						break;
					case KeyCodes.KEY_LEFT:
						onLeftPressed();
						event.cancel();
						break;
					case KeyCodes.KEY_RIGHT:
						onRightPressed();
						event.cancel();
						break;
				}
			} else if(event.getTypeInt() == Event.ONKEYUP) {
				
				switch(event.getNativeEvent().getKeyCode()) {
					case ' ':
						onDownReleased();
						event.cancel();
						break;
					case KeyCodes.KEY_BACKSPACE:
						onUpReleased();
						event.cancel();
						break;
					case KeyCodes.KEY_UP:
						onForwardReleased();
						event.cancel();
						break;
					case KeyCodes.KEY_DOWN:
						onBackwardReleased();
						event.cancel();
						break;
					case KeyCodes.KEY_LEFT:
						onLeftReleased();
						event.cancel();
						break;
					case KeyCodes.KEY_RIGHT:
						onRightReleased();
						event.cancel();
						break;
				}
			}
		}

		private void onUpReleased() {
			SubmarineExperiment.this.upPressed = false;
			sendMove(UP_OFF);
		}
		
		private void onDownReleased() {
			SubmarineExperiment.this.downPressed = false;
			sendMove(DOWN_OFF);
		}
		
		private void onRightReleased() {
			SubmarineExperiment.this.rightPressed = false;
			sendMove(RIGHT_OFF);
		}

		private void onLeftReleased() {
			SubmarineExperiment.this.leftPressed = false;
			sendMove(LEFT_OFF);
		}

		private void onBackwardReleased() {
			SubmarineExperiment.this.backwardPressed = false;
			sendMove(BACKWARD_OFF);
		}

		private void onForwardReleased() {
			SubmarineExperiment.this.forwardPressed = false;
			sendMove(FORWARD_OFF);
		}

		private void onUpPressed() {
			if(!SubmarineExperiment.this.upPressed) {
				SubmarineExperiment.this.upPressed = true;
				sendMove(UP_ON);
			}
		}

		private void onDownPressed() {
			if(!SubmarineExperiment.this.downPressed) {
				SubmarineExperiment.this.downPressed = true;
				sendMove(DOWN_ON);
			}
		}

		private void onRightPressed() {
			if(!SubmarineExperiment.this.rightPressed) {
				SubmarineExperiment.this.rightPressed = true;
				sendMove(RIGHT_ON);
			}
		}

		private void onLeftPressed() {
			if(!SubmarineExperiment.this.leftPressed) {
				SubmarineExperiment.this.leftPressed = true;
				sendMove(LEFT_ON);
			}
		}

		private void onBackwardPressed() {
			if(!SubmarineExperiment.this.backwardPressed) {
				SubmarineExperiment.this.backwardPressed = true;
				sendMove(BACKWARD_ON);
			}
		}

		private void onForwardPressed() {
			if(!SubmarineExperiment.this.forwardPressed) {
				SubmarineExperiment.this.forwardPressed = true;
				sendMove(FORWARD_ON);
			}
		}
	}
	
	private final InternalNativePreviewHandler nativeEventHandler;
	
	public SubmarineExperiment(IConfigurationRetriever configurationRetriever, IBoardBaseController commandSender) {
		super(configurationRetriever, commandSender);
		
		this.createProvidedWidgets();
		
		SubmarineExperiment.uiBinder.createAndBindUi(this);
		
		this.buttons = new HashMap<String, Image>();
		this.buttons.put(FORWARD_ON,   this.forwardButton);
		this.buttons.put(BACKWARD_ON,  this.backwardButton);
		this.buttons.put(LEFT_ON,      this.leftButton);
		this.buttons.put(RIGHT_ON,     this.rightButton);
		this.buttons.put(UP_ON,        this.upButton);
		this.buttons.put(DOWN_ON,      this.downButton);
		
		this.nativeEventHandler = new InternalNativePreviewHandler();
	}
	
	/**
	 * Setup certain widgets that require it after the experiment has been 
	 * started.
	 */
	private void setupWidgets() {
		this.lightSwitch.addActionListener(new IWlActionListener() {
			
			@Override
			public void onAction(IWlWidget widget) {
				boolean state = SubmarineExperiment.this.lightSwitch.isSwitched();
				SubmarineExperiment.this.boardController.sendCommand("LIGHT " + (state?"ON":"OFF"));
				SubmarineExperiment.this.lightImage.setUrl(GWT.getModuleBaseURL() + "img/bulb_" + (state?"on":"off") + ".png");
			}
		});
		
		this.foodButton.addActionListener(new IWlActionListener() {
			
			@Override
			public void onAction(IWlWidget widget) {
				SubmarineExperiment.this.boardController.sendCommand("FOOD", new IResponseCommandCallback() {
					
					@Override
					public void onFailure(CommException e) {
						setMessage("Error feeding: " + e.getMessage());
					}
					
					@Override
					public void onSuccess(ResponseCommand responseCommand) {
						if(responseCommand.getCommandString().startsWith("fed")) {
							SubmarineExperiment.this.lookHereImage.setVisible(true);
							final Timer t = new Timer() {
								@Override
								public void run() {
									SubmarineExperiment.this.lookHereImage.setVisible(false);
								}
							};
							t.schedule(5000);
							setMessage(i18n.fishFed());
						} else if (responseCommand.getCommandString().startsWith("notfed:")) {
							final String time = responseCommand.getCommandString().substring("notfed:".length());
							setMessage(i18n.fishAlreadyFed(time));
						} else {
							setMessage(i18n.fishNotFed(responseCommand.getCommandString()));
						}
					}
				});
			}
		});
		
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
		
		this.webcam1 = GWT.create(WlWebcam.class);
		this.webcam1.setTime(this.getWebcamRefreshingTime());
		this.webcam2 = GWT.create(WlWebcam.class);
		this.webcam2.setTime(this.getWebcamRefreshingTime());
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
	    this.widget.setVisible(true);
	    
	    this.setupWidgets();
	    
	    final JSONObject config = parseWebcamConfig(initialConfiguration);
	    if(config == null)
	    	return;

	    if(!config.containsKey("light")) {
	    	Window.alert("\"light\" key not found in the initial configuration: " + initialConfiguration);
	    	return;
	    }
	    
	    final JSONBoolean light = config.get("light").isBoolean();
	    if(light != null && light.booleanValue()) {
	    	this.lightImage.setUrl(GWT.getModuleBaseURL() + "img/bulb_on.png");
	    	this.lightSwitch.switchWithoutFiring(true);
	    } else {
	    	this.lightImage.setUrl(GWT.getModuleBaseURL() + "img/bulb_off.png");
	    	this.lightSwitch.switchWithoutFiring(false);
	    }
	    
	    if(config.containsKey("temperature")) {
	    	this.thermometer.setUrl(GWT.getModuleBaseURL() + "/img/experiments/submarine-thermometer.png");
	    	final double celsius = config.get("temperature").isNumber().doubleValue();
	    	final double fahrenheit = celsius * 1.8 + 32;
	    	this.temperature.setHTML(celsius + " ºC /<br/> " + fahrenheit + " ºF");
	    	this.temperature.setVisible(true);
	    	this.thermometer.setVisible(true);
	    }
	    
	    final String osWidget = HistoryProperties.getValue(HistoryProperties.WIDGET, "");
	    final boolean widgetMode = !osWidget.isEmpty() && (osWidget.startsWith("cam") || osWidget.startsWith("button"));
	    
	    if (widgetMode) {
		    this.webcam1.setVisible(false);
		    this.webcam2.setVisible(false);
			this.inputWidgetsPanel.setVisible(false);
			this.messages.setText("");
			this.messages.stop();
	    	
	    	if (osWidget.equals("cam1")) {
			    this.webcam1.setVisible(true);
			    this.webcam1.start();
	    	} else if(osWidget.equals("cam2")) {
			    this.webcam2.setVisible(true);
			    this.webcam2.start();
	    	} else if(osWidget.startsWith("button")) {
				this.inputWidgetsPanel.setVisible(true);
				this.activateSubmarinePanel.setVisible(false);
	    	}
	    	
	    } else {
		    this.webcam1.setVisible(true);
		    this.webcam1.start();
		    this.webcam2.setVisible(true);
		    this.webcam2.start();
	
			this.inputWidgetsPanel.setVisible(true);
			this.messages.setText(i18n.youCanNowControlTheAquarium());
			this.messages.stop();
	    }
	}

	@SuppressWarnings("unused")
	@UiHandler("activateSubmarineButton")
	public void onSubmarineActivate(ClickEvent event) {
		this.activateSubmarinePanel.setVisible(false);
		this.activateSubmarinePanel2.setVisible(true);
	}
	
	@SuppressWarnings("unused")
	@UiHandler("activateSubmarineButton2")
	public void onSubmarineActivateConfirm(ClickEvent event) {
		Event.addNativePreviewHandler(this.nativeEventHandler);
		this.nativeEventHandler.activate();
		this.submarineGrid.setVisible(true);
		this.submarinePanel.setVisible(true);
		this.activateSubmarinePanel2.setVisible(false);
	}
		
	@SuppressWarnings("unused")
	@UiHandler("upButton")
	public void onUpMouseDown(MouseDownEvent event) {
		sendMove(UP_ON);
		this.upPressed = true;
	}

	@SuppressWarnings("unused")
	@UiHandler("downButton")
	public void onDownMouseDown(MouseDownEvent event) {
		sendMove(DOWN_ON);
		this.downPressed = true;
	}

	@SuppressWarnings("unused")
	@UiHandler("forwardButton")
	public void onForwardMouseDown(MouseDownEvent event) {
		sendMove(FORWARD_ON);
		this.forwardPressed = true;
	}

	
	@SuppressWarnings("unused")
	@UiHandler("backwardButton")
	public void onBackwardMouseDown(MouseDownEvent event) {
		sendMove(BACKWARD_ON);
		this.backwardPressed = true;
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
		sendMove(UP_OFF);
		this.upPressed = false;
	}
	
	@SuppressWarnings("unused")
	@UiHandler("downButton")
	public void onDownMouseUp(MouseUpEvent event) {
		sendMove(DOWN_OFF);
		this.downPressed = false;
	}
	
	@SuppressWarnings("unused")
	@UiHandler("forwardButton")
	public void onForwardMouseUp(MouseUpEvent event) {
		sendMove(FORWARD_OFF);
		this.forwardPressed = false;
	}

	
	@SuppressWarnings("unused")
	@UiHandler("backwardButton")
	public void onBackwardMouseUp(MouseUpEvent event) {
		sendMove(BACKWARD_OFF);
		this.backwardPressed = false;
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
	
	private void enableButtons(){
		for(Image img : this.buttons.values())
			img.setStyleName("wl-img-button");
	}
	
	private void disableButtons(){
		for(Image img : this.buttons.values())
			img.setStyleName("wl-disabled-img-button");
	}

	private void sendMove(final String s){
		if(s.endsWith("ON")) {
			disableButtons();
			enableButton(s);
		} else 
			enableButtons();
		
		this.boardController.sendCommand(s, new IResponseCommandCallback() {
			
			@Override
			public void onFailure(CommException e) {
				Window.alert("Error sending message: " + e.getMessage());
			}
			
			@Override
			public void onSuccess(ResponseCommand responseCommand) {
				System.out.println(s + " sent. Obtained: " + responseCommand.getCommandString());
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
		if(this.webcam1 != null){
			this.webcam1.dispose();
		}
		if(this.webcam2 != null){
			this.webcam2.dispose();
		}
	}
	
	public void setMessage(String msg) {
		this.messages.setText(msg);
	}	
	

	private JSONObject parseWebcamConfig(String initialConfiguration) {
		final JSONValue initialConfigValue   = JSONParser.parseStrict(initialConfiguration);
	    final JSONObject initialConfigObject = initialConfigValue.isObject();
	    if(initialConfigObject == null) {
	    	Window.alert("Error parsing submarine configuration: not an object: " + initialConfiguration);
	    	return null;
	    }
	    
	    configureWebcam(this.webcam1, initialConfigObject, 1);
	    configureWebcam(this.webcam2, initialConfigObject, 2);
	    
	    return initialConfigObject;
	}
	
	private void configureWebcam(WlWebcam webcam, JSONObject initialConfigObject, int number) {
		final JSONValue webcamValue = initialConfigObject.get("webcam" + number);
	    if(webcamValue != null) {
	    	final String urlWebcam = webcamValue.isString().stringValue();
	    	webcam.setUrl(urlWebcam);
	    }
	    
	    final JSONValue mjpegValue = initialConfigObject.get("mjpeg" + number);
	    if(mjpegValue != null) {
	    	final String mjpeg = mjpegValue.isString().stringValue();
	    	int width = 320;
	    	int height = 240;
	    	if(initialConfigObject.get("mjpegWidth" + number) != null) {
	    		final JSONValue mjpegWidth = initialConfigObject.get("mjpegWidth" + number);
	    		if(mjpegWidth.isNumber() != null) {
	    			width = (int)mjpegWidth.isNumber().doubleValue();
	    		} else if(mjpegWidth.isString() != null) {
	    			width = Integer.parseInt(mjpegWidth.isString().stringValue());
	    		}
	    	}
	    	if(initialConfigObject.get("mjpegHeight" + number) != null) {
	    		final JSONValue mjpegHeight = initialConfigObject.get("mjpegHeight" + number);
	    		if(mjpegHeight.isNumber() != null) {
	    			height = (int)mjpegHeight.isNumber().doubleValue();
	    		} else if(mjpegHeight.isString() != null) {
	    			height = Integer.parseInt(mjpegHeight.isString().stringValue());
	    		}
	    	}
	    	webcam.setStreamingUrl(mjpeg, width, height);
	    }
	}
}
