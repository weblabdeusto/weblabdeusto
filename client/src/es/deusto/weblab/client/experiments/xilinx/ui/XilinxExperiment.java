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
* Author: Pablo Orduña <pablo@ordunya.com>
*         Luis Rodriguez <luis.rodriguez@opendeusto.es>
*
*/ 
package es.deusto.weblab.client.experiments.xilinx.ui;

import java.util.Vector;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.json.client.JSONParser;
import com.google.gwt.json.client.JSONValue;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.Timer;
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
import es.deusto.weblab.client.ui.widgets.WlButton.IWlButtonUsed;
import es.deusto.weblab.client.ui.widgets.WlClockActivator;
import es.deusto.weblab.client.ui.widgets.WlPredictiveProgressBar;
import es.deusto.weblab.client.ui.widgets.WlPredictiveProgressBar.IProgressBarListener;
import es.deusto.weblab.client.ui.widgets.WlPredictiveProgressBar.IProgressBarTextUpdater;
import es.deusto.weblab.client.ui.widgets.WlPredictiveProgressBar.TextProgressBarTextUpdater;
import es.deusto.weblab.client.ui.widgets.WlSwitch;
import es.deusto.weblab.client.ui.widgets.WlTimedButton;
import es.deusto.weblab.client.ui.widgets.WlTimer;
import es.deusto.weblab.client.ui.widgets.WlTimer.IWlTimerFinishedCallback;
import es.deusto.weblab.client.ui.widgets.WlWaitingLabel;
import es.deusto.weblab.client.ui.widgets.WlWebcam;

public class XilinxExperiment extends ExperimentBase{

	
	 /******************
	 * UIBINDER RELATED
	 ******************/
	
	interface WlDeustoXilinxBasedBoardUiBinder extends UiBinder<Widget, XilinxExperiment> {
	}

	private static final WlDeustoXilinxBasedBoardUiBinder uiBinder = GWT.create(WlDeustoXilinxBasedBoardUiBinder.class);
	
	private static final String XILINX_DEMO_PROPERTY                  = "is.demo";
	private static final boolean DEFAULT_XILINX_DEMO                  = false;
	
	private static final String XILINX_MULTIRESOURCE_DEMO_PROPERTY   = "is.multiresource.demo";
	private static final boolean DEFAULT_MULTIRESOURCE_XILINX_DEMO   = false;
	
	private static final String DEFAULT_XILINX_WEBCAM_IMAGE_URL       = GWT.getModuleBaseURL() + "/waiting_url_image.jpg";
	
	private static final String XILINX_WEBCAM_REFRESH_TIME_PROPERTY   = "webcam.refresh.millis";
	private static final int    DEFAULT_XILINX_WEBCAM_REFRESH_TIME    = 400;
	
	private final int DEFAULT_EXPECTED_PROGRAMMING_TIME = 25000;
	private final int DEFAULT_EXPECTED_SYNTHESIZING_TIME = 120000;

	private static final int IS_READY_QUERY_TIMER = 1000;
	private static final String STATE_SYNTHESIZING_ERROR = "synthesizing_error";
	private static final String STATE_AWAITING_CODE = "awaiting_code";
	private static final String STATE_NOT_READY = "not_ready";
	private static final String STATE_SYNTHESIZING = "synthesizing";
	private static final String STATE_PROGRAMMING = "programming";
	private static final String STATE_READY = "ready";
	private static final String STATE_FAILED = "failed";
	private static final String STATE_NOT_ALLOWED = "not_allowed";
	
	// The state the experiment is currently in. Must be a string within the states list.
	private String currentState;
	
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
	
	@UiField HorizontalPanel timerMessagesPanel;
	@UiField WlWaitingLabel messages;
	@UiField WlClockActivator clockActivator;

	@UiField HorizontalPanel switchesRow;
	@UiField HorizontalPanel buttonsRow;
	@UiField HorizontalPanel webcamPanel;
	
	@UiField WlPredictiveProgressBar progressBar;
	
	//@UiField(provided=true)
	private UploadStructure uploadStructure;
	
	private WlWebcam webcam;
	
	@UiField(provided = true)
	WlTimer timer;
	
	private Timer readyTimer;
	private boolean deviceReady;
	private int expectedProgrammingTime = this.DEFAULT_EXPECTED_PROGRAMMING_TIME;
	private int expectedSynthesizingTime = this.DEFAULT_EXPECTED_SYNTHESIZING_TIME;
	
	private boolean synthesizingMode = false;

	private final Vector<Widget> interactiveWidgets;
	
	public XilinxExperiment(IConfigurationRetriever configurationRetriever, IBoardBaseController boardController){
		super(configurationRetriever, boardController);
		
		this.deviceReady = false;
		
		this.interactiveWidgets = new Vector<Widget>();
		
		this.createProvidedWidgets();
		
		XilinxExperiment.uiBinder.createAndBindUi(this);
		
		this.webcamPanel.add(this.webcam.getWidget());
		
		this.findInteractiveWidgets();
		
		this.disableInteractiveWidgets();
		
		if(isDemo()){
			if(isMultiresourceDemo()){
				this.selectProgram.setText(i18n.thisDemoDemonstratesMultiresourceXilinx());
			}else{
				this.selectProgram.setText(i18n.thisDemoDoesNotAllowUpload());
			}
		}
	}
	
	private boolean isDemo(){
		return this.configurationRetriever.getBoolProperty(
				XilinxExperiment.XILINX_DEMO_PROPERTY, 
				XilinxExperiment.DEFAULT_XILINX_DEMO
			);
	}
	
	private boolean isMultiresourceDemo(){
		return this.configurationRetriever.getBoolProperty(
				XilinxExperiment.XILINX_MULTIRESOURCE_DEMO_PROPERTY, 
				XilinxExperiment.DEFAULT_MULTIRESOURCE_XILINX_DEMO
			);
	}

	private int getWebcamRefreshingTime() {
		return this.configurationRetriever.getIntProperty(
				XilinxExperiment.XILINX_WEBCAM_REFRESH_TIME_PROPERTY, 
				XilinxExperiment.DEFAULT_XILINX_WEBCAM_REFRESH_TIME
			);
	}	
	
	/**
	 * Will find those interactive widgets that are defined on UiBinder
	 * and add them to the interactive widgets list, so that they can
	 * be disabled. This isn't too convenient but currently there doesn't 
	 * seem to be any other way around. That may change in the future.
	 */
	private void findInteractiveWidgets() {
		
		// Find switches
		for(int i = 0; i < this.switchesRow.getWidgetCount(); ++i){
			final Widget wid = this.switchesRow.getWidget(i);
			if(wid instanceof WlSwitch) {
				final WlSwitch swi = (WlSwitch)wid;
				this.addInteractiveWidget(swi);
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
		
	}
	
	/**
	 * Creates those widgets that are specified in the UiBinder xml
	 * file but which are marked as provided because they can't be
	 * allocated using the default ctor.
	 */
	private void createProvidedWidgets() {
		this.webcam = new WlWebcam(
				this.getWebcamRefreshingTime(),
				XilinxExperiment.DEFAULT_XILINX_WEBCAM_IMAGE_URL
			);
		
		this.timer = new WlTimer(false);
		
		this.timer.setTimerFinishedCallback(new IWlTimerFinishedCallback(){
			@Override
			public void onFinished() {
				XilinxExperiment.this.boardController.clean();
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
		final boolean success = this.tryUpload();
		
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
			
			// Extract the file extension.
			final String filename = this.uploadStructure.getFileUpload().getFilename();
			final String [] split = filename.split("\\.");
			String extension;
			if(split.length == 0)
				extension = "bit"; // BIT as default
			extension = split[split.length-1];
			
			this.uploadStructure.getFormPanel().setVisible(false);
			this.uploadStructure.setFileInfo(extension.toLowerCase());
			
			// TODO: Probably it would be more elegant if the server itself would decide whether we are synthesizing
			// and programming or just programming. However, at least for now, this will do fine. The mode is currently
			// used only to decide how to estimate progress bar length.
			if(extension.toLowerCase().equals("vhd"))
				this.synthesizingMode = true;
			
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
	 * are "webcam", "expected_programming_time", "expected_synthesizing_time".
	 */
	@Override
	public void start(int time, String initialConfiguration){
		
		final JSONValue parsedInitialConfiguration = JSONParser.parseStrict(initialConfiguration);
		
		this.currentState = STATE_NOT_READY;
		
		try {
			final String webcamUrl = parsedInitialConfiguration.isObject().get("webcam").isString().stringValue();
			this.webcam.setUrl(webcamUrl);
		} catch(Exception e) {
			this.messages.setText("[Xilinx] Did not receive the webcam parameter.");
    		GWT.log("[Xilinx] Did not receive the webcam parameter.", null);
    		return;
		}
		
		try {
			double expectedProgrammingTime = parsedInitialConfiguration.isObject().get("expected_programming_time").isNumber().doubleValue();
			XilinxExperiment.this.expectedProgrammingTime = (int)(expectedProgrammingTime * 1000);
		} catch(Exception e) {	
			this.messages.setText("[Xilinx] Did not receive the expected_programming_time parameter.");
    		GWT.log("[Xilinx] Did not receive the expected_programming_time parameter.", null);
    		return;
		}
		
		// TODO: Consider whether this parameter should or should not be mandatory. For now, it isn't. 
		// If the parameter is not provided by the server then the default will be used.
		try {
			double expectedSynthesizingTime = parsedInitialConfiguration.isObject().get("expected_synthesizing_time").isNumber().doubleValue();
			XilinxExperiment.this.expectedSynthesizingTime = (int)(expectedSynthesizingTime * 1000);
		} catch(Exception e) {	
			//this.messages.setText("[Xilinx] Did not receive the expected_synthesizing_time parameter.");
    		GWT.log("[Xilinx] Did not receive the expected_synthesizing_time parameter. Using the default. ", null);
    		XilinxExperiment.this.expectedSynthesizingTime = this.DEFAULT_EXPECTED_SYNTHESIZING_TIME;
    		//return;
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
				XilinxExperiment.this.boardController.sendCommand(command, new IResponseCommandCallback() {
					@Override
					public void onFailure(CommException e) {
						XilinxExperiment.this.messages.setText("There was an error while trying to find out whether the experiment is ready");
					}
					@Override
					public void onSuccess(ResponseCommand responseCommand) {
						
						// Read the full message returned by the exp server and ensure it's not empty
						final String resp = responseCommand.getCommandString();
						if(resp.length() == 0) 
							XilinxExperiment.this.messages.setText("The STATE query returned an empty result");
						
						// The command follows the format STATE=ready
						// Extract both parts
						final String [] tokens = resp.split("=", 2);
						if(tokens.length != 2 || !tokens[0].equals("STATE")) {
							XilinxExperiment.this.messages.setText("Unexpected response ot the STATE query: " + resp);
							return;
						}
						
						final String state = tokens[1];
						
						// Update the current state. This is needed in other places within this experiment.
						XilinxExperiment.this.currentState = state;
						
						System.out.println("[DBG]: Current state is: " + state);
						
						if(state.equals(STATE_NOT_READY)) {
							XilinxExperiment.this.readyTimer.schedule(IS_READY_QUERY_TIMER);
						} else if(state.equals(STATE_READY)) {
							// Ready
							XilinxExperiment.this.onDeviceReady();
						} else if(state.equals(STATE_SYNTHESIZING)) {
							// Check in a few seconds whether the state changed.
							XilinxExperiment.this.readyTimer.schedule(IS_READY_QUERY_TIMER);
						} else if(state.equals(STATE_PROGRAMMING)) {
							// Check in a few seconds whether the state changed.
							XilinxExperiment.this.readyTimer.schedule(IS_READY_QUERY_TIMER);
						} else if(state.equals(STATE_FAILED)) {
							// Something failed in the programming.
							XilinxExperiment.this.onDeviceProgrammingFailed();
						} else if(state.equals(STATE_SYNTHESIZING_ERROR)) {
							// Compiling failed. 
							XilinxExperiment.this.onDeviceSynthesizingError();
						} else if(state.equals(STATE_NOT_ALLOWED)) {
							// That filetype is not allowed.
							XilinxExperiment.this.onFileNotAllowed();
						} else if(state.equals(STATE_AWAITING_CODE)) {
							// Awaiting for VHDL code.
							// TODO: Implement this. THIS IS NOT YET SUPPORTED.
							XilinxExperiment.this.messages.setText("STATE_AWAITING_CODE is not yet supported");
						} else {
							XilinxExperiment.this.messages.setText("Received unexpected response to the STATE query");
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
	    	XilinxExperiment.this.messages.setText(i18n.fileSent());
	    }

	    @Override
	    public void onFailure(CommException e) {
	    	
	    	GWT.log("It was not possible to send the file");
	    	
		    if(XilinxExperiment.DEBUG_ENABLED)
		    	XilinxExperiment.this.enableInteractiveWidgets();
		    
	    	XilinxExperiment.this.messages.stop();
	    	
	    	XilinxExperiment.this.progressBar.stop();
	    	XilinxExperiment.this.progressBar.setTextUpdater(new IProgressBarTextUpdater(){
				@Override
				public String generateText(double progress) {
					return "Error. Could not complete.";
				}});
				
			XilinxExperiment.this.messages.setText("Error sending file: " + e.getMessage());
		    
	    }
	};	
	
	/**
	 * Called when the STATE query tells us that the experiment is ready.
	 */
	private void onDeviceReady() {
		this.deviceReady = true;
		
		if(XilinxExperiment.this.progressBar.isWaiting()){
			this.progressBar.stop();
			this.progressBar.setVisible(false);
		}else
	    	// Make the bar finish in a few seconds, it will make itself
	    	// invisible once it is full.
			this.progressBar.finish(300);

		this.enableInteractiveWidgets();
		this.messages.setText(i18n.deviceReady());
		this.messages.stop();
	}
	
	
	/**
	 * Called when the STATE query tells us that the filetype we uploaded is
	 * not allowed.
	 */
	private void onFileNotAllowed() {
		this.deviceReady = true;
		
		if(XilinxExperiment.this.progressBar.isWaiting()){
			this.progressBar.stop();
			this.progressBar.setVisible(false);
		}else
	    	// Make the bar finish in a few seconds, it will make itself
	    	// invisible once it is full.
			this.progressBar.finish(300);
    	
		this.messages.setText(i18n.fileNotAllowed());
		this.messages.stop();	
	}
	
	
	/**
	 * Called when the STATE query tells us that the board programming failed.
	 */
	private void onDeviceProgrammingFailed() {
		this.deviceReady = true;
		
		if(XilinxExperiment.this.progressBar.isWaiting()){
			this.progressBar.stop();
			this.progressBar.setVisible(false);
		}else
	    	// Make the bar finish in a few seconds, it will make itself
	    	// invisible once it is full.
			this.progressBar.finish(300);
    	
		this.messages.setText(i18n.deviceProgrammingFailed());
		this.messages.stop();	
	}
	
	// TODO: Implement this properly.
	/**
	 * Called when the STATE query tells us that the compiling process failed.
	 */
	private void onDeviceSynthesizingError() {
		this.deviceReady = false;
		
		if(XilinxExperiment.this.progressBar.isWaiting()){
			this.progressBar.stop();
			this.progressBar.setVisible(false);
		}else
			// Make the bar finish in a few seconds, it will make itself
			// invisible once it is full.
			this.progressBar.finish(300);
		
		
		final Command compilingResultCommand = new Command() {
			@Override
			public String getCommandString() {
				return "SYNTHESIZING_RESULT";
			}};
		
		this.messages.setText("Synthesizing failed");
		this.messages.stop();
			
		// Find out why compiling failed through the COMPILING_RESULT command.
		XilinxExperiment.this.boardController.sendCommand(compilingResultCommand, new IResponseCommandCallback() {
			@Override
			public void onFailure(CommException e) {
				XilinxExperiment.this.messages.setText("There was an error while trying to retrieve the SYNTHESIZING_RESULT");
			}

			@Override
			public void onSuccess(ResponseCommand responseCommand) {
				XilinxExperiment.this.messages.setText("Synthesizing failed: \n" + responseCommand);
			}
		});
		

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
	}

	private void loadProgressBar() {
		this.progressBar.setResolution(40);
		this.progressBar.setTextUpdater(new IProgressBarTextUpdater(){
			@Override
			public String generateText(double progress) {
				// Set the current action. Depending on the state, it will
				// be either compiling or programming the device.
				
				// TODO: Remove this.
				System.out.println("[DBG/GT]: State: " + XilinxExperiment.this.currentState);
				
				final String currentAction;
				if( XilinxExperiment.this.currentState.equals(STATE_PROGRAMMING) )
					currentAction = "Programming device";
				else if( XilinxExperiment.this.currentState.equals(STATE_SYNTHESIZING) )
					currentAction = "Synthesizing VHDL";
				else
					currentAction = "Processing";
				
				return currentAction + " (" + (int)(progress*100) + "%)";
			}});
		
		// Set up a listener to automatically remove the progress
		// bar whenever it reaches a 100%.
		this.progressBar.setListener(new IProgressBarListener() {
			@Override
			public void onFinished() {
				if(XilinxExperiment.this.deviceReady){
					XilinxExperiment.this.progressBar.setVisible(false);
				}else{
					// This order is important, since setTextUpdater would call onFinished again
					XilinxExperiment.this.progressBar.keepWaiting();
					XilinxExperiment.this.progressBar.setTextUpdater(new TextProgressBarTextUpdater(i18n.finishingProgramming() + "..."));
				}
			}});
		
		this.progressBar.setWaitPoint(0.98);
		this.progressBar.setVisible(true);
		
		if(this.synthesizingMode)
			this.progressBar.setEstimatedTime(this.expectedSynthesizingTime + this.expectedProgrammingTime);
		else
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
		
		for(int i = 0; i < this.switchesRow.getWidgetCount(); ++i){
			final Widget wid = this.switchesRow.getWidget(i);
			if(wid instanceof WlSwitch) {
				final WlSwitch swi = (WlSwitch)wid;
				
				// Avoid trying to convert non-numerical titles (which serve
				// as identifiers). Not exactly an elegant way to do it.
				if(swi.getTitle().length() != 1) 
					continue;
				
				final int id = this.switchesRow.getWidgetCount() - Integer.parseInt(swi.getTitle()) - 1;
				final IWlActionListener actionListener = new SwitchListener(id, this.boardController, this.getResponseCommandCallback());
				swi.addActionListener(actionListener);
				this.addInteractiveWidget(swi);
			}
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
				final WlTimedButton timedButton = (WlTimedButton)wid;
				
				if(timedButton.getTitle().length() != 1)
					continue;
				
				final int id = Integer.parseInt(timedButton.getTitle());
				final IWlButtonUsed buttonUsed = 
					new ButtonListener(id, this.boardController, this.getResponseCommandCallback());
				timedButton.addButtonListener(buttonUsed);
				this.addInteractiveWidget(timedButton);
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
    			XilinxExperiment.this.messages.stop();
    			XilinxExperiment.this.messages.setText("Error sending command: " + e.getMessage());
		    }
		};	    
	}
}
