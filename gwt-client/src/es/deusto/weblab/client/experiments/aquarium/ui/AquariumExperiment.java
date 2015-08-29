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
* Author: Pablo Orduña <pablo.orduna@deusto.es>
* 		  
*/ 
package es.deusto.weblab.client.experiments.aquarium.ui;

import com.google.gwt.json.client.JSONObject;
import com.google.gwt.json.client.JSONParser;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.Widget;

import es.deusto.weblab.client.HistoryProperties;
import es.deusto.weblab.client.configuration.IConfigurationRetriever;
import es.deusto.weblab.client.lab.experiments.IBoardBaseController;
import es.deusto.weblab.client.lab.experiments.IDisposableWidgetsContainer;
import es.deusto.weblab.client.lab.experiments.UIExperimentBase;
import es.deusto.weblab.client.ui.widgets.IWlDisposableWidget;

public class AquariumExperiment extends UIExperimentBase {

	private IStatusUpdatable statusUpdatable;
	
	public AquariumExperiment(IConfigurationRetriever configurationRetriever, IBoardBaseController commandSender) {
		super(configurationRetriever, commandSender);
	}
	
	/**
	 * This function gets called just when the actual experiment starts, after
	 * the reserve is done and the queue is over.
	 */
	@Override
	public void start(int time, String initialConfiguration) {
		
		IDisposableWidgetsContainer disposableContainer = null;

		// Check if we're in widget mode
		final String widgetName = HistoryProperties.getValue(HistoryProperties.WIDGET, null);
		Widget widget = null;
		
		final JSONObject initialStatusObj = JSONParser.parseStrict(initialConfiguration).isObject().get("status").isObject();
		final Status initialStatus = new Status(initialStatusObj);
		
		if (widgetName != null) {
			
			// If so, identify which widget must be shown
			if (widgetName.equals("ball-blue")) {
				widget = new BallPanel(Color.blue);
			} else if (widgetName.equals("ball-white")){
				widget = new BallPanel(Color.white);
			} else if (widgetName.equals("ball-yellow")){
				widget = new BallPanel(Color.yellow);
			} else if (widgetName.equals("ball-red")){
				widget = new BallPanel(Color.red);
			} else if (widgetName.equals("camera")){
				final WebcamPanel webcam = new WebcamPanel(this.configurationRetriever, initialConfiguration);
				webcam.start();
				widget = webcam;
			} else if (widgetName.equals("camera1")) {
				final SingleWebcamPanel webcam = new SingleWebcamPanel(this.configurationRetriever, initialConfiguration, 1);
				webcam.start();
				widget = webcam;
			} else if (widgetName.equals("camera2")) {
				final SingleWebcamPanel webcam = new SingleWebcamPanel(this.configurationRetriever, initialConfiguration, 2);
				webcam.start();
				widget = webcam;
			}
			
			System.out.println("Widget is: " + widget);

			// If a widget is shown, wrap it and put it
			if (widget != null) {
				// This class basically provides the time management, common to all the widgets
				final WidgetContainerPanel containerPanel = new WidgetContainerPanel(widget, time);
				putWidget(containerPanel);
				disposableContainer = containerPanel;
				this.statusUpdatable = containerPanel;
				
				if(widget instanceof BallPanel) {
					final BallPanel ballPanel = (BallPanel)widget;
					ballPanel.setGlobalUpdater(this.statusUpdatable);
					ballPanel.setBoardController(this.boardController);
				}
			}
		}
		
		// If there was no identified widget (or no widget mode), load the regular main panel
		if (widget == null) {
			final MainPanel mainPanel = new MainPanel(this.boardController, this.configurationRetriever, time, initialConfiguration, initialStatus);
			putWidget(mainPanel);
			disposableContainer = mainPanel;
			this.statusUpdatable = mainPanel;
		}
		
		// Append all the disposable widgets
		if(disposableContainer != null)
			for(IWlDisposableWidget disposableWidget : disposableContainer.getDisposableWidgets()) 
				addDisposableWidgets(disposableWidget);
		
		final StatusUpdater updater = new StatusUpdater(2500, this.boardController, this);
		addDisposableWidgets(updater);
		
		this.statusUpdatable.updateStatus(initialStatus);
	}
	
	void updateStatus(Status status) {
		this.statusUpdatable.updateStatus(status);
	}

	public void setMessage(String msg) {
		if (msg.contains("Current user")) { // Fail since other widget failed
			this.boardController.clean();
			return;
		}
		Window.alert(msg);
	}
}
