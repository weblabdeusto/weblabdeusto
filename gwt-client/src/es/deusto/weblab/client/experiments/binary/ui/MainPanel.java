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

package es.deusto.weblab.client.experiments.binary.ui;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.Timer;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.Widget;

import es.deusto.weblab.client.comm.exceptions.CommException;
import es.deusto.weblab.client.dto.experiments.ResponseCommand;
import es.deusto.weblab.client.i18n.IWebLabI18N;
import es.deusto.weblab.client.lab.comm.callbacks.IResponseCommandCallback;
import es.deusto.weblab.client.lab.experiments.IBoardBaseController;
import es.deusto.weblab.client.ui.widgets.WlTimer;
import es.deusto.weblab.client.ui.widgets.WlWebcam;

@SuppressWarnings("unqualified-field-access")
class MainPanel extends Composite {
	
	private static final int IS_READY_QUERY_TIMER = 1000;
	private static final String STATE_NOT_READY = "not_ready";
	private static final String STATE_PROGRAMMING = "programming";
	private static final String STATE_READY = "ready";
	private static final String STATE_FAILED = "failed";
	
	// GWT UiBinder stuff
	interface MainPanelUiBinder extends UiBinder<Widget, MainPanel> { }
	private static MainPanelUiBinder uiBinder = GWT.create(MainPanelUiBinder.class);
	private static IWebLabI18N i18n = GWT.create(IWebLabI18N.class);
	
	// Mapped fields
	@UiField WlWebcam camera;
	@UiField WlTimer timer;
	@UiField Label messages;
	
	@UiField HorizontalPanel contentPanel;
	
	// Local fields
	private final IBoardBaseController controller;
	private final String [] labels;
	private final Button [] buttons;
	private Timer readyTimer;
	
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
		this.messages.setText(i18n.selectACode());
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
							loadTimer(label);
						}
						
						@Override
						public void onFailure(CommException e) {
							e.printStackTrace();
							onDeviceProgrammingFailed(": " + e.getMessage(), label);
						}
					});
				}
			});
			this.buttons[i] = b;
			this.contentPanel.add(b);
		}
	}
	
	void onDeviceReady(String label) {
		enableButtons();
		loadInteractivePanel(label);
	}
	
	void onDeviceProgrammingFailed(String errorMessage, String label) {
		Window.alert("Command " + label + " failed" + errorMessage);
		enableButtons();
	}
	
	private void loadTimer(final String label) {
		this.readyTimer = new Timer() {
			@Override
			public void run() {
				
				// Send the command and react to the response
				controller.sendCommand("STATE", new IResponseCommandCallback() {
					@Override
					public void onFailure(CommException e) {
						messages.setText("There was an error while trying to find out whether the experiment is ready");
					}
					
					@Override
					public void onSuccess(ResponseCommand responseCommand) {
						
						// Read the full message returned by the exp server and ensure it's not empty
						final String resp = responseCommand.getCommandString();
						if(resp.length() == 0) 
							messages.setText("The STATE query returned an empty result");
						
						// The command follows the format STATE=ready
						// Extract both parts
						final String [] tokens = resp.split("=", 2);
						if(tokens.length != 2 || !tokens[0].equals("STATE")) {
							messages.setText("Unexpected response ot the STATE query: " + resp);
							return;
						}
						
						final String state = tokens[1];
						
						if(state.equals(STATE_NOT_READY)) {
							readyTimer.schedule(IS_READY_QUERY_TIMER);
						} else if(state.equals(STATE_READY)) {
							// Ready
							onDeviceReady(label);
						} else if(state.equals(STATE_PROGRAMMING)) {
							readyTimer.schedule(IS_READY_QUERY_TIMER);
						} else if(state.equals(STATE_FAILED)) {
							onDeviceProgrammingFailed("", label);
						} else {
							messages.setText("Received unexpected response to the STATE query");
						}
					} 
				}); 
			} 
		};
		this.readyTimer.schedule(IS_READY_QUERY_TIMER);
	}
	
	private void disableButtons(String label) {
		this.messages.setText(i18n.loading(label) + "...");
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
