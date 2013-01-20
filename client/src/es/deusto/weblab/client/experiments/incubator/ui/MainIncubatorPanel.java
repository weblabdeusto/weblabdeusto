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

import java.util.Collection;
import java.util.HashMap;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.json.client.JSONObject;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.Grid;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.Widget;

public class MainIncubatorPanel extends Composite {

	private static MainIncubatorPanelUiBinder uiBinder = GWT.create(MainIncubatorPanelUiBinder.class);
	
	interface MainIncubatorPanelUiBinder extends UiBinder<Widget, MainIncubatorPanel> {}

	@UiField Button turnOffAllButton;
	@UiField Button turnOnAllButton;
	@UiField Label temperature;
	@UiField Grid grid;
	@UiField Label messages;
	
	private IncubatorExperiment experiment;
	
	private HashMap<Integer, EggMiniWidget> eggWidgets = new HashMap<Integer, EggMiniWidget>();
	
	public MainIncubatorPanel() {
		initWidget(uiBinder.createAndBindUi(this));
	}
	
	public MainIncubatorPanel(IncubatorExperiment experiment, Status status, JSONObject configuration) {
		this.experiment = experiment;
		initWidget(uiBinder.createAndBindUi(this));
		
		this.grid.resize(status.getSize() / 3, 3);
		
		for(int i = 0; i < status.getSize(); ++i) {
			final EggMiniWidget wid = new EggMiniWidget(experiment, this, i, configuration);
			this.eggWidgets.put(Integer.valueOf(i), wid);
			this.grid.setWidget(i / 3, i % 3, wid);
		}
		
		this.temperature.setText(status.getTemperature() + "º");
	}
	
	@SuppressWarnings("unused")
	@UiHandler("turnOffAllButton")
	public void onTurnAllOff(ClickEvent event) {
		if(this.experiment != null) 
			this.experiment.turnAllLights(false);
	}
	
	@SuppressWarnings("unused")
	@UiHandler("turnOnAllButton")
	public void onTurnAllOn(ClickEvent event) {
		if(this.experiment != null) 
			this.experiment.turnAllLights(true);
	}

	void showError(String message) {
		this.messages.setText(message);
	}

	void update(Status status) {
		for(int i = 0; i < status.getSize(); ++i) {
			final boolean lightOn = status.isLightOn(i);
			final EggMiniWidget eggWidget = this.eggWidgets.get(Integer.valueOf(i));
			eggWidget.setLight(lightOn);
		}
		
		this.temperature.setText(status.getTemperature() + "º");
	}

	Collection<EggMiniWidget> getDisposableWidgets() {
		return this.eggWidgets.values();
	}
}
