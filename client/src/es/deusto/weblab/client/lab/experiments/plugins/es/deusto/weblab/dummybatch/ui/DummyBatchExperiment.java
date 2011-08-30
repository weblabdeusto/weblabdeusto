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
package es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.dummybatch.ui;

import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;

import es.deusto.weblab.client.configuration.IConfigurationRetriever;
import es.deusto.weblab.client.lab.experiments.ExperimentBase;

public class DummyBatchExperiment extends ExperimentBase {

	public static final String DUMMY_WEBCAM_IMAGE_URL_PROPERTY = "es.deusto.weblab.dummy.webcam.image.url";
	public static final String DEFAULT_DUMMY_WEBCAM_IMAGE_URL       = "http://fpga.weblab.deusto.es/webcam/fpga0/image.jpg";
	
	public static final String DUMMY_WEBCAM_REFRESH_TIME_PROPERTY = "es.deusto.weblab.pld.webcam.refresh.millis";
	public static final int    DEFAULT_DUMMY_WEBCAM_REFRESH_TIME       = 400;
	
	@SuppressWarnings("unused")
	private final IConfigurationRetriever configurationRetriever;
	
	private VerticalPanel verticalPanel = new VerticalPanel();
	
	public DummyBatchExperiment(IConfigurationRetriever configurationRetriever,
			IBoardBaseController boardController) {
		super(boardController);
		this.configurationRetriever = configurationRetriever;
	    print("Instance created");
	}
	
	@Override
	public void start(int time, String initialConfiguration){
	    print("initial configuration:" + initialConfiguration);
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
	public void setTime(int time) {
	    print("time:" + time);
	}
}
