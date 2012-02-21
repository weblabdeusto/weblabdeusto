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
package es.deusto.weblab.client.experiments.dummybatch.ui;

import com.google.gwt.json.client.JSONBoolean;
import com.google.gwt.json.client.JSONObject;
import com.google.gwt.json.client.JSONValue;
import com.google.gwt.user.client.ui.CheckBox;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;

import es.deusto.weblab.client.configuration.IConfigurationRetriever;
import es.deusto.weblab.client.lab.experiments.ExperimentBase;
import es.deusto.weblab.client.lab.experiments.IBoardBaseController;

public class DummyBatchExperiment extends ExperimentBase {

	public static final String DUMMY_WEBCAM_IMAGE_URL_PROPERTY = "es.deusto.weblab.dummy.webcam.image.url";
	public static final String DEFAULT_DUMMY_WEBCAM_IMAGE_URL       = "http://fpga.weblab.deusto.es/webcam/fpga0/image.jpg";
	
	public static final String DUMMY_WEBCAM_REFRESH_TIME_PROPERTY = "es.deusto.weblab.pld.webcam.refresh.millis";
	public static final int    DEFAULT_DUMMY_WEBCAM_REFRESH_TIME       = 400;
	
	private VerticalPanel verticalPanel = new VerticalPanel();
	private CheckBox batchCheckBox = new CheckBox("Batch (finish when just started)");
	private CheckBox earlyFinishCheckBox = new CheckBox("Early finish (before assigned time)");
	private CheckBox longFinishCheckBox = new CheckBox("Long finish (wait for some time)");
	
	public DummyBatchExperiment(IConfigurationRetriever configurationRetriever,
			IBoardBaseController boardController) {
		super(configurationRetriever, boardController);
		this.verticalPanel.add(this.batchCheckBox);
		this.verticalPanel.add(this.earlyFinishCheckBox);
		this.verticalPanel.add(this.longFinishCheckBox);
	    print("Instance created");
	}
	
	@Override
	public JSONValue getInitialData(){
		final JSONObject data = new JSONObject();
		data.put("batch", JSONBoolean.getInstance(this.batchCheckBox.getValue()));
		data.put("early_finish", JSONBoolean.getInstance(this.earlyFinishCheckBox.getValue()));
		data.put("long_finish", JSONBoolean.getInstance(this.longFinishCheckBox.getValue()));
		
		this.batchCheckBox.setEnabled(false);
		this.earlyFinishCheckBox.setEnabled(false);
		this.longFinishCheckBox.setEnabled(false);
		
		return data;
	}
	
	@Override
	public void start(int time, String initialConfiguration){
	    print("Initial data:" + initialConfiguration);
	    print("Assigned time (seconds):" + time);
	}
	
	private void print(String message){
		System.out.println(message);
		this.verticalPanel.add(new Label(message));
	}
	
	@Override
	public Widget getWidget() {
		return this.verticalPanel;
	}

	@Override
	public void end() {
	    print("end.");
	}
	
	@Override
	public void postEnd(String initialData, String endData){
		print("Post end initial: " + initialData);
		print("Post end end: " + endData);
	}
	
	@Override
	public boolean expectsPostEnd(){
		return true;
	}

	@Override
	public void setTime(int time) {
	    print("Assigned time (seconds):" + time);
	}
}
