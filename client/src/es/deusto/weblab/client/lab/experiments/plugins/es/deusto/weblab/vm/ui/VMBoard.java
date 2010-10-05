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
package es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.vm.ui;

import java.util.HashMap;
import java.util.Map;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
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

import es.deusto.weblab.client.comm.exceptions.WlCommException;
import es.deusto.weblab.client.configuration.IConfigurationManager;
import es.deusto.weblab.client.dto.experiments.Command;
import es.deusto.weblab.client.dto.experiments.ResponseCommand;
import es.deusto.weblab.client.lab.comm.callbacks.IResponseCommandCallback;
import es.deusto.weblab.client.lab.experiments.commands.RequestWebcamCommand;
import es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.logic.circuit.Circuit;
import es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.logic.circuit.CircuitParser;
import es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.logic.circuit.Gate;
import es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.logic.circuit.InvalidCircuitException;
import es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.logic.circuit.Operation;
import es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.logic.circuit.Switch;
import es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.logic.commands.GetCircuitCommand;
import es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.logic.commands.SolveCircuitCommand;
import es.deusto.weblab.client.lab.ui.BoardBase;
import es.deusto.weblab.client.ui.widgets.EasyGrid;
import es.deusto.weblab.client.ui.widgets.WlTimer;
import es.deusto.weblab.client.ui.widgets.WlWaitingLabel;
import es.deusto.weblab.client.ui.widgets.WlWebcam;
import es.deusto.weblab.client.ui.widgets.WlTimer.IWlTimerFinishedCallback;

public class VMBoard extends BoardBase {
	
	/******************
	 * UIBINDER RELATED
	 ******************/
	
	interface VMBoardUiBinder extends UiBinder<Widget, VMBoard> {
	}

	private static final VMBoardUiBinder uiBinder = GWT.create(VMBoardUiBinder.class);
	

	public static class Style   {
		public static final String TIME_REMAINING          = "wl-time_remaining";
		public static final String CLOCK_ACTIVATION_PANEL  = "wl-clock_activation_panel"; 
		public static final String LOGIC_INPUT_VALUE_LABEL = "logic-input-value-label"; 
		public static final String LOGIC_MOUSE_POINTER_HAND = "logic-mouse-pointer-hand";
	}

	private final IConfigurationManager configurationManager;
	
	// Root panel.
	@UiField VerticalPanel widget;
	
	
	public VMBoard(IConfigurationManager configurationManager, IBoardBaseController commandSender) {
		super(commandSender);
		
		this.configurationManager = configurationManager;
		
		this.createProvidedWidgets();
		
		VMBoard.uiBinder.createAndBindUi(this);
	}
	
	/* Creates those widgets that are placed through UiBinder but
	 * whose ctors need to take certain parameters and hence be
	 * instanced in code.
	 */
	private void createProvidedWidgets() {
		
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
	public void start() {
		
	    this.widget.setVisible(true);
	}	
	
	@Override
	public void setTime(int time) {
		//this.timer.updateTime(time);
	}

	@Override
	public Widget getWidget() {
		return this.widget;
	}

	@Override
	public void end() {
	}
	
	private void sendCommand(Command command){
		//this.boardController.sendCommand(command, this.commandCallback);
	}
	
}
