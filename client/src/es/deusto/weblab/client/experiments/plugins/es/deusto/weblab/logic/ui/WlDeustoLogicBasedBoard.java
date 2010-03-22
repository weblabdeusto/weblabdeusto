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
*
*/ 
package es.deusto.weblab.client.experiments.plugins.es.deusto.weblab.logic.ui;

import java.util.HashMap;
import java.util.Map;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.user.client.Timer;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.DialogBox;
import com.google.gwt.user.client.ui.Grid;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.HasHorizontalAlignment;
import com.google.gwt.user.client.ui.HasVerticalAlignment;
import com.google.gwt.user.client.ui.Image;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.Widget;

import es.deusto.weblab.client.comm.callbacks.IResponseCommandCallback;
import es.deusto.weblab.client.configuration.IConfigurationManager;
import es.deusto.weblab.client.dto.experiments.Command;
import es.deusto.weblab.client.dto.experiments.ResponseCommand;
import es.deusto.weblab.client.exceptions.comm.WlCommException;
import es.deusto.weblab.client.experiments.plugins.es.deusto.weblab.gpib.ui.WlDeustoGpibBoard;
import es.deusto.weblab.client.experiments.plugins.es.deusto.weblab.logic.circuit.Circuit;
import es.deusto.weblab.client.experiments.plugins.es.deusto.weblab.logic.circuit.CircuitParser;
import es.deusto.weblab.client.experiments.plugins.es.deusto.weblab.logic.circuit.Gate;
import es.deusto.weblab.client.experiments.plugins.es.deusto.weblab.logic.circuit.InvalidCircuitException;
import es.deusto.weblab.client.experiments.plugins.es.deusto.weblab.logic.circuit.Operation;
import es.deusto.weblab.client.experiments.plugins.es.deusto.weblab.logic.circuit.Switch;
import es.deusto.weblab.client.experiments.plugins.es.deusto.weblab.logic.commands.GetCircuitCommand;
import es.deusto.weblab.client.experiments.plugins.es.deusto.weblab.logic.commands.SolveCircuitCommand;
import es.deusto.weblab.client.ui.BoardBase;
import es.deusto.weblab.client.ui.widgets.WlHorizontalPanel;
import es.deusto.weblab.client.ui.widgets.WlTimer;
import es.deusto.weblab.client.ui.widgets.WlVerticalPanel;
import es.deusto.weblab.client.ui.widgets.WlWaitingLabel;
import es.deusto.weblab.client.ui.widgets.WlWebcam;
import es.deusto.weblab.client.ui.widgets.WlTimer.IWlTimerFinishedCallback;

public class WlDeustoLogicBasedBoard extends BoardBase {

	public static final String LOGIC_WEBCAM_IMAGE_URL_PROPERTY = "es.deusto.weblab.logic.webcam.image.url";
	public static final String DEFAULT_LOGIC_WEBCAM_IMAGE_URL = GWT.isScript() ? "https://www.weblab.deusto.es/webcam/logic0/image.jpg?size=2" : "";
	
	private static final String LOGIC_WEBCAM_REFRESH_TIME_PROPERTY = "es.deusto.weblab.logic.webcam.refresh.millis";
	private static final int DEFAULT_LOGIC_WEBCAM_REFRESH_TIME = 400;
	
	public static class Style{
		public static final String TIME_REMAINING          = "wl-time_remaining";
		public static final String CLOCK_ACTIVATION_PANEL  = "wl-clock_activation_panel"; 
		public static final String LOGIC_INPUT_VALUE_LABEL = "logic-input-value-label"; 
		public static final String LOGIC_MOUSE_POINTER_HAND = "logic-mouse-pointer-hand";
	}

	private final IConfigurationManager configurationManager;
	private final Map<Operation, String> operation2url = new HashMap<Operation, String>();
	private final Map<String, Operation> url2operation = new HashMap<String, Operation>();
	private final String unknownOperationUrl = GWT.getModuleBaseURL() + "img/logic/UNKNOWN.png";
	
	private final String zeroString = "0";
	private final String oneString  = "1";
	
	// Widgets
	private final WlVerticalPanel widget;
	private final WlVerticalPanel removableWidgetsPanel;
	private WlHorizontalPanel circuitAndWebcamPanel;
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
	private Label referenceToShowBoxesLabel = new Label("");
	
	// DTOs
	private Command lastCommand;
	private Circuit circuit;
	private boolean solving = true;
	private int points = 0;
	
	private IResponseCommandCallback commandCallback = new IResponseCommandCallback(){

	    public void onSuccess(ResponseCommand responseCommand) {
		WlDeustoLogicBasedBoard.this.processCommandSent(responseCommand);		    
	    }

	    public void onFailure(WlCommException e) {
		WlDeustoLogicBasedBoard.this.messages.setText("Error: " + e.getMessage() + ". Please, notify the WebLab-Deusto administrators at weblab@deusto.es about this error.");
	    }
	};
	
	public WlDeustoLogicBasedBoard(IConfigurationManager configurationManager, IBoardBaseController commandSender) {
		super(commandSender);
		
		this.fillMaps();
		
		this.configurationManager = configurationManager;
		
		this.widget = new WlVerticalPanel();
		this.widget.setWidth("100%");
		this.widget.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
		
		this.removableWidgetsPanel = new WlVerticalPanel();
		this.removableWidgetsPanel.setWidth("100%");
		this.removableWidgetsPanel.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
		this.removableWidgetsPanel.setSpacing(20);
	}
	
	private void fillMaps(){
	    this.operation2url.put(Operation.AND,  GWT.getModuleBaseURL() + "img/logic/AND.png");
	    this.operation2url.put(Operation.NAND, GWT.getModuleBaseURL() + "img/logic/NAND.png");
	    this.operation2url.put(Operation.OR,   GWT.getModuleBaseURL() + "img/logic/OR.png");
	    this.operation2url.put(Operation.NOR,  GWT.getModuleBaseURL() + "img/logic/NOR.png");
	    this.operation2url.put(Operation.XOR,  GWT.getModuleBaseURL() + "img/logic/XOR.png");
	    
	    for(Operation op : this.operation2url.keySet())
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

	@Override
	public void initialize(){
		this.removableWidgetsPanel.add(new Label("Welcome to the WebLab-Deusto Logic Game!"));
		this.removableWidgetsPanel.add(new Label("Replace the unknown door with the correct one so the LED turns on."));
		this.removableWidgetsPanel.add(new Label("Solve as many circuits as possible to get more points and become the champion!"));
		
		this.widget.add(this.removableWidgetsPanel);
	}	
	
	@Override
	public void queued(){
	    	this.widget.setVisible(false);
	}	
	
	@Override
	public void start() {
	    	this.points = 0;
	    	this.widget.setVisible(true);
		
		while(this.removableWidgetsPanel.getWidgetCount() > 0)
		    this.removableWidgetsPanel.remove(0);

		// Timer
		this.timer = new WlTimer();
		this.timer.setStyleName(WlDeustoGpibBoard.Style.TIME_REMAINING);
		this.timer.getWidget().setWidth("30%");
		this.timer.setTimerFinishedCallback(new IWlTimerFinishedCallback(){
			public void onFinished() {
			    WlDeustoLogicBasedBoard.this.boardController.onClean();
			}
		});
		this.removableWidgetsPanel.add(this.timer.getWidget());		

		// Horizontal Panel
		this.circuitAndWebcamPanel = new WlHorizontalPanel();
		this.circuitAndWebcamPanel.setWidth("100%");
		this.circuitAndWebcamPanel.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
		
		this.circuitAndWebcamPanel.add(this.referenceToShowBoxesLabel);
		
		// Circuit
		this.circuitGrid = new Grid(5, 8);
		this.circuitGrid.setBorderWidth(0);
		this.circuitAndWebcamPanel.add(this.circuitGrid);
		
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
		for(RowColumnPair pair : RowColumnPair.getRowsColumnPairs()){
		    final Image pairImage = new Image(pair.getImageResourceWeb());
		    this.circuitGrid.setWidget(pair.getRow(), pair.getColumn() + 1, pairImage);
		}
		
		// Setting the Unknown Gate
		this.unknownGateImage = this.gateA2Image;
		this.unknownGateImage.addStyleName(Style.LOGIC_MOUSE_POINTER_HAND);
		this.changeUnknownGateDialogBox = new ChangeUnknownGateDialogBox(this);
		this.unknownGateImage.addClickHandler(new ClickHandler(){
		    @Override
		    public void onClick(ClickEvent event) {
			if(WlDeustoLogicBasedBoard.this.solving)
			    //WlDeustoLogicBasedBoard.this.changeUnknownGateDialogBox.show();
			    WlDeustoLogicBasedBoard.this.changeUnknownGateDialogBox.showRelativeTo(WlDeustoLogicBasedBoard.this.referenceToShowBoxesLabel);
			
		    }
		});
		
		// Webcam
    		this.webcam = new WlWebcam(this.getWebcamRefreshingTime(), this.getWebcamImageUrl());
    		this.webcam.start();
		this.circuitAndWebcamPanel.add(this.webcam.getWidget());

		this.circuitAndWebcamPanel.setCellHorizontalAlignment(this.circuitGrid, HasHorizontalAlignment.ALIGN_RIGHT);
		this.circuitAndWebcamPanel.setCellVerticalAlignment(this.webcam.getWidget(), HasVerticalAlignment.ALIGN_MIDDLE);
		this.circuitAndWebcamPanel.setCellHorizontalAlignment(this.webcam.getWidget(), HasHorizontalAlignment.ALIGN_LEFT);
		this.removableWidgetsPanel.add(this.circuitAndWebcamPanel);
		
		// Messages
		this.messages = new WlWaitingLabel("Receiving the circuit");
		this.messages.start();
		this.removableWidgetsPanel.add(this.messages.getWidget());
		
		// Send Solution button
		this.sendSolutionButton = new Button("Send Solution");
		this.sendSolutionButton.setEnabled(false);
		this.sendSolutionButton.addClickHandler(new ClickHandler(){

		    @Override
		    public void onClick(ClickEvent event) {
			WlDeustoLogicBasedBoard.this.sendCommand(new SolveCircuitCommand(WlDeustoLogicBasedBoard.this.circuit));
			WlDeustoLogicBasedBoard.this.messages.setText("Sending solution");
			WlDeustoLogicBasedBoard.this.messages.start();
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
			this.webcam.dispose();
			this.webcam = null;
		}	
		if(this.timer != null){
			this.timer.dispose();
			this.timer = null;
		}
		if(this.messages != null){
			this.messages.dispose();
			this.messages = null;
		}
	}
	
	private String getWebcamImageUrl() {
		return this.configurationManager.getProperty(
			WlDeustoLogicBasedBoard.LOGIC_WEBCAM_IMAGE_URL_PROPERTY, 
				this.getDefaultWebcamImageUrl()
			);
	}
	
	protected String getDefaultWebcamImageUrl(){
		return WlDeustoLogicBasedBoard.DEFAULT_LOGIC_WEBCAM_IMAGE_URL;
	}

	private int getWebcamRefreshingTime() {
		return this.configurationManager.getIntProperty(
			WlDeustoLogicBasedBoard.LOGIC_WEBCAM_REFRESH_TIME_PROPERTY, 
			WlDeustoLogicBasedBoard.DEFAULT_LOGIC_WEBCAM_REFRESH_TIME
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
		    } catch (InvalidCircuitException e) {
			this.messages.setText("Invalid Circuit received: " + e.getMessage());
			return;
		    }
            this.sendSolutionButton.setEnabled(false);
		    this.updateCircuitGrid();
	    	} else if ( this.lastCommand instanceof SolveCircuitCommand ) {
	    	    this.messages.stop();
	    	    
	    	    if(responseCommand.getCommandString().startsWith("FAIL")){
	    		this.solving = false;
	    		this.messages.setText("Wrong one! Game over. Total points: " + this.points);
	    		this.sendSolutionButton.setEnabled(false);
	    	    }else if(responseCommand.getCommandString().startsWith("OK")){
	    		this.points++;
	    		this.messages.setText("Well done! 1 point. Let's see the next one!");
	    		Timer sleepTimer = new Timer(){

			    @Override
			    public void run() {
				WlDeustoLogicBasedBoard.this.sendCommand(new GetCircuitCommand());
			    }};
	    		sleepTimer.schedule(2000);
	    	    }
	    	    
		}else{
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
