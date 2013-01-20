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
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.DialogBox;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.Widget;

import es.deusto.weblab.client.ui.widgets.IWlDisposableWidget;
import es.deusto.weblab.client.ui.widgets.WlSwitch;
import es.deusto.weblab.client.ui.widgets.WlSwitch.SwitchEvent;
import es.deusto.weblab.client.ui.widgets.WlWebcam;

public class EggMiniWidget extends Composite implements IWlDisposableWidget {

	private static EggMiniWidgetUiBinder uiBinder = GWT.create(EggMiniWidgetUiBinder.class);

	interface EggMiniWidgetUiBinder extends UiBinder<Widget, EggMiniWidget> {}
	
	@UiField Label titleLabel;
	@UiField WlWebcam webcam;
	@UiField WlSwitch lightSwitch;
	
	private final IncubatorExperiment experiment;
	private final MainIncubatorPanel parentPanel;
	int pos;

	public EggMiniWidget() {
		this.experiment = null;
		this.parentPanel = null;
		initWidget(uiBinder.createAndBindUi(this));
	}
	
	public EggMiniWidget(IncubatorExperiment experiment, MainIncubatorPanel parentPanel, int pos, JSONObject configuration) {
		this.experiment = experiment;
		this.parentPanel = parentPanel;
		initWidget(uiBinder.createAndBindUi(this));
		final String label = "" + (pos + 1);
		this.pos = pos;
		this.titleLabel.setText(label);
		final String webcamUrl = configuration.get("webcam" + (pos + 1)).isString().stringValue();
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
		
		this.experiment.turnLight(this.pos, event.isOn());
	}

	public void setLight(boolean lightOn) {
		if(this.lightSwitch.isSwitched() != lightOn)
			this.lightSwitch.switchWithoutFiring(lightOn);
	}
	
	@UiHandler("more")
	public void onMoreClicked(@SuppressWarnings("unused") ClickEvent event) {
		final DialogBox panel = new DialogBox(false, true);
		panel.setWidget(new EggHistoryWidget(this.experiment, this.pos));
		panel.setPopupPosition(this.parentPanel.getAbsoluteLeft(), this.parentPanel.getAbsoluteTop());
		// TODO
		// panel.setWidth(this.parentPanel.getOffsetWidth() + "px");
		// panel.setHeight(this.parentPanel.getOffsetHeight() + "px");
		panel.show();
	}

	@Override
	public void dispose() {
		this.webcam.stop();
	}	
}
