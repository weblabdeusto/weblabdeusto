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

package es.deusto.weblab.client.experiments.binary.ui;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.Widget;

import es.deusto.weblab.client.comm.exceptions.CommException;
import es.deusto.weblab.client.dto.experiments.ResponseCommand;
import es.deusto.weblab.client.lab.comm.callbacks.IResponseCommandCallback;
import es.deusto.weblab.client.lab.experiments.IBoardBaseController;
import es.deusto.weblab.client.ui.widgets.WlTimer;
import es.deusto.weblab.client.ui.widgets.WlWebcam;

@SuppressWarnings("unqualified-field-access")
class MainPanel extends Composite {
	
	// GWT UiBinder stuff
	interface MainPanelUiBinder extends UiBinder<Widget, MainPanel> { }
	private static MainPanelUiBinder uiBinder = GWT.create(MainPanelUiBinder.class);
	
	// Mapped fields
	@UiField WlWebcam camera;
	@UiField WlTimer timer;
	@UiField Label messages;
	
	@UiField HorizontalPanel contentPanel;
	
	// Local fields
	private final IBoardBaseController controller;
	private final String [] labels;
	private final Button [] buttons;
	
	public MainPanel(IBoardBaseController controller, String [] labels) {
		this.controller = controller;
		initWidget(uiBinder.createAndBindUi(this));
		this.labels = (labels == null)?new String[]{"sample", "content"}:labels;
		this.buttons = new Button[this.labels.length];
		loadButtons();
	}
	
	public WlWebcam getWebcam() {
		return this.camera;
	}
	
	public WlTimer getTimer() {
		return this.timer;
	}
	
	void loadButtons() {
		this.messages.setText("Select a code:");
		this.contentPanel.clear();
		
		for (int i = 0; i < this.labels.length; ++i) {
			final String label = this.labels[i];
			
			final Button b = new Button(label, new ClickHandler() {
				@Override
				public void onClick(ClickEvent event) {
					disableButtons(label);
					
					controller.sendCommand("label:" + label, new IResponseCommandCallback() {

						@Override
						public void onSuccess(ResponseCommand responseCommand) {
							enableButtons();
							loadInteractivePanel(label);
						}
						
						@Override
						public void onFailure(CommException e) {
							e.printStackTrace();
							Window.alert("Command " + label + " failed: " + e.getMessage());
							enableButtons();
						}
					});
				}
			});
			this.buttons[i] = b;
			this.contentPanel.add(b);
		}
	}
	
	private void disableButtons(String label) {
		this.messages.setText("Loading " + label + "...");
		for(Button b : this.buttons)
			b.setEnabled(false);
	}
	
	private void enableButtons() {
		this.messages.setText("");
		for(Button b : this.buttons)
			b.setEnabled(true);
	}
	
	private void loadInteractivePanel(String label) {
		this.contentPanel.clear();
		final InteractivePanel panel = new InteractivePanel(this, this.controller, label);
		this.contentPanel.add(panel);
	}
}
