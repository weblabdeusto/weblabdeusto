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
import java.util.Vector;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.json.client.JSONObject;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.CellPanel;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.Grid;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.Widget;

import es.deusto.weblab.client.HistoryProperties;
import es.deusto.weblab.client.ui.widgets.IWlDisposableWidget;
import es.deusto.weblab.client.ui.widgets.WlTimer;

public class MainIncubatorPanel extends Composite {

	private static MainIncubatorPanelUiBinder uiBinder = GWT.create(MainIncubatorPanelUiBinder.class);
	
	interface MainIncubatorPanelUiBinder extends UiBinder<Widget, MainIncubatorPanel> {}

	@UiField Button turnOffAllButton;
	@UiField Button turnOnAllButton;
	@UiField Label temperature;
	@UiField Grid grid;
	@UiField Label messages;
	@UiField WlTimer timer;
	@UiField CellPanel upperPanel;
	
	private IncubatorExperiment experiment;
	
	private HashMap<Integer, EggMiniWidget> eggWidgets = new HashMap<Integer, EggMiniWidget>();
	
	public MainIncubatorPanel() {
		initWidget(uiBinder.createAndBindUi(this));
	}
	
	public MainIncubatorPanel(IncubatorExperiment experiment, Status status, JSONObject configuration, int time) {
		
		final String widget = HistoryProperties.getValue(HistoryProperties.WIDGET, "");
		final boolean widgetMode = !widget.isEmpty() && widget.startsWith("egg");
		
		this.experiment = experiment;
		initWidget(uiBinder.createAndBindUi(this));
		
		this.timer.updateTime(time);
		
		if (widgetMode) {
			
			this.upperPanel.setVisible(false);
			this.grid.resize(1, 1);
			
			int i = 0;
			try{
				i = Integer.parseInt(widget.substring("egg".length())) - 1;
			} catch(Exception e) { }
		
			final EggMiniWidget wid = new EggMiniWidget(experiment, this, "" + (i + 1), configuration);
			this.eggWidgets.put(Integer.valueOf(i), wid);
			this.grid.setWidget(0, 0, wid);
			
		} else {
		
			this.grid.resize(status.getSize() / 3, 3);
			
			for(int i = 0; i < status.getSize(); ++i) {
				final EggMiniWidget wid = new EggMiniWidget(experiment, this, "" + (i + 1), configuration);
				this.eggWidgets.put(Integer.valueOf(i), wid);
				this.grid.setWidget(i / 3, i % 3, wid);
			}
			
			showTemperature(status);
		}
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
			final boolean lightOn = status.isLightOn("" + (i + 1));
			final EggMiniWidget eggWidget = this.eggWidgets.get(Integer.valueOf(i));
			eggWidget.setLight(lightOn);
		}

		showTemperature(status);
	}

	private void showTemperature(Status status) {
		final double celsius = status.getTemperature();
		final double fahrenheit = celsius * 1.8 + 32;
		final String temperatureString = toSmallString(celsius) + "ºC / " + toSmallString(fahrenheit) + "ºF";
		this.temperature.setText(temperatureString);
	}
	
	private String toSmallString(double d) {
		int floor        = (int)Math.floor(d);
		int firstDecimal = ((int)Math.floor(Math.abs(10 * d))) % 10;
		return floor + "." + firstDecimal;
	}

	Collection<IWlDisposableWidget> getDisposableWidgets() {
		final Vector<IWlDisposableWidget> disposableWidgets = new Vector<IWlDisposableWidget>(this.eggWidgets.values());
		return disposableWidgets;
	}
}
