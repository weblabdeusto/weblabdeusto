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
*
*/ 
package es.deusto.weblab.client.experiments.logic.ui;

import java.util.HashMap;
import java.util.Map;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.json.client.JSONParser;
import com.google.gwt.json.client.JSONValue;
import com.google.gwt.media.client.Audio;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.Timer;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.DialogBox;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.HasHorizontalAlignment;
import com.google.gwt.user.client.ui.HasVerticalAlignment;
import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.Image;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;

import es.deusto.weblab.client.WebLabClient;
import es.deusto.weblab.client.comm.exceptions.CommException;
import es.deusto.weblab.client.configuration.IConfigurationRetriever;
import es.deusto.weblab.client.dto.experiments.Command;
import es.deusto.weblab.client.dto.experiments.ResponseCommand;
import es.deusto.weblab.client.experiments.logic.circuit.Circuit;
import es.deusto.weblab.client.experiments.logic.circuit.CircuitParser;
import es.deusto.weblab.client.experiments.logic.circuit.Gate;
import es.deusto.weblab.client.experiments.logic.circuit.InvalidCircuitException;
import es.deusto.weblab.client.experiments.logic.circuit.Operation;
import es.deusto.weblab.client.experiments.logic.circuit.Switch;
import es.deusto.weblab.client.experiments.logic.commands.GetCircuitCommand;
import es.deusto.weblab.client.experiments.logic.commands.SolveCircuitCommand;
import es.deusto.weblab.client.lab.comm.callbacks.IResponseCommandCallback;
import es.deusto.weblab.client.lab.experiments.ExperimentBase;
import es.deusto.weblab.client.lab.experiments.IBoardBaseController;
import es.deusto.weblab.client.ui.audio.AudioManager;
import es.deusto.weblab.client.ui.widgets.EasyGrid;
import es.deusto.weblab.client.ui.widgets.WlTimer;
import es.deusto.weblab.client.ui.widgets.WlTimer.IWlTimerFinishedCallback;
import es.deusto.weblab.client.ui.widgets.WlWaitingLabel;
import es.deusto.weblab.client.ui.widgets.WlWebcam;

public class LogicExperiment extends ExperimentBase {
	
	
	/******************
	 * UIBINDER RELATED
	 ******************/
	
	interface WlDeustoLogicBasedBoardUiBinder extends UiBinder<Widget, LogicExperiment> {
	}

	private static final WlDeustoLogicBasedBoardUiBinder uiBinder = GWT.create(WlDeustoLogicBasedBoardUiBinder.class);
	

	public static final String LOGIC_WEBCAM_IMAGE_URL_PROPERTY = "es.deusto.weblab.logic.webcam.image.url";
	public static final String DEFAULT_LOGIC_WEBCAM_IMAGE_URL = GWT.isScript() ? "https://www.weblab.deusto.es/webcam/logic0/image.jpg?size=2" : "";
	
	private static final String LOGIC_WEBCAM_REFRESH_TIME_PROPERTY = "es.deusto.weblab.logic.webcam.refresh.millis";
	private static final int DEFAULT_LOGIC_WEBCAM_REFRESH_TIME = 400;
	
	private static final String LOGIC_USE_WEBCAM_PROPERTY = "logic.use.webcam";
	private static final boolean DEFAULT_LOGIC_USE_WEBCAM = false;
	
	public static class Style   {
		public static final String TIME_REMAINING          = "wl-time_remaining";
		public static final String CLOCK_ACTIVATION_PANEL  = "wl-clock_activation_panel"; 
		public static final String LOGIC_INPUT_VALUE_LABEL = "logic-input-value-label"; 
		public static final String LOGIC_MOUSE_POINTER_HAND = "logic-mouse-pointer-hand";
	}

	private final Map<Operation, String> operation2url = new HashMap<Operation, String>();
	private final Map<String, Operation> url2operation = new HashMap<String, Operation>();
	private final String unknownOperationUrl = GWT.getModuleBaseURL() + "img/logic/UNKNOWN.png";
	
	private final String zeroString = "0";
	private final String oneString  = "1";
	
	/** WIDGETS **/
	
	// Root panel.
	@UiField VerticalPanel widget;
	
	// Contains the experiment introduction. (Welcome message, etc).
	@UiField VerticalPanel introPanel;
	
	// Contains the intro text itself.
	@UiField VerticalPanel textIntroPanel;
	
	// The panel of the experiment itself.
	@UiField VerticalPanel expPanel;
	
	@UiField HorizontalPanel circuitAndWebcamPanel;
	
	@UiField(provided=true)
	WlTimer timer;
	
	@UiField(provided=true)
	WlWebcam webcam;
	
	@UiField
	Image light;
	
	@UiField WlWaitingLabel messages;
	@UiField EasyGrid circuitGrid;
	
	private HTML input1Label; // Input values
	private HTML input2Label;
	private HTML input3Label;
	private HTML input4Label;
	private Image gateA1Image; // 1st level (A) of gates
	private Image gateA2Image;
	private Image gateA3Image;
	private Image gateB1Image; // 2nd level (B) of gates
	private Image gateB2Image;
	private Image gateC1Image; // 3rd level (C) of gates
	private Image unknownGateImage;
	private DialogBox changeUnknownGateDialogBox;
	
	// Button to send the solution.
	@UiField Button sendSolutionButton;
	
	@UiField Label referenceToShowBoxesLabel;
	
	// DTOs
	private final boolean useWebcam;
	private Command lastCommand;
	private Circuit circuit;
	private boolean solving = true;
	private int points = 0;
	private final Resources resources = GWT.create(Resources.class);
	
	private final IResponseCommandCallback commandCallback = new IResponseCommandCallback(){

	    @Override
		public void onSuccess(ResponseCommand responseCommand) {
	    	LogicExperiment.this.processCommandSent(responseCommand);		    
	    }

	    @Override
		public void onFailure(CommException e) {
	    	LogicExperiment.this.messages.setText("Error: " + e.getMessage() + ". Please, notify the WebLab-Deusto administrators at weblab@deusto.es about this error.");
	    }
	    
	};
	
	public LogicExperiment(IConfigurationRetriever configurationRetriever, IBoardBaseController commandSender) {
		super(configurationRetriever, commandSender);
		this.useWebcam = this.configurationRetriever.getBoolProperty(LOGIC_USE_WEBCAM_PROPERTY, DEFAULT_LOGIC_USE_WEBCAM);
		
		this.fillMaps();
		
		this.createProvidedWidgets();
		
		LogicExperiment.uiBinder.createAndBindUi(this);
	}
	
	/* Creates those widgets that are placed through UiBinder but
	 * whose ctors need to take certain parameters and hence be
	 * instanced in code.
	 */
	private void createProvidedWidgets() {
		
		this.webcam = new WlWebcam(this.getWebcamRefreshingTime(), this.getWebcamImageUrl());
		
		this.timer = new WlTimer(false);
		
		this.timer.setTimerFinishedCallback(new IWlTimerFinishedCallback(){
			@Override
			public void onFinished() {
			    LogicExperiment.this.boardController.clean();
			}
		});	
		
	}
	
	private void fillMaps(){
		
	    this.operation2url.put(Operation.AND,  GWT.getModuleBaseURL() + "img/logic/AND.png");
	    this.operation2url.put(Operation.NAND, GWT.getModuleBaseURL() + "img/logic/NAND.png");
	    this.operation2url.put(Operation.OR,   GWT.getModuleBaseURL() + "img/logic/OR.png");
	    this.operation2url.put(Operation.NOR,  GWT.getModuleBaseURL() + "img/logic/NOR.png");
	    this.operation2url.put(Operation.XOR,  GWT.getModuleBaseURL() + "img/logic/XOR.png");
	    
	    for(final Operation op : this.operation2url.keySet())
	    	this.url2operation.put(this.operation2url.get(op), op);
	    
	}
	
	public String getURL(Operation operation){
	    return this.operation2url.get(operation);
	}
		
	public Operation getOperation(String url){
	    return this.url2operation.get(url);
	}
		
	void changeUnknownGate(Operation operation) {
	    this.unknownGateImage.setUrl(this.getURL(operation));
	    this.sendSolutionButton.setEnabled(true);
	    this.circuit.setUnknownOperation(0, operation);
	}

	/**
	 * The initialize function gets called on the "reserve" stage,
	 * before the experiment starts.
	 */
	@Override
	public void initialize(){
	}
	
	@Override
	public void initializeReserved(){
		this.textIntroPanel.setVisible(false);
	}
	
	@Override
	public void queued(){
	    this.widget.setVisible(false);
	}	
	
	/**
	 * This function gets called just when the actual experiment starts, after
	 * the reserve is done and the queue is over.
	 */
	@Override
	public void start(int time, String initialConfiguration) {
		final JSONValue parsedInitialConfiguration = JSONParser.parseStrict(initialConfiguration);
		final String webcamUrl = parsedInitialConfiguration.isObject().get("webcam").isString().stringValue();
		
		this.textIntroPanel.setVisible(false);
		
		if(this.useWebcam) {
			this.webcam.setUrl(webcamUrl);
			this.webcam.setVisible(true);
		} else {
			this.light.setVisible(true);
			turnOffLight();
		}
		
	    this.points = 0;
	    this.widget.setVisible(true);
		
	    this.timer.start();	
		
		// Inputs
		this.input1Label = new HTML(this.getFormatedInputLabel(this.zeroString, 1));
		this.input1Label.setStyleName(Style.LOGIC_INPUT_VALUE_LABEL);
		this.circuitGrid.setWidget(0, 0, this.input1Label);
		this.input2Label = new HTML(this.getFormatedInputLabel(this.zeroString, 2));
		this.input2Label.setStyleName(Style.LOGIC_INPUT_VALUE_LABEL);
		this.circuitGrid.setWidget(1, 0, this.input2Label);
		this.input3Label = new HTML(this.getFormatedInputLabel(this.zeroString, 3));
		this.input3Label.setStyleName(Style.LOGIC_INPUT_VALUE_LABEL);
		this.circuitGrid.setWidget(3, 0, this.input3Label);		
		this.input4Label = new HTML(this.getFormatedInputLabel(this.zeroString, 4));
		this.input4Label.setStyleName(Style.LOGIC_INPUT_VALUE_LABEL);
		this.circuitGrid.setWidget(4, 0, this.input4Label);
		
		// Gates (level A)
		this.gateA1Image = new Image(this.unknownOperationUrl);
		this.circuitGrid.setWidget(0, 2, this.gateA1Image);
		this.gateA2Image = new Image(this.unknownOperationUrl);
		this.circuitGrid.setWidget(2, 2, this.gateA2Image);
		this.gateA3Image = new Image(this.unknownOperationUrl);
		this.circuitGrid.setWidget(4, 2, this.gateA3Image);

		// Gates (level B)
		this.gateB1Image = new Image(this.unknownOperationUrl);
		this.circuitGrid.setWidget(1, 4, this.gateB1Image);
		this.gateB2Image = new Image(this.unknownOperationUrl);
		this.circuitGrid.setWidget(3, 4, this.gateB2Image);

		// Gates (level C)
		this.gateC1Image = new Image(this.unknownOperationUrl);
		this.circuitGrid.setWidget(2, 6, this.gateC1Image);
		
		// Connections
		for(final RowColumnPair pair : RowColumnPair.getRowsColumnPairs()){
		    final Image pairImage = new Image(pair.getImageResourceWeb(this.resources));
		    this.circuitGrid.setWidget(pair.getRow(), pair.getColumn() + 1, pairImage);
		}
		
		// Setting the Unknown Gate
		this.unknownGateImage = this.gateA2Image;
		this.unknownGateImage.addStyleName(Style.LOGIC_MOUSE_POINTER_HAND);
		this.changeUnknownGateDialogBox = new ChangeUnknownGateDialogBox(this);
		this.unknownGateImage.addClickHandler(new ClickHandler(){
			
		    @Override
		    public void onClick(ClickEvent event) {
		    	if(LogicExperiment.this.solving)
		    		//WlDeustoLogicBasedBoard.this.changeUnknownGateDialogBox.show();
		    		LogicExperiment.this.changeUnknownGateDialogBox.showRelativeTo(LogicExperiment.this.referenceToShowBoxesLabel);
		    }
		    
		});
		
		// Webcam
		final Widget webcamWidget;
		if(this.useWebcam) {
			this.webcam.start();
			webcamWidget = this.webcam.getWidget();
		} else {
			webcamWidget = this.light;
		}
		
		this.circuitAndWebcamPanel.add(webcamWidget);
		this.circuitAndWebcamPanel.setCellHorizontalAlignment(this.circuitGrid, HasHorizontalAlignment.ALIGN_RIGHT);
		
		this.circuitAndWebcamPanel.setCellVerticalAlignment(webcamWidget, HasVerticalAlignment.ALIGN_MIDDLE);
		this.circuitAndWebcamPanel.setCellHorizontalAlignment(webcamWidget, HasHorizontalAlignment.ALIGN_LEFT);
		
		// Messages
		this.messages.setText("Receiving the circuit");
		this.messages.start();
		
		this.sendCommand(new GetCircuitCommand());
	
    	this.sendSolutionButton.setVisible(true);
	}	
	
	void turnOffLight() {
		this.light.setUrl(GWT.getModuleBaseURL() + "/img/bulb_off.png");
	}
	
	void turnOnLight() {
		this.light.setUrl(GWT.getModuleBaseURL() + "/img/bulb_on.png");
	}
	
	@Override
	public boolean expectsPostEnd(){
		return true;
	}
	
	@Override
	public void postEnd(String initialData, String endData){
		if(endData == null){
			this.messages.setText(i18n.finishedWaitingPunctuation() + "...");
		}else{
			this.messages.setText(i18n.finishedYourPunctuation(endData));
			this.widget.add(new HTML(i18n.checkTheRankingHere(WebLabClient.baseLocation + "/weblab/admin/winners.py")));
		}
	}
	
	/**
	 * @param event Click event that is passed to the handler. 
	 */
	@UiHandler("sendSolutionButton")
	public void onSendSolutionClicked(ClickEvent event) {
		LogicExperiment.this.messages.setVisible(true);
		LogicExperiment.this.sendCommand(new SolveCircuitCommand(LogicExperiment.this.circuit));
		LogicExperiment.this.messages.setText(i18n.sendingSolution());
		LogicExperiment.this.messages.start();
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
		if(this.webcam != null){
			this.webcam.setVisible(false);
			this.webcam.dispose();
			this.webcam = null;
		}	
		if(this.timer != null){
			this.timer.setVisible(false);
			this.timer.dispose();
			this.timer = null;
		}
		if(this.messages != null){
			this.messages.dispose();
		}
		if(this.sendSolutionButton != null) {
			this.sendSolutionButton.setVisible(false);
		}
	}
	
	private String getWebcamImageUrl() {
		return this.configurationRetriever.getProperty(
			LogicExperiment.LOGIC_WEBCAM_IMAGE_URL_PROPERTY, 
				this.getDefaultWebcamImageUrl()
			);
	}
	
	protected String getDefaultWebcamImageUrl(){
		return LogicExperiment.DEFAULT_LOGIC_WEBCAM_IMAGE_URL;
	}

	private int getWebcamRefreshingTime() {
		return this.configurationRetriever.getIntProperty(
			LogicExperiment.LOGIC_WEBCAM_REFRESH_TIME_PROPERTY, 
			LogicExperiment.DEFAULT_LOGIC_WEBCAM_REFRESH_TIME
			);
	}

	private void sendCommand(Command command){
		this.lastCommand = command;
		this.boardController.sendCommand(command, this.commandCallback);
	}
	
	private void processCommandSent(ResponseCommand responseCommand) {
		if (this.lastCommand instanceof GetCircuitCommand) {
			this.messages.stop();
			this.messages.setText("");
			final CircuitParser circuitParser = new CircuitParser();
			try {
				this.circuit = circuitParser.parseCircuit(responseCommand
						.getCommandString());
			} catch (final InvalidCircuitException e) {
				this.messages.setText("Invalid Circuit received: "
						+ e.getMessage());
				return;
			}
			this.sendSolutionButton.setEnabled(false);
			this.updateCircuitGrid();
		} else if (this.lastCommand instanceof SolveCircuitCommand) {
			this.messages.stop();

			if (responseCommand.getCommandString().startsWith("FAIL")) {
				this.solving = false;
				
				if(Audio.isSupported()) {
					@SuppressWarnings("unused")
					final Audio audio = Audio.createIfSupported();
				
				}
				
				AudioManager.getInstance().playBest("snd/wrong");
				
				this.messages.setText(i18n.wrongOneGameOver(this.points));
				this.sendSolutionButton.setEnabled(false);
			} else if (responseCommand.getCommandString().startsWith("OK")) {
				this.points++;
				turnOnLight();
				this.messages.setText(i18n.wellDone1point());
								
				AudioManager.getInstance().playBest("snd/applause");
				
				final Timer sleepTimer = new Timer() {

					@Override
					public void run() {
						LogicExperiment.this
								.sendCommand(new GetCircuitCommand());
						turnOffLight();
					}
					
				};
				sleepTimer.schedule(2000);
			}

		} else {
			// TODO: Unknown command!
		}
	}

	private void updateCircuitGrid() {
	    final Gate gateC1 = this.circuit.getRoot();
	    final Gate gateB1 = (Gate)gateC1.getRight();
	    final Gate gateB2 = (Gate)gateC1.getLeft();
	    final Gate gateA1 = (Gate)gateB1.getRight();
	    final Gate gateA2 = (Gate)gateB1.getLeft();
	    final Gate gateA3 = (Gate)gateB2.getLeft();
	    final Switch switch1 = (Switch)gateA1.getRight();
	    final Switch switch2 = (Switch)gateA1.getLeft();
	    final Switch switch3 = (Switch)gateA2.getLeft();
	    final Switch switch4 = (Switch)gateA3.getLeft();
	    
	    this.gateC1Image.setUrl(this.getURL(gateC1.getOperation()));
	    this.gateB1Image.setUrl(this.getURL(gateB1.getOperation()));
	    this.gateB2Image.setUrl(this.getURL(gateB2.getOperation()));
	    this.gateA1Image.setUrl(this.getURL(gateA1.getOperation()));
	    this.gateA2Image.setUrl(this.getURL(gateA2.getOperation()));
	    this.gateA3Image.setUrl(this.getURL(gateA3.getOperation()));
	    
	    this.input1Label.setHTML(this.getFormatedInputLabel(switch1.turned?this.oneString:this.zeroString, 1));
	    this.input2Label.setHTML(this.getFormatedInputLabel(switch2.turned?this.oneString:this.zeroString, 2));
	    this.input3Label.setHTML(this.getFormatedInputLabel(switch3.turned?this.oneString:this.zeroString, 3));
	    this.input4Label.setHTML(this.getFormatedInputLabel(switch4.turned?this.oneString:this.zeroString, 4));
	    
	    this.unknownGateImage.setUrl(this.unknownOperationUrl);
	}
	
	private String getFormatedInputLabel(String labelText, int inputNumber)
	{
	    switch ( inputNumber )
	    {
	    case 1:
		return labelText+"<br /><br />";
	    case 4:
		return "<br />" + labelText;
	    default:
		return labelText;
	    }
	}
}
