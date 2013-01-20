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

import java.util.Date;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.json.client.JSONArray;
import com.google.gwt.json.client.JSONObject;
import com.google.gwt.json.client.JSONParser;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.Widget;
import com.google.gwt.user.datepicker.client.DatePicker;

import es.deusto.weblab.client.comm.exceptions.CommException;
import es.deusto.weblab.client.dto.experiments.ResponseCommand;
import es.deusto.weblab.client.lab.comm.callbacks.IResponseCommandCallback;

public class EggHistoryWidget extends Composite {

	private static EggHistoryWidgetUiBinder uiBinder = GWT
			.create(EggHistoryWidgetUiBinder.class);

	interface EggHistoryWidgetUiBinder
			extends
				UiBinder<Widget, EggHistoryWidget> {
	}
	
	@UiField DatePicker picker;
	@UiField Label messages;
	
	private int pos;
	private IncubatorExperiment experiment;
	
	public EggHistoryWidget() {
		initWidget(uiBinder.createAndBindUi(this));
	}
	
	public EggHistoryWidget(IncubatorExperiment experiment, int pos) {
		
		this.experiment = experiment;
		this.pos = pos;
		
		initWidget(uiBinder.createAndBindUi(this));

		this.picker.setValue(new Date()); // today
	}
	
	@SuppressWarnings({"unused", "deprecation"})
	@UiHandler("showButton")
	public void onDateShowClicked(ClickEvent event) {
		final Date selectedDate = this.picker.getValue();
		if(selectedDate == null) {
			showError("A date must be selected");
			return;
		}
		final int year  = selectedDate.getYear() + 1900;
		final int month = selectedDate.getMonth() + 1;
		final int day   = selectedDate.getDay() + 1; // TODO: why this is not fine????
		
		System.out.println(selectedDate);	
		System.out.println(year);
		System.out.println(month);
		System.out.println(day);
		
		this.experiment.getHistoricData("" + year, "" + month, "" + day, new IResponseCommandCallback() {
			
			@Override
			public void onFailure(CommException e) {
				showError("Retrieving historic data failed: " + e.getMessage());
			}
			
			@Override
			public void onSuccess(ResponseCommand responseCommand) {
				final String command = responseCommand.getCommandString();
				if(command.startsWith("error:")) {
					showError("Retrieving historic data failed: " + command.substring("error:".length()));
				} else {
					final JSONObject object = JSONParser.parseStrict(command).isObject();
					final JSONArray data = object.get("" + (EggHistoryWidget.this.pos + 1)).isArray();
					if(data.size() == 0) {
						showError("No picture for " + year + "/" + month +  "/" + day);
					} else {
						// TODO: display data
					}
				}
			}
		});
	}

	private void showError(String message) {
		this.messages.setText(message);
	}
}
