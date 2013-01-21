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
import com.google.gwt.i18n.client.DateTimeFormat;
import com.google.gwt.json.client.JSONArray;
import com.google.gwt.json.client.JSONObject;
import com.google.gwt.json.client.JSONParser;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.Grid;
import com.google.gwt.user.client.ui.Image;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.ScrollPanel;
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
	@UiField ScrollPanel historicPicturesScroll;
	@UiField Grid historicPictures;
	
	private int pos;
	private IncubatorExperiment experiment;
	private Runnable closeRunnable;
	
	public EggHistoryWidget() {
		initWidget(uiBinder.createAndBindUi(this));
	}
	
	public EggHistoryWidget(IncubatorExperiment experiment, int pos, Runnable closeRunnable) {
		
		this.experiment = experiment;
		this.pos = pos;
		this.closeRunnable = closeRunnable;
		
		initWidget(uiBinder.createAndBindUi(this));

		this.picker.setValue(new Date()); // today
	}
	
	@UiHandler("showButton")
	public void onDateShowClicked(@SuppressWarnings("unused") ClickEvent event) {
		final Date selectedDate = this.picker.getValue();
		if(selectedDate == null) {
			showError("A date must be selected");
			return;
		}
		
		final String formatted = DateTimeFormat.getFormat("y/M/d").format(selectedDate);

		this.experiment.getHistoricData(formatted, new IResponseCommandCallback() {
			
			@Override
			public void onFailure(CommException e) {
				EggHistoryWidget.this.historicPicturesScroll.setVisible(true);
				showError("Retrieving historic data failed: " + e.getMessage());
			}
			
			@Override
			public void onSuccess(ResponseCommand responseCommand) {
				final String command = responseCommand.getCommandString();
				if(command.startsWith("error:")) {
					EggHistoryWidget.this.historicPicturesScroll.setVisible(false);
					showError("Retrieving historic data failed: " + command.substring("error:".length()));
				} else {
					System.out.println(command);
					final JSONObject object = JSONParser.parseStrict(command).isObject();
					final JSONArray data = object.get("" + (EggHistoryWidget.this.pos + 1)).isArray();
					if(data.size() == 0) {
						EggHistoryWidget.this.historicPicturesScroll.setVisible(false);
						showError("No picture for " + formatted);
					} else {
						EggHistoryWidget.this.historicPicturesScroll.setVisible(true);
						EggHistoryWidget.this.historicPictures.resize(data.size(), 2);
						for(int i = 0; i < data.size(); ++i) {
							final String value = data.get(i).isString().stringValue();
							EggHistoryWidget.this.historicPictures.setWidget(i, 0, new Label(value));
							final Image img = new Image(value);
							EggHistoryWidget.this.historicPictures.setWidget(i, 1, img);
						}
						showError("");
					}
				}
			}
		});
	}
	
	@UiHandler("closeButton")
	void addCloseHandler(@SuppressWarnings("unused") ClickEvent event) {
		if(this.closeRunnable != null)
			this.closeRunnable.run();
	}

	private void showError(String message) {
		this.messages.setText(message);
	}
}
