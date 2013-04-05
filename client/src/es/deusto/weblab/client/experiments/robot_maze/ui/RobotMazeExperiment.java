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
package es.deusto.weblab.client.experiments.robot_maze.ui;

import com.google.gwt.json.client.JSONParser;
import com.google.gwt.user.client.Event;

import es.deusto.weblab.client.configuration.IConfigurationRetriever;
import es.deusto.weblab.client.lab.experiments.IBoardBaseController;
import es.deusto.weblab.client.lab.experiments.UIExperimentBase;
import es.deusto.weblab.client.ui.widgets.IWlDisposableWidget;

public class RobotMazeExperiment extends UIExperimentBase {

	public RobotMazeExperiment(IConfigurationRetriever configurationRetriever, IBoardBaseController commandSender) {
		super(configurationRetriever, commandSender);
	}

	/**
	 * The initialize function gets called on the "reserve" stage,
	 * before the experiment starts.
	 */
	@Override
	public void initialize(){
		putWidget(new InitialPanel());
	}	
	
	
	/**
	 * This function gets called just when the actual experiment starts, after
	 * the reserve is done and the queue is over.
	 */
	@Override
	public void start(int time, String initialConfiguration) {
		
		// Create the control panel
		final ControlPanel panel = new ControlPanel(this.boardController, this.configurationRetriever, JSONParser.parseStrict(initialConfiguration).isObject(), time);
		putWidget(panel);
		
		// Add and activate the keyboard handler
		final InternalNativePreviewHandler handler = new InternalNativePreviewHandler(panel);
		Event.addNativePreviewHandler(handler);
		handler.activate();
		
		// Add disposable widgets
		addDisposableWidgets(handler);
		
		for(IWlDisposableWidget disposableWidget : panel.getDisposableWidgets())
			addDisposableWidgets(disposableWidget);
	}	
}
