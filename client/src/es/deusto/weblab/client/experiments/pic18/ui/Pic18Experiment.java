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
* Author: Pablo Orduña <pablo@ordunya.com>
*         Luis Rodriguez <luis.rodriguez@opendeusto.es>
*
*/ 
package es.deusto.weblab.client.experiments.pic18.ui;

import java.util.Vector;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.json.client.JSONObject;
import com.google.gwt.json.client.JSONParser;
import com.google.gwt.json.client.JSONValue;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.Timer;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.Label;
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
import es.deusto.weblab.client.ui.widgets.IWlActionListener;
import es.deusto.weblab.client.ui.widgets.IWlWidget;
import es.deusto.weblab.client.ui.widgets.WlButton.IWlButtonUsed;
import es.deusto.weblab.client.ui.widgets.WlClockActivator;
import es.deusto.weblab.client.ui.widgets.WlPotentiometer;
import es.deusto.weblab.client.ui.widgets.WlPredictiveProgressBar;
import es.deusto.weblab.client.ui.widgets.WlPredictiveProgressBar.IProgressBarListener;
import es.deusto.weblab.client.ui.widgets.WlPredictiveProgressBar.IProgressBarTextUpdater;
import es.deusto.weblab.client.ui.widgets.WlPredictiveProgressBar.TextProgressBarTextUpdater;
import es.deusto.weblab.client.ui.widgets.WlSwitch;
import es.deusto.weblab.client.ui.widgets.WlTextBoxWithButton;
import es.deusto.weblab.client.ui.widgets.WlTimedButton;
import es.deusto.weblab.client.ui.widgets.WlTimer;
import es.deusto.weblab.client.ui.widgets.WlTimer.IWlTimerFinishedCallback;
import es.deusto.weblab.client.ui.widgets.WlWaitingLabel;
import es.deusto.weblab.client.ui.widgets.WlWebcam;

public class Pic18Experiment extends ExperimentBase{

	
	 /******************
	 * UIBINDER RELATED
	 ******************/
	
	interface PIC18UiBinder extends UiBinder<Widget, Pic18Experiment> {
	}

	private static final PIC18UiBinder uiBinder = GWT.create(PIC18UiBinder.class);
	
	private static final String DEMO_PROPERTY                         = "is.demo";
	private static final boolean DEFAULT_DEMO                         = false;
	
	private static final String WEBCAM_REFRESH_TIME_PROPERTY          = "webcam.refresh.millis";
	private static final int    DEFAULT_WEBCAM_REFRESH_TIME           = 400;
	
	private final int DEFAULT_EXPECTED_PROGRAMMING_TIME = 25000;

	private static final int IS_READY_QUERY_TIMER = 1000;
	private static final String STATE_NOT_READY = "not_ready";
	private static final String STATE_PROGRAMMING = "programming";
	private static final String STATE_READY = "ready";
	private static final String STATE_FAILED = "failed";
	
	public static class Style{
		public static final String TIME_REMAINING         = "wl-time_remaining";
		public static final String CLOCK_ACTIVATION_PANEL = "wl-clock_activation_panel"; 
	}
	
	private static final boolean DEBUG_ENABLED = false;
	
	@UiField public VerticalPanel verticalPanel;
	@UiField VerticalPanel widget;
	@UiField VerticalPanel innerVerticalPanel;
	@UiField HorizontalPanel uploadStructurePanel;
	
	@UiField Button uploadButton;
	@UiField Label selectProgram;
	@UiField Label clockInput;

	@UiField HorizontalPanel timerMessagesPanel;
	@UiField WlWaitingLabel messages;
	@UiField WlClockActivator clockActivator;
 
	@UiField HorizontalPanel switchesRow;
	@UiField HorizontalPanel buttonsRow;
	@UiField HorizontalPanel serialRow;
	@UiField HorizontalPanel webcamPanel;
	
	@UiField WlPredictiveProgressBar progressBar;
	
	@UiField WlSwitch switch5;
	@UiField WlSwitch switch4;
	@UiField WlSwitch switch3;
	@UiField WlSwitch switch2;
	@UiField WlSwitch switch1;
	@UiField WlSwitch switch0;
	
	@UiField WlPotentiometer pot0;
	@UiField WlPotentiometer pot1;	
	
	@UiField WlTimedButton timedButton1;
	@UiField WlTimedButton timedButton2;
	@UiField WlTimedButton timedButton3;
	@UiField WlTimedButton timedButton4;
	
	@UiField WlTextBoxWithButton serial0;
	
	//@UiField(provided=true)
	private UploadStructure uploadStructure;
	
	private WlWebcam webcam;
	
	@UiField(provided = true)
	WlTimer timer;
	
	private Timer readyTimer;
	private boolean deviceReady;
	private int expectedProgrammingTime = this.DEFAULT_EXPECTED_PROGRAMMING_TIME;

	private final Vector<Widget> interactiveWidgets;
	
	public Pic18Experiment(IConfigurationRetriever configurationRetriever, IBoardBaseController boardController){
		super(configurationRetriever, boardController);
		
		this.deviceReady = false;
		
		this.interactiveWidgets = new Vector<Widget>();
		
		this.createProvidedWidgets();
		
		Pic18Experiment.uiBinder.createAndBindUi(this);
		
		this.webcamPanel.add(this.webcam.getWidget());
		
		this.findInteractiveWidgets();
		
		this.disableInteractiveWidgets();
		
		if(isDemo()){
			this.selectProgram.setText(i18n.thisDemoDoesNotAllowUpload());
		}
	}
	
	private boolean isDemo(){
		return this.configurationRetriever.getBoolProperty(
				Pic18Experiment.DEMO_PROPERTY, 
				Pic18Experiment.DEFAULT_DEMO
			);
	}
	
	private int getWebcamRefreshingTime() {
		return this.configurationRetriever.getIntProperty(
				Pic18Experiment.WEBCAM_REFRESH_TIME_PROPERTY, 
				Pic18Experiment.DEFAULT_WEBCAM_REFRESH_TIME
			);
	}	
	
	/**
	 * Will find those interactive widgets that are defined on UiBinder
	 * and add them to the interactive widgets list, so that they can
	 * be disabled. This isn't too convenient but currently there doesn't 
	 * seem to be any other way around. That may change in the future.
	 */
	private void findInteractiveWidgets() {
		
		// Find switches & potentiometers (All in the same Row)
		for(int i = 0; i < this.switchesRow.getWidgetCount(); ++i){
			final Widget wid = this.switchesRow.getWidget(i);
			if(wid instanceof WlSwitch) {
				this.addInteractiveWidget(wid);
			}else if(wid instanceof WlPotentiometer){
				this.addInteractiveWidget(wid);
			}			
		}
		
		// Find timed buttons
		for(int i = 0; i < this.buttonsRow.getWidgetCount(); ++i) {
			final Widget wid = this.buttonsRow.getWidget(i);
			if(wid instanceof WlTimedButton) {
				final WlTimedButton swi = (WlTimedButton)wid;
				this.addInteractiveWidget(swi);
			}
		}
		
		// Add the textboxs for serial sending (Initially just one)
		for(int i = 0; i < this.buttonsRow.getWidgetCount(); ++i) {
			final Widget wid = this.serialRow.getWidget(0);
			if(wid instanceof WlTextBoxWithButton ) {
				final WlTextBoxWithButton swi = (WlTextBoxWithButton)wid;
				this.addInteractiveWidget(swi);
			}
		}
		
	}
	
	/**
	 * Creates those widgets that are specified in the UiBinder xml
	 * file but which are marked as provided because they can't be
	 * allocated using the default ctor.
	 */
	private void createProvidedWidgets() {
		this.webcam = GWT.create(WlWebcam.class);
		this.webcam.setTime(this.getWebcamRefreshingTime());
		
		this.timer = new WlTimer(false);
		
		this.timer.setTimerFinishedCallback(new IWlTimerFinishedCallback(){
			@Override
			public void onFinished() {
				Pic18Experiment.this.boardController.clean();
			}
		});
		
		if(!isDemo()){
			this.uploadStructure = new UploadStructure();
			this.uploadStructure.setFileInfo("program");
		}
	}
	
	@Override
	public void initialize(){
		
		// Doesn't seem to work from UiBinder.
		if(!isDemo()){
			this.uploadStructurePanel.add(this.uploadStructure.getFormPanel());
		}
	
		this.webcam.setVisible(false);
	}
	
	@Override
	public void queued(){
	    this.widget.setVisible(false);
	    this.selectProgram.setVisible(false);
	}
	
	
	/**
	 * Event handler which gets called whenever the upload button is pressed.
	 * The upload button is currently only visible when the file could not be
	 * uploaded on the reservation stage, generally due to wrong user input.
	 * 
	 * @param e
	 */
	@UiHandler("uploadButton")
	void handleClick(ClickEvent e) {
		boolean success = this.tryUpload();
		
		if(success)
			this.uploadButton.setVisible(false);
	}
	
	/**
	 * Helper method to try to upload a file. Currently, we only consider that an upload
	 * failed if the filename the user chose is empty.
	 * If the upload succeeds we load the standard experiment controls through loadStartControls and
	 * hide the upload panel, which is no longer needed.
	 * 
	 * @return True if the upload succeeds, false otherwise.
	 */
	private boolean tryUpload() {
		final boolean didChooseFile = !this.uploadStructure.getFileUpload().getFilename().isEmpty();
		
		if(didChooseFile) {
			this.uploadStructure.getFormPanel().setVisible(false);
			this.boardController.sendFile(this.uploadStructure, this.sendFileCallback);
			this.loadStartControls();
		} else {
			GWT.log("The user did not really choose a file");
		}
		
		return didChooseFile;
	}
	

	/**
	 * Called when the experiment starts. 
	 * @param time Time available for the experiment
	 * @param initialConfiguration JSON-encoded server-provided configuration parameters. 
	 * This feature is part of the API version 2. Parameters expected by this experiment
	 * are "webcam" and "expected_programming_time".
	 */
	@Override
	public void start(int time, String initialConfiguration){
		
	    if(parseWebcamConfig(initialConfiguration))
	    	return;
		
		try {
			final JSONValue parsedInitialConfiguration = JSONParser.parseStrict(initialConfiguration);
			double expectedProgrammingTime = parsedInitialConfiguration.isObject().get("expected_programming_time").isNumber().doubleValue();
			Pic18Experiment.this.expectedProgrammingTime = (int)(expectedProgrammingTime * 1000);
		} catch(Exception e) {	
			this.messages.setText("[PIC18] Did not receive the expected_programming_time parameter.");
    		GWT.log("[PIC18] Did not receive the expected_programming_time parameter.", null);
    		return;
		}
	
		// If it's not a demo, the user will have been prompted a file uploading form.
		// He might have indeed chosen a file to upload, or he might not.
		if(!isDemo()) {
			
			boolean success = this.tryUpload();
			
			// If the file upload attempt on the reserve stage failed, then we will have to display 
			// a button during the experiment itself so that the user can request the file he chose
			// be uploaded to the server.
			if(!success)
				this.uploadButton.setVisible(true);
			
		} else {
			this.loadStartControls();
		}
		
		// The experiment started, so we should start the timer.
		this.timer.start();
		
		// Start polling to know when the board has been programmed and the server is ready
		// to receive our requests.
		setupReadyTimer();
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
	
	/**
	 * Loads those controls that are meant to be displayed
	 * when the experiment starts.
	 */
	private void loadStartControls() {
		this.loadProgressBar();
		
	    this.widget.setVisible(true);
	    this.selectProgram.setVisible(false);
	    
	    
		this.loadWidgets();
		this.disableInteractiveWidgets();
	}
	
	
	
	/**
	 * Will setup the timer that will poll the experiment server for its state, to
	 * know when the board programming process ends and how.
	 */
	private void setupReadyTimer() {
		
		this.readyTimer = new Timer() {
			@Override
			public void run() {
				
				// Build the command to query the state.
				final Command command = new Command() {
					@Override
					public String getCommandString() {
						return "STATE";
					}
				}; //! new Command
				
				
				// Send the command and react to the response
				Pic18Experiment.this.boardController.sendCommand(command, new IResponseCommandCallback() {
					@Override
					public void onFailure(CommException e) {
						Pic18Experiment.this.messages.setText("There was an error while trying to find out whether the experiment is ready");
					}
					@Override
					public void onSuccess(ResponseCommand responseCommand) {
						
						// Read the full message returned by the exp server and ensure it's not empty
						final String resp = responseCommand.getCommandString();
						if(resp.length() == 0) 
							Pic18Experiment.this.messages.setText("The STATE query returned an empty result");
						
						// The command follows the format STATE=ready
						// Extract both parts
						final String [] tokens = resp.split("=", 2);
						if(tokens.length != 2 || !tokens[0].equals("STATE")) {
							Pic18Experiment.this.messages.setText("Unexpected response ot the STATE query: " + resp);
							return;
						}
						
						final String state = tokens[1];
						
						if(state.equals(STATE_NOT_READY)) {
							Pic18Experiment.this.readyTimer.schedule(IS_READY_QUERY_TIMER);
						} else if(state.equals(STATE_READY)) {
							// Ready
							Pic18Experiment.this.onDeviceReady();
						} else if(state.equals(STATE_PROGRAMMING)) {
							Pic18Experiment.this.readyTimer.schedule(IS_READY_QUERY_TIMER);
						} else if(state.equals(STATE_FAILED)) {
							Pic18Experiment.this.onDeviceProgrammingFailed();
						} else {
							Pic18Experiment.this.messages.setText("Received unexpected response to the STATE query");
						}
					} //! onSuccess
				}); //! new IResponseCommandCallback for the STATE command.
			} //! run() of the Timer
		}; //! new Timer
		
		
		this.readyTimer.schedule(1000);
		
	} //! setupReadyTimer
	
	
	final IResponseCommandCallback sendFileCallback = new IResponseCommandCallback() {
	    
	    @Override
	    public void onSuccess(ResponseCommand response) {
	    	Pic18Experiment.this.messages.setText(i18n.fileSent());
	    }

	    @Override
	    public void onFailure(CommException e) {
	    	
	    	GWT.log("It was not possible to send the file");
	    	
		    if(Pic18Experiment.DEBUG_ENABLED)
		    	Pic18Experiment.this.enableInteractiveWidgets();
		    
	    	Pic18Experiment.this.messages.stop();
	    	
	    	Pic18Experiment.this.progressBar.stop();
	    	Pic18Experiment.this.progressBar.setTextUpdater(new IProgressBarTextUpdater(){
				@Override
				public String generateText(double progress) {
					return "Error. Could not complete.";
				}});
				
			Pic18Experiment.this.messages.setText("Error sending file: " + e.getMessage());
		    
	    }
	};	
	
	/**
	 * Called when the STATE query tells us that the experiment is ready.
	 */
	private void onDeviceReady() {
		this.deviceReady = true;
		
		if(Pic18Experiment.this.progressBar.isWaiting()){
			this.progressBar.stop();
			this.progressBar.setVisible(false);
		}else
	    	// Make the bar finish in a few seconds, it will make itself
	    	// invisible once it is full.
			this.progressBar.finish(300);

		this.enableInteractiveWidgets();
		this.messages.setText("Device ready");
		this.messages.stop();
		this.clockInput.setVisible(true);
	}
	
	
	/**
	 * Called when the STATE query tells us that the board programming failed.
	 */
	private void onDeviceProgrammingFailed() {
		this.deviceReady = true;
		
		if(Pic18Experiment.this.progressBar.isWaiting()){
			this.progressBar.stop();
			this.progressBar.setVisible(false);
		}else
	    	// Make the bar finish in a few seconds, it will make itself
	    	// invisible once it is full.
			this.progressBar.finish(300);
    	
		this.messages.setText(i18n.deviceProgrammingFailed());
		this.messages.stop();	
	}
	
	private void loadWidgets() {
		
		this.webcam.setVisible(true);
		this.webcam.start();
		
	
		this.messages.setText(i18n.sendingFile());
		this.messages.start();
		
		final ClockActivationListener clockActivationListener = new ClockActivationListener(this.boardController, this.getResponseCommandCallback());
		this.clockActivator.addClockActivationListener(clockActivationListener);
		
		this.addInteractiveWidget(this.timer.getWidget());
		this.addInteractiveWidget(this.clockActivator);
		
		this.prepareSwitchesRow();
		this.prepareButtonsRow();
		
		this.innerVerticalPanel.setSpacing(20);
		
/*		IWlActionListener switchesListener = new IWlActionListener() {
			@Override
			public void onAction(IWlWidget widget) {
				//WlSwitch swicthItem = (WlSwitch)widget;
				String message = "SWITCH ";
				if(widget.equals(switch0)) {
					message += "0";
				}else if(widget.equals(switch1)) {
					message += "1";
				}else if(widget.equals(switch2)) {
					message += "2";
				}else if(widget.equals(switch3)) {
					message += "3";
				}else if(widget.equals(switch4)) {
					message += "4";
				}else if(widget.equals(switch5)) {
					message += "5";
				} 
				
				Pic18Experiment.this.boardController.sendCommand(message);
			}
		};*/
		
		this.pot1.addActionListener(new IWlActionListener(){
			@Override
			public void onAction(IWlWidget widget) {
				String message = "Analog 1 ";
				message += Double.toString(Pic18Experiment.this.pot1.getPower());
				if ((message.charAt(9) <= '9') && (message.charAt(9) >= '0') && (message.charAt(11) <= '9') && (message.charAt(11) >= '0') && (message.charAt(10)=='.')){
					Pic18Experiment.this.boardController.sendCommand(message);
				}else {
					Pic18Experiment.this.messages.setText("Valor no válido en potenciómetro: " + Double.toString(Pic18Experiment.this.pot0.getPower()));
				}
			}
		});
		
		this.pot0.addActionListener(new IWlActionListener(){
			@Override
			public void onAction(IWlWidget widget) {
				String message = "Analog 0 ";
				message += Double.toString(Pic18Experiment.this.pot0.getPower());
				if ((message.charAt(9) <= '9') && (message.charAt(9) >= '0') && (message.charAt(11) <= '9') && (message.charAt(11) >= '0') && (message.charAt(10)=='.')){
					Pic18Experiment.this.boardController.sendCommand(message);
				}else {
					Pic18Experiment.this.messages.setText("Valor no válido en potenciómetro: " + Double.toString(Pic18Experiment.this.pot0.getPower()));
				}
								
			}
		});
		
		this.serial0.addActionListener(new IWlActionListener(){
			@Override
			public void onAction(IWlWidget widget) {
				String message = "STRING ";
				message += Pic18Experiment.this.serial0.getText();
				Pic18Experiment.this.boardController.sendCommand(message);
			}
		});
		
		this.timedButton1.addButtonListener(new ButtonListener(1));
		this.timedButton2.addButtonListener(new ButtonListener(2));
		this.timedButton3.addButtonListener(new ButtonListener(3));
		this.timedButton4.addButtonListener(new ButtonListener(4));
	}
	
	private class ButtonListener implements IWlButtonUsed {
		 
		 private int n;
		 
		 public ButtonListener(int n) {
			 this.n = n;
		 }
		 
		 @Override
		 public void onPressed() {
			 String message = "timed button " + this.n + " on";
			 Pic18Experiment.this.boardController.sendCommand(message);				
		 }

		 @Override
		 public void onReleased() {
			 String message = "timed button " + this.n + " off";
			 Pic18Experiment.this.boardController.sendCommand(message);				
		 }
	 }
	
	
	private void loadProgressBar() {
		this.progressBar.setResolution(40);
		this.progressBar.setTextUpdater(new IProgressBarTextUpdater(){
			@Override
			public String generateText(double progress) {
				return "Programming device (" + (int)(progress*100) + "%)";
			}});
		
		// Set up a listener to automatically remove the progress
		// bar whenever it reaches a 100%.
		this.progressBar.setListener(new IProgressBarListener() {
			@Override
			public void onFinished() {
				if(Pic18Experiment.this.deviceReady){
					Pic18Experiment.this.progressBar.setVisible(false);
				}else{
					// This order is important, since setTextUpdater would call onFinished again
					Pic18Experiment.this.progressBar.keepWaiting();
					Pic18Experiment.this.progressBar.setTextUpdater(new TextProgressBarTextUpdater("Finishing programming..."));
				}
			}});
		
		this.progressBar.setWaitPoint(0.98);
		this.progressBar.setVisible(true);
		this.progressBar.setEstimatedTime(this.expectedProgrammingTime);
		this.progressBar.start();
	}
	
	private void addInteractiveWidget(Widget widget){
		this.interactiveWidgets.add(widget);
	}
	
	private void enableInteractiveWidgets(){
		for(int i = 0; i < this.interactiveWidgets.size(); ++i)
			this.interactiveWidgets.get(i).setVisible(true);		
	}
	
	private void disableInteractiveWidgets(){
		for(int i = 0; i < this.interactiveWidgets.size(); ++i)
			this.interactiveWidgets.get(i).setVisible(false);
	}
	
	/* Iterates through every switch in the switchesRow panel,
	 * setting up a listener for each of them. Switches found on it
	 * are defined anonymously on UiBinder, along with their title.
	 * This title is currently used as an integral identifier.
	 */
	private HorizontalPanel prepareSwitchesRow() {
		
		final WlSwitch [] switches = {
				this.switch0,
				this.switch1,
				this.switch2,
				this.switch3,
				this.switch4,
				this.switch5
		};
		
		for(int i = 0; i < switches.length; ++i){
			final WlSwitch swi = switches[i];
				
			final IWlActionListener actionListener = new SwitchListener(i, this.boardController, this.getResponseCommandCallback());
			swi.addActionListener(actionListener);
			this.addInteractiveWidget(swi);
		}
		
		return this.switchesRow;
	}

	/*
	 * Iterates through every timed button in the buttonsRow panel,
	 * setting up a listener for each of them. Buttons found on it
	 * are defined anonymously on UiBinder, along with their title.
	 * This title is currently used as an integral identifier.
	 */
	private HorizontalPanel prepareButtonsRow() {

		for(int i = 0; i < this.buttonsRow.getWidgetCount(); ++i) {
			final Widget wid = this.buttonsRow.getWidget(i);
			if(wid instanceof WlTimedButton) {
				this.addInteractiveWidget(wid);
			}
		}
		
		return this.buttonsRow;
	}

	@Override
	public void end(){
		
		if(this.readyTimer != null) {
			this.readyTimer.cancel();
			this.readyTimer = null;
		}
		
		if(this.webcam != null){
			this.webcam.dispose();
			this.webcam = null;
		}
		
		if(this.timer != null){
			this.timer.dispose();
			this.timer = null;
		}
		
		if(this.clockActivator != null){
			this.clockActivator.dispose();
			this.clockActivator = null;
		}
		
		for(int i = 0; i < this.switchesRow.getWidgetCount(); ++i) {
			final Widget wid = this.switchesRow.getWidget(i);
			if(wid instanceof WlSwitch)
				((WlSwitch)wid).dispose();
		}
		
		for(int i = 0; i < this.buttonsRow.getWidgetCount(); ++i) {
			final Widget wid = this.buttonsRow.getWidget(i);
			if(wid instanceof WlTimedButton)
				((WlTimedButton)wid).dispose();
		}
		
		if(this.progressBar != null)
			this.progressBar.stop();
		
		this.messages.stop();
	}
	
	@Override
	public void setTime(int time) {
		this.timer.updateTime(time);
	}
	
	@Override
	public Widget getWidget() {
		return this.widget;
	}
	
	protected IResponseCommandCallback getResponseCommandCallback(){
	    return new IResponseCommandCallback(){
		    @Override
			public void onSuccess(ResponseCommand responseCommand) {
	    		GWT.log("responseCommand: success", null);
		    }

		    @Override
			public void onFailure(CommException e) {
    			GWT.log("responseCommand: failure", null);
    			Pic18Experiment.this.messages.stop();
    			Pic18Experiment.this.messages.setText("Error sending command: " + e.getMessage());
		    }
		};	    
	}
}
