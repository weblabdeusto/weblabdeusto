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
package es.deusto.weblab.client.experiments.robot_proglist.ui;

import java.util.List;
import java.util.Vector;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.json.client.JSONObject;
import com.google.gwt.json.client.JSONParser;
import com.google.gwt.json.client.JSONValue;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.HorizontalPanel;
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

public class RobotProglistExperiment extends ExperimentBase {

	private static final String WEBCAM_REFRESH_TIME_PROPERTY   = "webcam.refresh.millis";
	private static final int    DEFAULT_WEBCAM_REFRESH_TIME    = 200;
	
	/******************
	 * UIBINDER RELATED
	 ******************/
	
	interface RobotProglistBoardUiBinder extends UiBinder<Widget, RobotProglistExperiment> {
	}

	private static final RobotProglistBoardUiBinder uiBinder = GWT.create(RobotProglistBoardUiBinder.class);
	
	public static class Style   {
		public static final String TIME_REMAINING          = "wl-time_remaining";
		public static final String CLOCK_ACTIVATION_PANEL  = "wl-clock_activation_panel"; 
	}

	private final List<Button> buttons = new Vector<Button>();
	
	@UiField(provided=true) WlTimer timer;
	
	// Root panel.
	@UiField VerticalPanel widget;
	
	@UiField VerticalPanel mainWidgetsPanel;
	
	@UiField WlWaitingLabel messages;
	
	@UiField HorizontalPanel inputWidgetsPanel;
	
	@UiField(provided=true) WlWebcam webcam;
	
	public RobotProglistExperiment(IConfigurationRetriever configurationRetriever, IBoardBaseController commandSender) {
		super(configurationRetriever, commandSender);
		
		this.createProvidedWidgets();
		
		RobotProglistExperiment.uiBinder.createAndBindUi(this);
	}
	
	/**
	 * Setup certain widgets that require it after the experiment has been 
	 * started.
	 */
	private void setupWidgets() {
		this.timer.setTimerFinishedCallback(new IWlTimerFinishedCallback(){
			@Override
			public void onFinished() {
			    RobotProglistExperiment.this.boardController.clean();
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
			RobotProglistExperiment.WEBCAM_REFRESH_TIME_PROPERTY, 
			RobotProglistExperiment.DEFAULT_WEBCAM_REFRESH_TIME
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

	    if(parseWebcamConfig(initialConfiguration))
	    	return;
	    
	    this.webcam.setVisible(true);
	    this.webcam.start();
	    
	    this.boardController.sendCommand("programs", new IResponseCommandCallback() {
			
			@Override
			public void onFailure(CommException e) {
				e.printStackTrace();
				RobotProglistExperiment.this.setMessage("Could not request experiments:" + e.getMessage());
				RobotProglistExperiment.this.messages.stop();
			}
			
			@Override
			public void onSuccess(ResponseCommand responseCommand) {
				RobotProglistExperiment.this.messages.stop();
				RobotProglistExperiment.this.buttons.clear();
				String response = responseCommand.getCommandString();
				setMessage(i18n.selectWhatProgramShouldBeSent());
				for(final String s : response.split(",")){
					if(s.trim().equals(""))
						continue;
					final Button button = new Button(s.trim());
					RobotProglistExperiment.this.buttons.add(button);
					button.addClickHandler(new ClickHandler() {
						
						@Override
						public void onClick(ClickEvent event) {
							for(Button b : RobotProglistExperiment.this.buttons)
								b.setVisible(false);
							
							setMessage("Programming " + s);
							RobotProglistExperiment.this.messages.start();
							RobotProglistExperiment.this.boardController.sendCommand("program:" + s.trim(), new IResponseCommandCallback() {
								
								@Override
								public void onFailure(CommException e) {
									setMessage(i18n.failed(e.getMessage()));
									RobotProglistExperiment.this.messages.stop();
								}
								
								@Override
								public void onSuccess(ResponseCommand responseCommand) {
									RobotProglistExperiment.this.messages.stop();
									if(responseCommand.getCommandString().startsWith("File sen")){
										RobotProglistExperiment.this.setMessage(i18n.fileSent());
									}
								}
							});
						}
					});
					RobotProglistExperiment.this.inputWidgetsPanel.add(button);
				}
			}
		});
	    
	    this.setMessage("Retrieving programs");
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
		this.messages.stop();
	}
	
	public void setMessage(String msg) {
		this.messages.setText(msg);
	}
}
