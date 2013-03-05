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

import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.Widget;

import es.deusto.weblab.client.HistoryProperties;
import es.deusto.weblab.client.configuration.IConfigurationRetriever;
import es.deusto.weblab.client.lab.experiments.IBoardBaseController;
import es.deusto.weblab.client.lab.experiments.IDisposableWidgetsContainer;
import es.deusto.weblab.client.lab.experiments.UIExperimentBase;
import es.deusto.weblab.client.ui.widgets.IWlDisposableWidget;

public class AquariumExperiment extends UIExperimentBase {

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
		
		if (widgetName != null) {
			
			// If so, identify which widget must be shown
			if (widgetName.equals("ball1")) {
				widget = new Label("ball1");
			} else if (widgetName.equals("ball2")){
				widget = new Label("ball2");
			} else if (widgetName.equals("ball3")){
				widget = new Label("ball3");
			} else if (widgetName.equals("camera")){
				widget = new Label("camera");
			}

			// If a widget is shown, wrap it and put it
			if (widget != null) {
				// This class basically provides the time management, common to all the widgets
				final WidgetContainerPanel containerPanel = new WidgetContainerPanel(widget, time);
				putWidget(containerPanel);
				disposableContainer = containerPanel;
			}
		}
		
		// If there was no identified widget (or no widget mode), load the regular main panel
		if (widget == null) {
			final MainPanel mainPanel = new MainPanel(this.boardController, this.configurationRetriever, time, initialConfiguration);
			putWidget(mainPanel);
			disposableContainer = mainPanel;
		}
		
		// Append all the disposable widgets
		if(disposableContainer != null)
			for(IWlDisposableWidget disposableWidget : disposableContainer.getDisposableWidgets()) 
				addDisposableWidgets(disposableWidget);
	}
}
