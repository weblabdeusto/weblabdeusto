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

import com.google.gwt.json.client.JSONArray;
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
		// 
		// When asked to submit information to the server, retrieve information from the initialization panel
		// 
		if(this.initializationPanel == null)
			return null;
		final String exercise = this.initializationPanel.getInitialExcercise();
		final JSONObject object = new JSONObject();
		object.put("exercise", new JSONString(exercise));
		return object;
	}
	
	@Override
	public void queued(){
		// 
		// Do not show anything while queued
		// 
		putWidget(new VerticalPanel());
	}
	
    @Override
    public void start(int time, String initialConfiguration) {
    	// 
    	// initialConfiguration is a JSON-encoded object returned directly by an assigned server
    	// An example would be: 
    	// {
    	//      "webcam"      : "http://...",
    	//      "mjpeg"       : "http://...",
    	//      "mjpegWidth"  : 320, 
    	//      "mjpegHeight" : 240, 
    	//      "labels"      : ["label1", "label2", "label3"],
    	// }
    	// 
    	
    	
    	final JSONValue value = JSONParser.parseStrict(initialConfiguration);
    	final JSONObject obj = (JSONObject)value;
    	
    	// 
    	// Retrieve labels
    	final JSONArray arr = obj.get("labels").isArray();
    	final String [] labels = new String[arr.size()];
    	for(int i = 0; i < arr.size(); ++i)
    		labels[i] = arr.get(i).isString().stringValue();
    	
		final MainPanel mainPanel = new MainPanel(this.boardController, labels);
		
		// 
		// Configure the camera
		final WlWebcam camera = mainPanel.getWebcam();
		camera.configureWebcam(obj);
		camera.start();
		addDisposableWidgets(camera);
		
		//
		// Configure the timer
		final WlTimer timer = mainPanel.getTimer();
		timer.updateTime(time);
		addDisposableWidgets(timer);
		
		putWidget(mainPanel);
    }
}
