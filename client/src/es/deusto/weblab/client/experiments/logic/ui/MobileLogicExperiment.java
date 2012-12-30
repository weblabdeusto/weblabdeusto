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
import com.google.gwt.resources.client.ImageResource;
import com.google.gwt.user.client.Timer;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.DialogBox;
import com.google.gwt.user.client.ui.Grid;
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
import es.deusto.weblab.client.experiments.gpib.ui.GpibExperiment;
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
import es.deusto.weblab.client.ui.widgets.WlTimer;
import es.deusto.weblab.client.ui.widgets.WlWaitingLabel;
import es.deusto.weblab.client.ui.widgets.WlWebcam;
import es.deusto.weblab.client.ui.widgets.WlTimer.IWlTimerFinishedCallback;

public class MobileLogicExperiment extends ExperimentBase {

	public static final String LOGIC_WEBCAM_IMAGE_URL_PROPERTY = "es.deusto.weblab.logic.webcam.image.url";
	public static final String DEFAULT_LOGIC_WEBCAM_IMAGE_URL = "https://www.weblab.deusto.es/webcam/logic0/image.jpg?size=1";
	
	private static final String LOGIC_WEBCAM_REFRESH_TIME_PROPERTY = "es.deusto.weblab.logic.webcam.refresh.millis";
	private static final int DEFAULT_LOGIC_WEBCAM_REFRESH_TIME = 400;
	
	private static final String LOGIC_USE_WEBCAM_PROPERTY = "logic.use.webcam";
	private static final boolean DEFAULT_LOGIC_USE_WEBCAM = false;
	
	public static class Style{
		public static final String TIME_REMAINING          = "wl-time_remaining";
		public static final String CLOCK_ACTIVATION_PANEL  = "wl-clock_activation_panel"; 
		public static final String LOGIC_INPUT_VALUE_LABEL = "logic-small-input-value-label"; 
		public static final String LOGIC_MOUSE_POINTER_HAND = "logic-mouse-pointer-hand";
	}

	private final Map<Operation, ImageResource> operation2url = new HashMap<Operation, ImageResource>();
	
	private final String zeroString = "0";
	private final String oneString  = "1";
	
	// Widgets
	private final VerticalPanel widget;
	private final VerticalPanel removableWidgetsPanel;
	private HorizontalPanel circuitPanel;
	private WlWebcam webcam;
	private WlTimer timer;
	private WlWaitingLabel messages;
	private Grid circuitGrid;
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
	private Button sendSolutionButton;
	private final Label referenceToShowBoxesLabel = new Label("");
	private Image light;
	
	// DTOs
	private final boolean useWebcam;
	private Command lastCommand;
	private Circuit circuit;
	private boolean solving = true;
	private int points = 0;
	private final ClickHandler unkownGateHandler;
	private final MobileResources resources = GWT.create(MobileResources.class);
	
	private final IResponseCommandCallback commandCallback = new IResponseCommandCallback(){

	    @Override
		public void onSuccess(ResponseCommand responseCommand) {
		MobileLogicExperiment.this.processCommandSent(responseCommand);		    
	    }

	    @Override
		public void onFailure(CommException e) {
		MobileLogicExperiment.this.messages.setText("Error: " + e.getMessage() + ". Please, notify the WebLab-Deusto administrators at weblab@deusto.es about this error.");
	    }
	};
	
	public MobileLogicExperiment(IConfigurationRetriever configurationRetriever, IBoardBaseController commandSender) {
		super(configurationRetriever, commandSender);
		
		this.useWebcam = this.configurationRetriever.getBoolProperty(LOGIC_USE_WEBCAM_PROPERTY, DEFAULT_LOGIC_USE_WEBCAM);
		
		this.fillMaps();
		
		this.widget = new VerticalPanel();
		this.widget.setWidth("100%");
		this.widget.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
		
		this.removableWidgetsPanel = new VerticalPanel();
		this.removableWidgetsPanel.setWidth("100%");
		this.removableWidgetsPanel.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
		this.removableWidgetsPanel.setSpacing(20);
		
		this.unkownGateHandler = new ClickHandler(){
		    @Override
		    public void onClick(ClickEvent event) {
			if(MobileLogicExperiment.this.solving)
			    MobileLogicExperiment.this.changeUnknownGateDialogBox.show();
			    MobileLogicExperiment.this.changeUnknownGateDialogBox.showRelativeTo(MobileLogicExperiment.this.referenceToShowBoxesLabel);
			
		    }
		};
	}
	
	private void fillMaps(){
	    this.operation2url.put(Operation.AND,  this.resources.smallAND());
	    this.operation2url.put(Operation.NAND, this.resources.smallNAND());
	    this.operation2url.put(Operation.OR,   this.resources.smallOR());
	    this.operation2url.put(Operation.NOR,  this.resources.smallNOR());
	    this.operation2url.put(Operation.XOR,  this.resources.smallXOR());
	}
	
	public ImageResource getURL(Operation operation){
	    return this.operation2url.get(operation);
	}
		
	void changeUnknownGate(Operation operation) {
	    this.setUnknownGate(this.getURL(operation));
	    this.sendSolutionButton.setEnabled(true);
	    this.circuit.setUnknownOperation(0, operation);
	}
	
	private void setUnknownGate(ImageResource resource){
		final Image image = new Image(resource);
		this.circuitGrid.setWidget(2, 2, image);
		image.addClickHandler(this.unkownGateHandler);
	}

	@Override
	public void initialize(){
		this.removableWidgetsPanel.add(new Label(i18n.welcomeToWebLabDeustoLogic()));
		this.removableWidgetsPanel.add(new Label(i18n.replaceTheUnknownGate()));
		this.removableWidgetsPanel.add(new Label(i18n.solveAsManyCircuitsAsPossible()));
		this.removableWidgetsPanel.add(new HTML(i18n.youCanCheckYourScoreAt()));
		
		this.widget.add(this.removableWidgetsPanel);
	}
	
	@Override
	public void initializeReserved(){
		
	}
	
	@Override
	public void queued(){
	    this.widget.setVisible(false);
	}	
	
	@Override
	public void start(int time, String initialConfiguration) {
		final JSONValue parsedInitialConfiguration = JSONParser.parseStrict(initialConfiguration);
		final String webcamUrl = parsedInitialConfiguration.isObject().get("webcam").isString().stringValue();

		this.points = 0;
	    this.widget.setVisible(true);
		
		while(this.removableWidgetsPanel.getWidgetCount() > 0)
		    this.removableWidgetsPanel.remove(0);

		// Timer
		this.timer = new WlTimer();
		this.timer.setStyleName(GpibExperiment.Style.TIME_REMAINING);
		this.timer.getWidget().setWidth("30%");
		this.timer.setTimerFinishedCallback(new IWlTimerFinishedCallback(){
			@Override
			public void onFinished() {
			    MobileLogicExperiment.this.boardController.clean();
			}
		});
		this.removableWidgetsPanel.add(this.timer.getWidget());		

		// Webcam
    	this.webcam = new WlWebcam(this.getWebcamRefreshingTime(), webcamUrl);
    	
		final Widget webcamWidget;		
    	if(this.useWebcam){
			webcamWidget = this.webcam.getWidget();
    		this.webcam.start();
    	} else {
    		this.light = new Image();
			webcamWidget = this.light;
    		turnOffLight();
    	}
		this.removableWidgetsPanel.add(webcamWidget);
    		
		// Horizontal Panel
		this.circuitPanel = new HorizontalPanel();
		this.circuitPanel.setWidth("100%");
		this.circuitPanel.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
		
		this.circuitPanel.add(this.referenceToShowBoxesLabel);
		
		// Circuit
		this.circuitGrid = new Grid(5, 8);
		this.circuitGrid.setBorderWidth(0);
		this.circuitPanel.add(this.circuitGrid);
		
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
		this.gateA1Image = new Image(this.resources.smallUNKNOWN());
		this.circuitGrid.setWidget(0, 2, this.gateA1Image);
		this.gateA2Image = new Image(this.resources.smallUNKNOWN());
		this.circuitGrid.setWidget(2, 2, this.gateA2Image);
		this.gateA3Image = new Image(this.resources.smallUNKNOWN());
		this.circuitGrid.setWidget(4, 2, this.gateA3Image);

		// Gates (level B)
		this.gateB1Image = new Image(this.resources.smallUNKNOWN());
		this.circuitGrid.setWidget(1, 4, this.gateB1Image);
		this.gateB2Image = new Image(this.resources.smallUNKNOWN());
		this.circuitGrid.setWidget(3, 4, this.gateB2Image);

		// Gates (level C)
		this.gateC1Image = new Image(this.resources.smallUNKNOWN());
		this.circuitGrid.setWidget(2, 6, this.gateC1Image);
		
		// Connections
		for(final RowColumnPair pair : RowColumnPair.getRowsColumnPairs()){
		    final Image pairImage = new Image(pair.getImageResourceMobile(this.resources));
		    this.circuitGrid.setWidget(pair.getRow(), pair.getColumn() + 1, pairImage);
		}
		
		// Setting the Unknown Gate
		this.unknownGateImage = this.gateA2Image;
		this.unknownGateImage.addStyleName(Style.LOGIC_MOUSE_POINTER_HAND);
		this.changeUnknownGateDialogBox = new MobileChangeUnknownGateDialogBox(this);
		
		this.circuitPanel.setCellHorizontalAlignment(this.circuitGrid, HasHorizontalAlignment.ALIGN_RIGHT);
		this.circuitPanel.setCellVerticalAlignment(webcamWidget, HasVerticalAlignment.ALIGN_MIDDLE);
		this.circuitPanel.setCellHorizontalAlignment(webcamWidget, HasHorizontalAlignment.ALIGN_LEFT);
		this.removableWidgetsPanel.add(this.circuitPanel);
		
		// Messages
		this.messages = new WlWaitingLabel("Receiving the circuit");
		this.messages.start();
		this.removableWidgetsPanel.add(this.messages.getWidget());
		
		// Send Solution button
		this.sendSolutionButton = new Button(i18n.sendSolution());
		this.sendSolutionButton.setEnabled(false);
		this.sendSolutionButton.addClickHandler(new ClickHandler(){

		    @Override
		    public void onClick(ClickEvent event) {
			MobileLogicExperiment.this.sendCommand(new SolveCircuitCommand(MobileLogicExperiment.this.circuit));
			MobileLogicExperiment.this.messages.setText("Sending solution");
			MobileLogicExperiment.this.messages.start();
		    }
		});
		this.removableWidgetsPanel.add(this.sendSolutionButton);

		this.sendCommand(new GetCircuitCommand());
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

	@Override
	public boolean expectsPostEnd(){
		return true;
	}

	@Override
	public void postEnd(String initialData, String endData){
		if(endData == null){
			this.messages.setText("Finished. Waiting for your punctuation...");
		}else{
			this.messages.setText("Finished. Your punctuation: " + endData);
			this.widget.add(new HTML("Check the ranking <a href=\"" + WebLabClient.baseLocation + "/weblab/admin/winners.py\">here</a>"));
		}
	}
	
	private int getWebcamRefreshingTime() {
		return this.configurationRetriever.getIntProperty(
			MobileLogicExperiment.LOGIC_WEBCAM_REFRESH_TIME_PROPERTY, 
			MobileLogicExperiment.DEFAULT_LOGIC_WEBCAM_REFRESH_TIME
			);
	}

	private void sendCommand(Command command){
		this.lastCommand = command;
		this.boardController.sendCommand(command, this.commandCallback);
	}
	
	private void processCommandSent(ResponseCommand responseCommand){
		if ( this.lastCommand instanceof GetCircuitCommand ){
			this.messages.stop();
			this.messages.setText("");
			final CircuitParser circuitParser = new CircuitParser();
			try {
				this.circuit = circuitParser.parseCircuit(responseCommand.getCommandString());
			} catch (final InvalidCircuitException e) {
				this.messages.setText("Invalid Circuit received: " + e.getMessage());
				return;
			}
			this.sendSolutionButton.setEnabled(false);
			this.updateCircuitGrid();
		} else if ( this.lastCommand instanceof SolveCircuitCommand ) {
			this.messages.stop();

			if(responseCommand.getCommandString().startsWith("FAIL")){
				this.solving = false;
				this.messages.setText(i18n.wrongOneGameOver(this.points));
				this.sendSolutionButton.setEnabled(false);
			}else if(responseCommand.getCommandString().startsWith("OK")){
				this.points++;
				this.messages.setText(i18n.wellDone1point());
				turnOnLight();
				final Timer sleepTimer = new Timer(){

					@Override
					public void run() {
						MobileLogicExperiment.this.sendCommand(new GetCircuitCommand());
						turnOffLight();
					}};
				sleepTimer.schedule(2000);
			}
		}else{
			// TODO: Unknown command!
		}
	}
	
	void turnOffLight() {
		this.light.setUrl(GWT.getModuleBaseURL() + "/img/bulb_off.png");
	}
	
	void turnOnLight() {
		this.light.setUrl(GWT.getModuleBaseURL() + "/img/bulb_on.png");
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
	    
	    this.circuitGrid.setWidget(2, 6, new Image(this.getURL(gateC1.getOperation())));
	    this.circuitGrid.setWidget(1, 4, new Image(this.getURL(gateB1.getOperation())));
	    this.circuitGrid.setWidget(3, 4, new Image(this.getURL(gateB2.getOperation())));
	    this.circuitGrid.setWidget(0, 2, new Image(this.getURL(gateA1.getOperation())));
	    this.circuitGrid.setWidget(2, 2, new Image(this.getURL(gateA2.getOperation())));
	    this.circuitGrid.setWidget(4, 2, new Image(this.getURL(gateA3.getOperation())));
	    
	    this.input1Label.setHTML(this.getFormatedInputLabel(switch1.turned?this.oneString:this.zeroString, 1));
	    this.input2Label.setHTML(this.getFormatedInputLabel(switch2.turned?this.oneString:this.zeroString, 2));
	    this.input3Label.setHTML(this.getFormatedInputLabel(switch3.turned?this.oneString:this.zeroString, 3));
	    this.input4Label.setHTML(this.getFormatedInputLabel(switch4.turned?this.oneString:this.zeroString, 4));
	    
	    this.setUnknownGate(this.resources.smallUNKNOWN());
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
