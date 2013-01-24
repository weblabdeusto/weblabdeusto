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
package es.deusto.weblab.client.experiments.robot_standard.ui;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.json.client.JSONObject;
import com.google.gwt.json.client.JSONParser;
import com.google.gwt.json.client.JSONValue;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;

import es.deusto.weblab.client.comm.exceptions.CommException;
import es.deusto.weblab.client.configuration.IConfigurationRetriever;
import es.deusto.weblab.client.dto.experiments.Command;
import es.deusto.weblab.client.dto.experiments.ResponseCommand;
import es.deusto.weblab.client.lab.comm.UploadStructure;
import es.deusto.weblab.client.lab.comm.callbacks.IResponseCommandCallback;
import es.deusto.weblab.client.lab.experiments.ExperimentBase;
import es.deusto.weblab.client.lab.experiments.IBoardBaseController;
import es.deusto.weblab.client.ui.widgets.WlTimer;
import es.deusto.weblab.client.ui.widgets.WlTimer.IWlTimerFinishedCallback;
import es.deusto.weblab.client.ui.widgets.WlWaitingLabel;
import es.deusto.weblab.client.ui.widgets.WlWebcam;

public class RobotStandardExperiment extends ExperimentBase {
	
	private static final String WEBCAM_REFRESH_TIME_PROPERTY   = "webcam.refresh.millis";
	private static final int    DEFAULT_WEBCAM_REFRESH_TIME    = 200;

	/******************
	 * UIBINDER RELATED
	 ******************/
	
	interface RobotStandardBoardUiBinder extends UiBinder<Widget, RobotStandardExperiment> {
	}

	private static final RobotStandardBoardUiBinder uiBinder = GWT.create(RobotStandardBoardUiBinder.class);
	
	public static class Style   {
		public static final String TIME_REMAINING          = "wl-time_remaining";
		public static final String CLOCK_ACTIVATION_PANEL  = "wl-clock_activation_panel"; 
	}

	@UiField(provided=true) WlTimer timer;
	
	// Root panel.
	@UiField VerticalPanel widget;
	
	@UiField VerticalPanel mainWidgetsPanel;
	
	@UiField WlWaitingLabel messages;
	
	@UiField VerticalPanel uploadStructurePanel;
	
	@UiField(provided=true) WlWebcam webcam;
	
	@UiField Button uploadButton;
	
	private UploadStructure uploadStructure;
	
	public RobotStandardExperiment(IConfigurationRetriever configurationRetriever, IBoardBaseController commandSender) {
		super(configurationRetriever, commandSender);
		
		this.createProvidedWidgets();
		
		RobotStandardExperiment.uiBinder.createAndBindUi(this);
	}
	
	final IResponseCommandCallback sendFileCallback = new IResponseCommandCallback() {
		
		@Override
		public void onFailure(CommException e) {
			RobotStandardExperiment.this.uploadStructurePanel.setVisible(false);
			RobotStandardExperiment.this.messages.stop();
			setMessage(i18n.failed(e.getMessage()));
		}
		
		@Override
		public void onSuccess(ResponseCommand responseCommand) {
			RobotStandardExperiment.this.uploadStructurePanel.setVisible(false);
			RobotStandardExperiment.this.messages.stop();
			if(responseCommand.getCommandString().toLowerCase().trim().equals("ok")){
				setMessage(i18n.theProgramIsBeingExecutedInTheBot());
			}else{
				setMessage(i18n.thereWasAnError(responseCommand.getCommandString()));
			}
		}
	};
	
	/**
	 * Setup certain widgets that require it after the experiment has been 
	 * started.
	 */
	private void setupWidgets() {
		this.timer.setTimerFinishedCallback(new IWlTimerFinishedCallback(){
			@Override
			public void onFinished() {
			    RobotStandardExperiment.this.boardController.clean();
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
		
		this.uploadStructure = new UploadStructure();
		this.uploadStructure.setFileInfo("program");
	}
	
	private int getWebcamRefreshingTime() {
		return this.configurationRetriever.getIntProperty(
			RobotStandardExperiment.WEBCAM_REFRESH_TIME_PROPERTY, 
			RobotStandardExperiment.DEFAULT_WEBCAM_REFRESH_TIME
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
	public void start(int time, String initialConfiguration) {
	    this.widget.setVisible(true);
	    
	    this.setupWidgets();
	    
	    if(parseWebcamConfig(initialConfiguration))
	    	return;
	    
	    tryUpload();
	}	
	
	@UiHandler("uploadButton")
	void handleClick(@SuppressWarnings("unused") ClickEvent e) {
		tryUpload();
	}
	
	void tryUpload() {
		final boolean didChooseFile = !this.uploadStructure.getFileUpload().getFilename().isEmpty();
		
		if(didChooseFile) {
		    this.webcam.setVisible(true);
		    this.webcam.start();

			this.uploadButton.setVisible(false);
		    this.uploadStructure.getFormPanel().setVisible(false);
			this.boardController.sendFile(this.uploadStructure, this.sendFileCallback);
		    this.setMessage(i18n.sendingFile());
		    this.messages.start();
		    this.sendGetConfigurationCommand();
		} else {
			this.uploadButton.setVisible(true);
		}
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
			public void onFailure(CommException e) {
				RobotStandardExperiment.this.setMessage("It was not possible to obtain the configuration");
			}
			@Override
			public void onSuccess(ResponseCommand responseCommand) {
			}
		});
	}
	
}
