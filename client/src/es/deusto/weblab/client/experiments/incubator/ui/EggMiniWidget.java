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
* Author: FILLME
*
*/

package es.deusto.weblab.client.experiments.incubator.ui;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.json.client.JSONObject;
import com.google.gwt.json.client.JSONValue;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.PopupPanel;
import com.google.gwt.user.client.ui.Widget;

import es.deusto.weblab.client.ui.widgets.IWlDisposableWidget;
import es.deusto.weblab.client.ui.widgets.WlSwitch;
import es.deusto.weblab.client.ui.widgets.WlSwitch.SwitchEvent;
import es.deusto.weblab.client.ui.widgets.WlWebcam;

public class EggMiniWidget extends Composite implements IWlDisposableWidget {

	private static EggMiniWidgetUiBinder uiBinder = GWT.create(EggMiniWidgetUiBinder.class);

	interface EggMiniWidgetUiBinder extends UiBinder<Widget, EggMiniWidget> {}
	
	@UiField Label titleLabel;
	@UiField(provided=true) WlWebcam webcam;
	@UiField WlSwitch lightSwitch;
	
	private PopupPanel dialogPanel;
	private final IncubatorExperiment experiment;
	private final MainIncubatorPanel parentPanel;
	private String label;

	public EggMiniWidget() {
		this.experiment = null;
		this.parentPanel = null;
		this.webcam = GWT.create(WlWebcam.class);
		initWidget(uiBinder.createAndBindUi(this));
	}
	
	public EggMiniWidget(IncubatorExperiment experiment, MainIncubatorPanel parentPanel, String label, JSONObject configuration) {
		this.experiment = experiment;
		this.parentPanel = parentPanel;
		
		this.webcam = GWT.create(WlWebcam.class);
		initWidget(uiBinder.createAndBindUi(this));
		
		configureWebcam(this.webcam, configuration, label);
		
		this.label = label;
		this.titleLabel.setText(this.label);
		final String webcamUrl = configuration.get("webcam" + this.label).isString().stringValue();
		System.out.println(webcamUrl);
		this.webcam.setUrl(webcamUrl);
		this.webcam.start();
	}
	
	public void setValue(boolean value) {
		if(this.lightSwitch.isSwitched() != value)
			this.lightSwitch.switchWithoutFiring(value);
	}
	
	@UiHandler("lightSwitch")
 	public void onLightSwitch(SwitchEvent event) {
		if(this.experiment == null)
			return;
		
		this.experiment.turnLight(this.label, event.isOn());
	}

	public void setLight(boolean lightOn) {
		if(this.lightSwitch.isSwitched() != lightOn)
			this.lightSwitch.switchWithoutFiring(lightOn);
	}
	
	@UiHandler("more")
	public void onMoreClicked(@SuppressWarnings("unused") ClickEvent event) {
		this.dialogPanel = new PopupPanel(false, true);
		this.dialogPanel.setWidget(new EggHistoryWidget(this.experiment, this.label, this.dialogPanel));
		final int absoluteLeft = this.parentPanel.getAbsoluteLeft() + this.parentPanel.getOffsetWidth() / 4;
		final int absoluteTop  =  this.parentPanel.getAbsoluteTop() / 2;
		this.dialogPanel.setPopupPosition(absoluteLeft, absoluteTop);
		this.dialogPanel.setSize((this.parentPanel.getOffsetWidth() / 2) + "px", "100%");
		this.dialogPanel.show();
		this.dialogPanel.center();
	}

	@Override
	public void dispose() {
		if(this.dialogPanel != null)
			this.dialogPanel.hide();
		this.webcam.stop();
	}
	
	private void configureWebcam(WlWebcam webcam, JSONObject initialConfigObject, String number) {
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
}
