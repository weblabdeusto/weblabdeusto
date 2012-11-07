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
package es.deusto.weblab.client.experiments.binary.ui;

import com.google.gwt.json.client.JSONObject;
import com.google.gwt.json.client.JSONParser;
import com.google.gwt.json.client.JSONString;
import com.google.gwt.json.client.JSONValue;
import com.google.gwt.user.client.ui.VerticalPanel;

import es.deusto.weblab.client.configuration.IConfigurationRetriever;
import es.deusto.weblab.client.lab.experiments.IBoardBaseController;
import es.deusto.weblab.client.lab.experiments.UIExperimentBase;
import es.deusto.weblab.client.ui.widgets.WlTimer;
import es.deusto.weblab.client.ui.widgets.WlWebcam;

public class BinaryExperiment extends UIExperimentBase {

	private InitializationPanel initializationPanel = null;
	
	public BinaryExperiment(IConfigurationRetriever configurationRetriever, IBoardBaseController boardController){
		super(configurationRetriever, boardController);
	}
	
	@Override
	public void initialize(){
		this.initializationPanel = new InitializationPanel();
		putWidget(this.initializationPanel);
	}
	
	@Override
	public JSONValue getInitialData() {
		if(this.initializationPanel == null)
			return null;
		final String exercise = this.initializationPanel.getInitialExcercise();
		final JSONObject object = new JSONObject();
		object.put("exercise", new JSONString(exercise));
		return object;
	}
	
	@Override
	public void queued(){
		// Do not show anything
		putWidget(new VerticalPanel());
	}
	
    @Override
    public void start(int time, String initialConfiguration) {
    	final JSONValue value = JSONParser.parseStrict(initialConfiguration);
    	
		final BinaryMainPanel mainPanel = new BinaryMainPanel();
		
		final WlWebcam camera = mainPanel.getWebcam();
		camera.configureWebcam((JSONObject)value);
		camera.start();
		addDisposableWidgets(camera);
		
		final WlTimer timer = mainPanel.getTimer();
		timer.updateTime(time);
		addDisposableWidgets(timer);
		
		putWidget(mainPanel);
    }
}
