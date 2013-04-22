/*
* Copyright (C) 2012 onwards University of Deusto
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

import com.google.gwt.core.client.GWT;
import com.google.gwt.json.client.JSONObject;
import com.google.gwt.json.client.JSONParser;
import com.google.gwt.json.client.JSONValue;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.Widget;

import es.deusto.weblab.client.configuration.IConfigurationRetriever;
import es.deusto.weblab.client.lab.experiments.IDisposableWidgetsContainer;
import es.deusto.weblab.client.ui.widgets.IWlDisposableWidget;
import es.deusto.weblab.client.ui.widgets.WlWebcam;

public class WebcamPanel extends Composite implements IDisposableWidgetsContainer {

	private static WebcamPanelUiBinder uiBinder = GWT.create(WebcamPanelUiBinder.class);

	@UiField(provided=true) WlWebcam webcam1;
	@UiField(provided=true) WlWebcam webcam2;
	
	private static final String WEBCAM_REFRESH_TIME_PROPERTY   = "webcam.refresh.millis";
	private static final int    DEFAULT_WEBCAM_REFRESH_TIME    = 200;
	
	private IConfigurationRetriever configurationRetriever;
	
	interface WebcamPanelUiBinder extends UiBinder<Widget, WebcamPanel> {
	}
	
	public WebcamPanel(IConfigurationRetriever configurationRetriever, String initialConfiguration) {
		
		this.configurationRetriever = configurationRetriever;
		
		this.webcam1 = GWT.create(WlWebcam.class);
		this.webcam1.setTime(getWebcamRefreshingTime());
		this.webcam2 = GWT.create(WlWebcam.class);
		this.webcam2. setTime(getWebcamRefreshingTime());
		initWidget(uiBinder.createAndBindUi(this));
		
		parseWebcamConfig(initialConfiguration);
	}
	
	public void start() {
		this.webcam1.start();
		this.webcam2.start();
	}
	
	private int getWebcamRefreshingTime() {
		return this.configurationRetriever.getIntProperty(WEBCAM_REFRESH_TIME_PROPERTY, DEFAULT_WEBCAM_REFRESH_TIME);
	}	
	

	private void parseWebcamConfig(String initialConfiguration) {
		System.out.println("Aquarium: initial config:" + initialConfiguration);
		final JSONValue initialConfigValue   = JSONParser.parseStrict(initialConfiguration);
	    final JSONObject initialConfigObject = initialConfigValue.isObject();
	    if(initialConfigObject == null) {
	    	Window.alert("Error parsing aquarium configuration: not an object: " + initialConfiguration);
	    	return;
	    }
	    
	    configureWebcam(this.webcam1, initialConfigObject, 1);
	    configureWebcam(this.webcam2, initialConfigObject, 2);
	}
	
	private void configureWebcam(WlWebcam webcam, JSONObject initialConfigObject, int number) {
		final JSONValue webcamValue = initialConfigObject.get("webcam" + number);
	    if(webcamValue != null) {
	    	final String urlWebcam = webcamValue.isString().stringValue();
	    	webcam.setUrl(urlWebcam);
	    }
	    
	    final JSONValue mjpegValue = initialConfigObject.get("mjpeg" + number);
	    if(mjpegValue != null) {
	    	final String mjpeg = mjpegValue.isString().stringValue();
	    	int width = 320;
	    	int height = 240;
	    	if(initialConfigObject.get("mjpegWidth" + number) != null) {
	    		final JSONValue mjpegWidth = initialConfigObject.get("mjpegWidth" + number);
	    		if(mjpegWidth.isNumber() != null) {
	    			width = (int)mjpegWidth.isNumber().doubleValue();
	    		} else if(mjpegWidth.isString() != null) {
	    			width = Integer.parseInt(mjpegWidth.isString().stringValue());
	    		}
	    	}
	    	if(initialConfigObject.get("mjpegHeight" + number) != null) {
	    		final JSONValue mjpegHeight = initialConfigObject.get("mjpegHeight" + number);
	    		if(mjpegHeight.isNumber() != null) {
	    			height = (int)mjpegHeight.isNumber().doubleValue();
	    		} else if(mjpegHeight.isString() != null) {
	    			height = Integer.parseInt(mjpegHeight.isString().stringValue());
	    		}
	    	}
	    	webcam.setStreamingUrl(mjpeg, width, height);
	    }
	}


	@Override
	public IWlDisposableWidget[] getDisposableWidgets() {
		return new IWlDisposableWidget[]{ this.webcam1, this.webcam2 };
	}


	@Override
	public Widget asGwtWidget() {
		return this;
	}
}
